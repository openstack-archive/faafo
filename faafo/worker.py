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

import eventlet
eventlet.monkey_patch()

import hashlib
import os
from PIL import Image
import random
import socket
import time

from oslo_config import cfg
from oslo_log import log
import oslo_messaging as messaging

from faafo import version


LOG = log.getLogger('faafo.worker')

worker_opts = [
    cfg.StrOpt('filesystem_store_datadir',
               default='/tmp',
               help='Directory that the filesystem backend store writes '
                    'fractal image files to.'),
]

cfg.CONF.register_opts(worker_opts)


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


class WorkerEndpoint(object):

    def process(self, ctxt, task):
        LOG.info("processing task %s" % task['uuid'])
        LOG.debug(task)
        start_time = time.time()
        juliaset = JuliaSet(task['width'],
                            task['height'],
                            task['xa'],
                            task['xb'],
                            task['ya'],
                            task['yb'],
                            task['iterations'])
        filename = os.path.join(cfg.CONF.filesystem_store_datadir,
                                "%s.png" % task['uuid'])
        elapsed_time = time.time() - start_time
        LOG.info("task %s processed in %f seconds" %
                 (task['uuid'], elapsed_time))
        juliaset.save(filename)
        LOG.info("saved result of task %s to file %s" %
                 (task['uuid'], filename))
        checksum = hashlib.sha256(open(filename, 'rb').read()).hexdigest()
        result = {
            'uuid': task['uuid'],
            'duration': elapsed_time,
            'checksum': checksum
        }
        return result


def main():
    log.register_options(cfg.CONF)
    log.set_defaults()

    cfg.CONF(project='worker', prog='faafo-worker',
             version=version.version_info.version_string())

    log.setup(cfg.CONF, 'worker',
              version=version.version_info.version_string())

    transport = messaging.get_transport(cfg.CONF)
    target = messaging.Target(topic='tasks', server=socket.gethostname())
    endpoints = [
        WorkerEndpoint()
    ]
    server = messaging.get_rpc_server(transport, target, endpoints,
                                      executor='eventlet')
    server.start()
    try:
        server.wait()
    except KeyboardInterrupt:
        LOG.info("Caught keyboard interrupt. Exiting.")


if __name__ == '__main__':
    main()
