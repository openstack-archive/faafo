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

import json
import random
import sys
import time
import uuid

import daemon
import kombu
from kombu.pools import producers
from oslo_config import cfg
from oslo_log import log
import requests

from openstack_application_tutorial import queues
from openstack_application_tutorial import version


CONF = cfg.CONF

cli_opts = [
    cfg.BoolOpt('daemonize',
                default=False,
                help='Run in background.'),
    cfg.StrOpt('amqp-url',
               default='amqp://tutorial:secretsecret@localhost:5672/',
               help='AMQP connection URL'),
    cfg.StrOpt('api-url',
               default='http://localhost:5000',
               help='API connection URL')
]

producer_opts = [
    cfg.BoolOpt("one-shot", default=False,
                help="Generate one set of tasks and exit."),
    cfg.IntOpt("max-height", default=1024,
               help="The maximum height of the generate image."),
    cfg.IntOpt("max-width", default=1024,
               help="The maximum width of the generated image."),
    cfg.FloatOpt("max-xa", default=-4.0,
                 help="The maximum value for the parameter 'xa'."),
    cfg.FloatOpt("max-xb", default=4.0,
                 help="The maximum value for the parameter 'xb'."),
    cfg.FloatOpt("max-ya", default=-3,
                 help="The maximum value for the parameter 'ya'."),
    cfg.FloatOpt("max-yb", default=3,
                 help="The maximum value for the parameter 'yb'."),
    cfg.IntOpt("max-iterations", default=512,
               help="The maximum number of iterations."),
    cfg.IntOpt("min-height", default=256,
               help="The minimum height of the generate image."),
    cfg.IntOpt("min-width", default=256,
               help="The minimum width of the generated image."),
    cfg.FloatOpt("min-xa", default=-1.0,
                 help="The minimum value for the parameter 'xa'."),
    cfg.FloatOpt("min-xb", default=1.0,
                 help="The minimum value for the parameter 'xb'."),
    cfg.FloatOpt("min-ya", default=-0.5,
                 help="The minimum value for the parameter 'ya'."),
    cfg.FloatOpt("min-yb", default=0.5,
                 help="The minimum value for the parameter 'yb'."),
    cfg.IntOpt("min-iterations", default=128,
               help="The minimum number of iterations."),
    cfg.FloatOpt("min-pause", default=1.0,
                 help="The minimum pause in seconds."),
    cfg.FloatOpt("max-pause", default=10.0,
                 help="The maximum pause in seconds."),
    cfg.IntOpt("min-tasks", default=1,
               help="The minimum number of generated tasks."),
    cfg.IntOpt("max-tasks", default=10,
               help="The maximum number of generated tasks.")
]

CONF.register_cli_opts(cli_opts)
CONF.register_cli_opts(producer_opts)

log.register_options(CONF)
log.setup(CONF, 'producer', version=version.version_info.version_string())
log.set_defaults()

CONF(args=sys.argv[1:],
     project='producer',
     version=version.version_info.version_string())

LOG = log.getLogger(__name__)


def generate_task():
    random.seed()

    width = random.randint(CONF.min_width, CONF.max_width)
    height = random.randint(CONF.min_height, CONF.max_height)
    iterations = random.randint(CONF.min_iterations, CONF.max_iterations)
    xa = random.uniform(CONF.min_xa, CONF.max_xa)
    xb = random.uniform(CONF.min_xb, CONF.max_xb)
    ya = random.uniform(CONF.min_ya, CONF.max_ya)
    yb = random.uniform(CONF.min_yb, CONF.max_yb)

    task = {
        'uuid': str(uuid.uuid4()),
        'width': width,
        'height': height,
        'iterations': iterations,
        'xa': xa,
        'xb': xb,
        'ya': ya,
        'yb': yb
    }

    return task


def run(messaging, api_url):
    while True:
        random.seed()
        number = random.randint(CONF.min_tasks, CONF.max_tasks)
        LOG.info("generating %d task(s)" % number)
        for i in xrange(0, number):
            task = generate_task()
            # NOTE(berendt): only necessary when using requests < 2.4.2
            headers = {'Content-type': 'application/json',
                       'Accept': 'text/plain'}
            requests.post("%s/api/fractal" % api_url, json.dumps(task),
                          headers=headers)
            LOG.info("generated task: %s" % task)
            with producers[messaging].acquire(block=True) as producer:
                producer.publish(
                    task,
                    serializer='pickle',
                    exchange=queues.task_exchange,
                    declare=[queues.task_exchange],
                    routing_key='tasks')

        if CONF.one_shot:
            break

        pause = random.uniform(CONF.min_pause, CONF.max_pause)
        LOG.info("sleeping for %f seconds" % pause)
        time.sleep(pause)


def main():
    messaging = kombu.Connection(CONF.amqp_url)

    if CONF.daemonize:
        with daemon.DaemonContext():
            run(messaging, CONF.api_url)
    else:
        try:
            run(messaging, CONF.api_url)
        except Exception as e:
            sys.exit("ERROR: %s" % e)


if __name__ == '__main__':
    main()
