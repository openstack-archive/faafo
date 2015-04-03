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

import base64
import copy
import hashlib
import json
import os
from PIL import Image
import random
import socket
import tempfile
import time

from kombu.mixins import ConsumerMixin
from oslo_config import cfg
from oslo_log import log
import requests

from faafo import queues

LOG = log.getLogger('faafo.worker')
CONF = cfg.CONF


worker_opts = {
    cfg.StrOpt('endpoint-url',
               default='http://localhost',
               help='API connection URL')
}

CONF.register_opts(worker_opts)


def list_opts():
    """Entry point for oslo-config-generator."""
    return [(None, copy.deepcopy(worker_opts))]


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

    def get_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            self.image.save(fp, "PNG")
            return fp.name

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

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=queues.task_queue,
                         accept=['json'],
                         callbacks=[self.process])]

    def process(self, task, message):
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
        elapsed_time = time.time() - start_time
        LOG.info("task %s processed in %f seconds" %
                 (task['uuid'], elapsed_time))

        filename = juliaset.get_file()
        LOG.debug("saved result of task %s to temporary file %s" %
                  (task['uuid'], filename))
        with open(filename, "rb") as fp:
            size = os.fstat(fp.fileno()).st_size
            image = base64.b64encode(fp.read())
        checksum = hashlib.sha256(open(filename, 'rb').read()).hexdigest()
        os.remove(filename)
        LOG.debug("removed temporary file %s" % filename)

        result = {
            'uuid': task['uuid'],
            'duration': elapsed_time,
            'image': image,
            'checksum': checksum,
            'size': size,
            'generated_by': socket.gethostname()
        }

        # NOTE(berendt): only necessary when using requests < 2.4.2
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}

        requests.put("%s/v1/fractal/%s" %
                     (CONF.endpoint_url, str(task['uuid'])),
                     json.dumps(result), headers=headers)

        message.ack()
        return result
