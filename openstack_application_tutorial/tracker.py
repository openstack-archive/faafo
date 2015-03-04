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
import logging
import sys

import daemon
import kombu
from kombu.mixins import ConsumerMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from openstack_application_tutorial import models
from openstack_application_tutorial import queues


class Tracker(ConsumerMixin):

    def __init__(self, amqp_url, database_url):
        self.connection = kombu.Connection(amqp_url)
        engine = create_engine(database_url)
        models.Base.metadata.bind = engine
        models.Base.metadata.create_all(engine)
        maker = sessionmaker(bind=engine)
        self.session = maker()

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=queues.result_queues,
                         accept=['pickle', 'json'],
                         callbacks=[self.process_result])]

    def process_result(self, body, message):
        logging.info("processing result %s" % body['uuid'])
        logging.info("elapsed time %f seconds" % body['duration'])
        logging.info("checksum %s" % body['checksum'])
        try:
            fractal = self.session.query(models.Fractal).filter(
                models.Fractal.uuid == str(body['uuid'])).one()
            fractal.duration = body['duration']
            fractal.checksum = body['checksum']
            self.session.commit()
        except Exception:
            pass
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
        "--database-url", type=str, help="database connection URL",
        default="mysql://tutorial:secretsecret@localhost:3306/tutorial")
    parser.add_argument(
        "--log-file", type=str, help="write logs to this file", default=None)
    parser.add_argument(
        "--daemonize", action="store_true", help="run in background")
    return parser.parse_args()


def main():
    args = parse_command_line_arguments()
    initialize_logging(args.log_file)
    tracker = Tracker(args.amqp_url, args.database_url)

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
