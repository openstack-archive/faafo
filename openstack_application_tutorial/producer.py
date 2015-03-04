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

import argparse
import json
import logging
import random
import sys
import time
import uuid

import daemon
import kombu
from kombu.pools import producers
import requests

from openstack_application_tutorial import queues


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
    parser.add_argument("--one-shot", action='store_true',
                        help="Generate one set of tasks and exit.")
    parser.add_argument("--max-height", type=int, default=1024,
                        help="The maximum height of the generate image.")
    parser.add_argument("--max-width", type=int, default=1024,
                        help="The maximum width of the generated image.")
    parser.add_argument("--max-xa", type=float, default=-4.0,
                        help="The maximum value for the parameter 'xa'.")
    parser.add_argument("--max-xb", type=float, default=4.0,
                        help="The maximum value for the parameter 'xb'.")
    parser.add_argument("--max-ya", type=float, default=-3,
                        help="The maximum value for the parameter 'ya'.")
    parser.add_argument("--max-yb", type=float, default=3,
                        help="The maximum value for the parameter 'yb'.")
    parser.add_argument("--max-iterations", type=int, default=512,
                        help="The maximum number of iterations.")
    parser.add_argument("--min-height", type=int, default=256,
                        help="The minimum height of the generate image.")
    parser.add_argument("--min-width", type=int, default=256,
                        help="The minimum width of the generated image.")
    parser.add_argument("--min-xa", type=float, default=-1.0,
                        help="The minimum value for the parameter 'xa'.")
    parser.add_argument("--min-xb", type=float, default=1.0,
                        help="The minimum value for the parameter 'xb'.")
    parser.add_argument("--min-ya", type=float, default=-0.5,
                        help="The minimum value for the parameter 'ya'.")
    parser.add_argument("--min-yb", type=float, default=0.5,
                        help="The minimum value for the parameter 'yb'.")
    parser.add_argument("--min-iterations", type=int, default=128,
                        help="The minimum number of iterations.")
    parser.add_argument("--min-pause", type=float, default=1.0,
                        help="The minimum pause in seconds.")
    parser.add_argument("--max-pause", type=float, default=10.0,
                        help="The maximum pause in seconds.")
    parser.add_argument("--min-tasks", type=int, default=1,
                        help="The minimum number of generated tasks.")
    parser.add_argument("--max-tasks", type=int, default=10,
                        help="The maximum number of generated tasks.")
    return parser.parse_args()


def generate_task(args):
    random.seed()

    width = random.randint(args.min_width, args.max_width)
    height = random.randint(args.min_height, args.max_height)
    iterations = random.randint(args.min_iterations, args.max_iterations)
    xa = random.uniform(args.min_xa, args.max_xa)
    xb = random.uniform(args.min_xb, args.max_xb)
    ya = random.uniform(args.min_ya, args.max_ya)
    yb = random.uniform(args.min_yb, args.max_yb)

    task = {
        'uuid': str(uuid.uuid4()),
        'dimension': {
            'width': width,
            'height': height,
        },
        'parameter': {
            'iterations': iterations,
            'xa': xa,
            'xb': xb,
            'ya': ya,
            'yb': yb
        }
    }

    return task


def run(args, messaging, api_url):
    while True:
        random.seed()
        number = random.randint(args.min_tasks, args.max_tasks)
        logging.info("generating %d task(s)" % number)
        for i in xrange(0, number):
            task = generate_task(args)
            # NOTE(berendt): only necessary when using requests < 2.4.2
            headers = {'Content-type': 'application/json',
                       'Accept': 'text/plain'}
            requests.post("%s/v1/fractals" % api_url, json.dumps(task),
                          headers=headers)
            logging.info("generated task: %s" % task)
            with producers[messaging].acquire(block=True) as producer:
                producer.publish(
                    task,
                    serializer='pickle',
                    exchange=queues.task_exchange,
                    declare=[queues.task_exchange],
                    routing_key='tasks')

        if args.one_shot:
            break

        pause = random.uniform(args.min_pause, args.max_pause)
        logging.info("sleeping for %f seconds" % pause)
        time.sleep(pause)


def main():
    args = parse_command_line_arguments()
    initialize_logging(args.log_file)
    messaging = kombu.Connection(args.amqp_url)

    if args.daemonize:
        with daemon.DaemonContext():
            run(args, messaging, args.api_url)
    else:
        try:
            run(args, messaging, args.api_url)
        except KeyboardInterrupt:
            return 0

    return 0

if __name__ == '__main__':
    sys.exit(main())
