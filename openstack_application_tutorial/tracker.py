#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# based on http://code.activestate.com/recipes/577120-julia-fractals/

import argparse
import json
import logging
import sys

import daemon
import kombu
from kombu.mixins import ConsumerMixin
import requests

from openstack_application_tutorial import queues


class Tracker(ConsumerMixin):

    def __init__(self, amqp_url, api_url):
        self.connection = kombu.Connection(amqp_url)
        self.api_url = api_url

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=queues.result_queues,
                         accept=['pickle', 'json'],
                         callbacks=[self.process_result])]

    def process_result(self, body, message):
        logging.info("processing result %s" % body['uuid'])
        logging.info("elapsed time %f seconds" % body['duration'])
        logging.info("checksum %s" % body['checksum'])
        result = {
            'duration': float(body['duration']),
            'checksum': str(body['checksum'])
        }
        # NOTE(berendt): only necessary when using requests < 2.4.2
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}
        requests.post("%s/v1/fractals/%s/result" %
                      (self.api_url, str(body['uuid'])),
                      json.dumps(result), headers=headers)
        message.ack()


def initialize_logging(filename):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO,
                        filename=filename)


def parse_command_line_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--amqp-url", type=str, help="AMQP connection URL",
        default="amqp://tutorial:secretsecret@localhost:5672/")
    parser.add_argument(
        "--api-url", type=str, help="API connection URL",
        default="http://localhost:5000")
    parser.add_argument(
        "--log-file", type=str, help="write logs to this file", default=None)
    parser.add_argument(
        "--daemonize", action="store_true", help="run in background")
    return parser.parse_args()


def main():
    args = parse_command_line_arguments()
    initialize_logging(args.log_file)
    tracker = Tracker(args.amqp_url, args.api_url)

    if args.daemonize:
        with daemon.DaemonContext():
            tracker.run()
    else:
        try:
            tracker.run()
        except KeyboardInterrupt:
            return 0

    return 0

if __name__ == '__main__':
    sys.exit(main())
