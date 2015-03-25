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

import json
import sys

import daemon
import kombu
from kombu.mixins import ConsumerMixin
from oslo_config import cfg
from oslo_log import log
import requests

from faafo import queues
from faafo import version


LOG = log.getLogger(__name__)

cli_opts = [
    cfg.BoolOpt('daemonize',
                default=False,
                help='Run in background.'),
    cfg.StrOpt('amqp-url',
               default='amqp://faafo:secretsecret@localhost:5672/',
               help='AMQP connection URL'),
    cfg.StrOpt('api-url',
               default='http://localhost:5000',
               help='API connection URL')
]

cfg.CONF.register_cli_opts(cli_opts)


class Tracker(ConsumerMixin):

    def __init__(self, amqp_url, api_url):
        self.connection = kombu.Connection(amqp_url)
        self.api_url = api_url

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=queues.result_queues,
                         accept=['pickle', 'json'],
                         callbacks=[self.process_result])]

    def process_result(self, body, message):
        LOG.info("processing result %s" % body['uuid'])
        LOG.info("elapsed time %f seconds" % body['duration'])
        LOG.info("checksum %s" % body['checksum'])
        result = {
            'duration': float(body['duration']),
            'checksum': str(body['checksum'])
        }
        # NOTE(berendt): only necessary when using requests < 2.4.2
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}
        requests.put("%s/api/fractal/%s" %
                     (self.api_url, str(body['uuid'])),
                     json.dumps(result), headers=headers)
        message.ack()


def main():
    log.register_options(cfg.CONF)
    log.set_defaults()

    cfg.CONF(project='tracker', prog='faafo-tracker',
             version=version.version_info.version_string())

    log.setup(cfg.CONF, 'tracker',
              version=version.version_info.version_string())

    tracker = Tracker(cfg.CONF.amqp_url, cfg.CONF.api_url)

    if cfg.CONF.daemonize:
        with daemon.DaemonContext():
            tracker.run()
    else:
        try:
            tracker.run()
        except Exception as e:
            sys.exit("ERROR: %s" % e)

if __name__ == '__main__':
    main()
