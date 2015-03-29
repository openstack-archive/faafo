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

import flask
import flask.ext.restless
import flask.ext.sqlalchemy

app = flask.Flask('faafo.api')
app.config.from_pyfile('settings.cfg', silent=False)
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']
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
    app.run(host=app.config['LISTEN_ADDRESS'], port=app.config['BIND_PORT'])

if __name__ == '__main__':
    main()
