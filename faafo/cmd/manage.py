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

from oslo_config import cfg
from oslo_log import log

from faafo.db import api as db_api
from faafo import version


def do_db_version():
    print(db_api.db_version(db_api.get_engine()))


def do_db_sync():
    db_api.db_sync(db_api.get_engine(), cfg.CONF.command.version)


def add_command_parsers(subparsers):
    parser = subparsers.add_parser('db_version')
    parser.set_defaults(func=do_db_version)

    parser = subparsers.add_parser('db_sync')
    parser.set_defaults(func=do_db_sync)
    parser.add_argument('version', nargs='?')
    parser.add_argument('current_version', nargs='?')


command_opt = cfg.SubCommandOpt('command',
                                title='Commands',
                                help='Show available commands.',
                                handler=add_command_parsers)


def main():
    log.register_options(cfg.CONF)
    log.set_defaults()

    cfg.CONF.register_cli_opt(command_opt)
    cfg.CONF(project='faafo', prog='faafo-manage',
             version=version.version_info.version_string())

    log.setup(cfg.CONF, 'manage',
              version=version.version_info.version_string())

    cfg.CONF.command.func()
