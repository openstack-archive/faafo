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
import uuid

from oslo_config import cfg
from oslo_log import log
import oslo_messaging as messaging
import requests

from faafo.openstack.common import periodic_task
from faafo.openstack.common import service
from faafo import version


LOG = log.getLogger('faafo.producer')

cli_opts = [
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
    cfg.IntOpt("min-tasks", default=1,
               help="The minimum number of generated tasks."),
    cfg.IntOpt("max-tasks", default=10,
               help="The maximum number of generated tasks."),
    cfg.IntOpt("interval", default=10, help="Interval in seconds.")
]

cfg.CONF.register_cli_opts(cli_opts)
cfg.CONF.register_cli_opts(producer_opts)


class ProducerService(service.Service, periodic_task.PeriodicTasks):
    def __init__(self):
        super(ProducerService, self).__init__()
        self._periodic_last_run = {}
        transport = messaging.get_transport(cfg.CONF)
        target = messaging.Target(topic='tasks', version='2.0')
        self._client = messaging.RPCClient(transport, target)

        @periodic_task.periodic_task(spacing=cfg.CONF.interval,
                                     run_immediately=True)
        def generate_task(self, ctxt):
            ctxt = {}
            random.seed()
            number = random.randint(cfg.CONF.min_tasks, cfg.CONF.max_tasks)
            LOG.info("generating %d task(s)" % number)
            for i in xrange(0, number):
                task = self.get_random_task()
                # NOTE(berendt): only necessary when using requests < 2.4.2
                headers = {'Content-type': 'application/json',
                           'Accept': 'text/plain'}
                requests.post("%s/api/fractal" % cfg.CONF.api_url,
                              json.dumps(task), headers=headers)
                LOG.info("generated task: %s" % task)
                self._client.call(ctxt, 'create', task=task)

        self.add_periodic_task(generate_task)
        self.tg.add_dynamic_timer(self.periodic_tasks)

    def periodic_tasks(self):
        """Tasks to be run at a periodic interval."""
        return self.run_periodic_tasks(None)

    @staticmethod
    def get_random_task():
        random.seed()

        width = random.randint(cfg.CONF.min_width, cfg.CONF.max_width)
        height = random.randint(cfg.CONF.min_height, cfg.CONF.max_height)
        iterations = random.randint(cfg.CONF.min_iterations,
                                    cfg.CONF.max_iterations)
        xa = random.uniform(cfg.CONF.min_xa, cfg.CONF.max_xa)
        xb = random.uniform(cfg.CONF.min_xb, cfg.CONF.max_xb)
        ya = random.uniform(cfg.CONF.min_ya, cfg.CONF.max_ya)
        yb = random.uniform(cfg.CONF.min_yb, cfg.CONF.max_yb)

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


def main():
    log.register_options(cfg.CONF)
    log.set_defaults()

    cfg.CONF(project='producer', prog='faafo-producer',
             version=version.version_info.version_string())

    log.setup(cfg.CONF, 'producer',
              version=version.version_info.version_string())

    srv = ProducerService()

    if cfg.CONF.one_shot:
        srv.periodic_tasks()
    else:
        launcher = service.launch(srv)
        launcher.wait()

if __name__ == '__main__':
    main()
