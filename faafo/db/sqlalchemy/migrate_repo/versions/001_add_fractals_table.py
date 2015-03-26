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

import sqlalchemy


def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    fractal = sqlalchemy.Table(
        'fractal', meta,
        sqlalchemy.Column('uuid', sqlalchemy.String(36), primary_key=True,
                          nullable=False),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime, nullable=False),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime, nullable=True),
        sqlalchemy.Column('checksum', sqlalchemy.String(255), nullable=True,
                          unique=True),
        sqlalchemy.Column('duration', sqlalchemy.Float, nullable=True),
        sqlalchemy.Column('iterations', sqlalchemy.Integer, nullable=False),
        sqlalchemy.Column('width', sqlalchemy.Integer, nullable=False),
        sqlalchemy.Column('height', sqlalchemy.Integer, nullable=False),
        sqlalchemy.Column('xa', sqlalchemy.Float, nullable=False),
        sqlalchemy.Column('xb', sqlalchemy.Float, nullable=False),
        sqlalchemy.Column('ya', sqlalchemy.Float, nullable=False),
        sqlalchemy.Column('yb', sqlalchemy.Float, nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )
    fractal.create()


def downgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    fractal = sqlalchemy.Table('fractal', meta, autoload=True)
    fractal.drop()
