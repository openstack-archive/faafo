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

import sys

import flask
import flask.ext.restless
import flask.ext.sqlalchemy
from oslo_config import cfg
from oslo_log import log

from openstack_application_tutorial import version

CONF = cfg.CONF

cli_opts = [
    cfg.StrOpt('listen-address',
               default='0.0.0.0',
               help='Listen address.'),
    cfg.IntOpt('bind-port',
               default='5000',
               help='Bind port.'),
    cfg.StrOpt('database-url',
               default='sqlite:////tmp/sqlite.db',
               help='Database connection URL.')
]

CONF.register_cli_opts(cli_opts)

log.register_options(CONF)
log.set_defaults()
log.setup(CONF, 'api', version=version.version_info.version_string())

CONF(args=sys.argv[1:],
     project='api',
     version=version.version_info.version_string())

LOG = log.getLogger(__name__)

app = flask.Flask(__name__)
app.config['DEBUG'] = CONF.debug
app.config['SQLALCHEMY_DATABASE_URI'] = CONF.database_url
db = flask.ext.sqlalchemy.SQLAlchemy(app)


class Fractal(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    checksum = db.Column(db.String(256), unique=True)
    duration = db.Column(db.Float)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    iterations = db.Column(db.Integer, nullable=False)
    xa = db.Column(db.Float, nullable=False)
    xb = db.Column(db.Float, nullable=False)
    ya = db.Column(db.Float, nullable=False)
    yb = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Fractal %s>' % self.uuid


db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)


def main():
    manager.create_api(Fractal, methods=['GET', 'POST', 'DELETE', 'PUT'])
    app.run(host=CONF.listen_address, port=CONF.bind_port)

if __name__ == '__main__':
    main()
