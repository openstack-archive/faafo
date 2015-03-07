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

import hashlib
import os
from PIL import Image
import random
import sys
import time

import daemon
import kombu
from kombu.mixins import ConsumerMixin
from kombu.pools import producers
from oslo_config import cfg
from oslo_log import log

from openstack_application_tutorial import queues
from openstack_application_tutorial import version


CONF = cfg.CONF

cli_opts = [
    cfg.BoolOpt('daemonize',
                default=False,
                help='Run in background.'),
    cfg.StrOpt('target',
               default='/tmp',
               help='Target directory for fractal image files.'),
    cfg.StrOpt('amqp-url',
               default='amqp://tutorial:secretsecret@localhost:5672/',
               help='AMQP connection URL')
]

CONF.register_cli_opts(cli_opts)

log.register_options(CONF)
log.setup(CONF, 'worker', version=version.version_info.version_string())
log.set_defaults()

CONF(args=sys.argv[1:],
     project='worker',
     version=version.version_info.version_string())

LOG = log.getLogger(__name__)


class JuliaSet(object):

    def __init__(self, width, height, xa=-2.0, xb=2.0, ya=-1.5, yb=1.5,
                 iterations=255):
        self.xa = xa
        self.xb = xb
        self.ya = ya
        self.yb = yb
        self.iterations = iterations
        self.width = width
        self.height = height
        self.draw()

    def draw(self):
        self.image = Image.new("RGB", (self.width, self.height))
        c, z = self._set_point()
        for y in range(self.height):
            zy = y * (self.yb - self.ya) / (self.height - 1) + self.ya
            for x in range(self.width):
                zx = x * (self.xb - self.xa) / (self.width - 1) + self.xa
                z = zx + zy * 1j
                for i in range(self.iterations):
                    if abs(z) > 2.0:
                        break
                    z = z * z + c
                self.image.putpixel((x, y),
                                    (i % 8 * 32, i % 16 * 16, i % 32 * 8))

    def save(self, filename):
        self.image.save(filename, "PNG")

    def _set_point(self):
        random.seed()
        while True:
            cx = random.random() * (self.xb - self.xa) + self.xa
            cy = random.random() * (self.yb - self.ya) + self.ya
            c = cx + cy * 1j
            z = c
            for i in range(self.iterations):
                if abs(z) > 2.0:
                    break
                z = z * z + c
            if i > 10 and i < 100:
                break

        return (c, z)


class Worker(ConsumerMixin):

    def __init__(self, url, target):
        self.connection = kombu.Connection(url)
        self.target = target

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=queues.task_queues,
                         accept=['pickle', 'json'],
                         callbacks=[self.process_task])]

    def process_task(self, body, message):
        LOG.info("processing task %s" % body['uuid'])
        LOG.debug(body)
        start_time = time.time()
        juliaset = JuliaSet(body['width'],
                            body['height'],
                            body['xa'],
                            body['xb'],
                            body['ya'],
                            body['yb'],
                            body['iterations'])
        filename = os.path.join(self.target, "%s.png" % body['uuid'])
        elapsed_time = time.time() - start_time
        LOG.info("task %s processed in %f seconds" %
                 (body['uuid'], elapsed_time))
        juliaset.save(filename)
        LOG.info("saved result of task %s to file %s" %
                 (body['uuid'], filename))
        checksum = hashlib.sha256(open(filename, 'rb').read()).hexdigest()
        result = {
            'uuid': body['uuid'],
            'duration': elapsed_time,
            'checksum': checksum
        }
        LOG.info("pushed result: %s" % result)
        with producers[self.connection].acquire(block=True) as producer:
            producer.publish(result, serializer='pickle',
                             exchange=queues.result_exchange,
                             declare=[queues.result_exchange],
                             routing_key='results')

        message.ack()


def main():
    worker = Worker(CONF.amqp_url, CONF.target)

    if CONF.daemonize:
        with daemon.DaemonContext():
            worker.run()
    else:
        try:
            worker.run()
        except Exception as e:
            sys.exit("ERROR: %s" % e)


if __name__ == '__main__':
    main()
