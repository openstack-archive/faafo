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

import base64
import copy
import cStringIO
from pkg_resources import resource_filename

import flask
import flask.ext.restless
import flask.ext.sqlalchemy
from flask_bootstrap import Bootstrap
from kombu import Connection
from kombu.pools import producers
from oslo_config import cfg
from oslo_log import log
from PIL import Image
from sqlalchemy.dialects.mysql import MEDIUMBLOB

from faafo import queues
from faafo import version

LOG = log.getLogger('faafo.api')
CONF = cfg.CONF

api_opts = [
    cfg.StrOpt('listen-address',
               default='0.0.0.0',
               help='Listen address.'),
    cfg.IntOpt('bind-port',
               default='80',
               help='Bind port.'),
    cfg.StrOpt('database-url',
               default='sqlite:////tmp/sqlite.db',
               help='Database connection URL.')
]

CONF.register_opts(api_opts)

log.register_options(CONF)
log.set_defaults()

CONF(project='api', prog='faafo-api',
     default_config_files=['/etc/faafo/faafo.conf'],
     version=version.version_info.version_string())

log.setup(CONF, 'api',
          version=version.version_info.version_string())

template_path = resource_filename(__name__, "templates")
app = flask.Flask('faafo.api', template_folder=template_path)
app.config['DEBUG'] = CONF.debug
app.config['SQLALCHEMY_DATABASE_URI'] = CONF.database_url
db = flask.ext.sqlalchemy.SQLAlchemy(app)
Bootstrap(app)


def list_opts():
    """Entry point for oslo-config-generator."""
    return [(None, copy.deepcopy(api_opts))]


class Fractal(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    checksum = db.Column(db.String(256), unique=True)
    url = db.Column(db.String(256), nullable=True)
    duration = db.Column(db.Float)
    size = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    iterations = db.Column(db.Integer, nullable=False)
    xa = db.Column(db.Float, nullable=False)
    xb = db.Column(db.Float, nullable=False)
    ya = db.Column(db.Float, nullable=False)
    yb = db.Column(db.Float, nullable=False)
    if CONF.database_url.startswith('sqlite'):
        LOG.info('Using sqlite')
        image = db.Column(db.LargeBinary, nullable=True)
    else:
        LOG.info('Using mysql')
        image = db.Column(MEDIUMBLOB, nullable=True)
    generated_by = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return '<Fractal %s>' % self.uuid


db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
connection = Connection(CONF.transport_url)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@app.route('/index/<int:page>', methods=['GET'])
def index(page=1):
    fractals = Fractal.query.filter(
        (Fractal.checksum != None) & (Fractal.size != None)).paginate(  # noqa
            page, 5, error_out=False)
    return flask.render_template('index.html', fractals=fractals)


@app.route('/fractal/<string:fractalid>', methods=['GET'])
def get_fractal(fractalid):
    fractal = Fractal.query.filter_by(uuid=fractalid).first()
    if not fractal:
        response = flask.jsonify({'code': 404,
                                  'message': 'Fracal not found'})
        response.status_code = 404
    else:
        image_data = base64.b64decode(fractal.image)
        image = Image.open(cStringIO.StringIO(image_data))
        output = cStringIO.StringIO()
        image.save(output, "PNG")
        image.seek(0)
        response = flask.make_response(output.getvalue())
        response.content_type = "image/png"

    return response


def generate_fractal(**kwargs):
    with producers[connection].acquire(block=True) as producer:
        producer.publish(kwargs['result'],
                         serializer='json',
                         exchange=queues.task_exchange,
                         declare=[queues.task_exchange],
                         routing_key='normal')


def main():
    manager.create_api(Fractal, methods=['GET', 'POST', 'DELETE', 'PUT'],
                       postprocessors={'POST': [generate_fractal]},
                       exclude_columns=['image'],
                       url_prefix='/v1')
    app.run(host=CONF.listen_address, port=CONF.bind_port)
