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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class Fractal(Base):
    __tablename__ = 'fractals'

    uuid = Column(String(36), primary_key=True)
    checksum = Column(String(256))
    duration = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    iterations = Column(Integer)
    xa = Column(Float)
    xb = Column(Float)
    ya = Column(Float)
    yb = Column(Float)

    def __repr__(self):
        return "<Fractal(uuid='%s')>" % self.uuid
