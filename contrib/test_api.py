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
import requests

url = 'http://127.0.0.1:5000/api/fractal'
headers = {'Content-Type': 'application/json'}

uuid = '13bf15a8-9f6c-4d59-956f-7d20f7484687'
data = {
    'uuid': uuid,
    'width': 100,
    'height': 100,
    'iterations': 10,
    'xa': 1.0,
    'xb': -1.0,
    'ya': 1.0,
    'yb': -1.0,
}
response = requests.post(url, data=json.dumps(data), headers=headers)
assert response.status_code == 201

response = requests.get(url, headers=headers)
assert response.status_code == 200
print(response.json())

response = requests.get(url + '/' + uuid, headers=headers)
assert response.status_code == 200
print(response.json())

data = {
    'checksum': 'c6fef4ef13a577066c2281b53c82ce2c7e94e',
    'duration': 10.12
}
response = requests.put(url + '/' + uuid, data=json.dumps(data),
                        headers=headers)
assert response.status_code == 200

response = requests.get(url + '/' + uuid, headers=headers)
assert response.status_code == 200
print(response.json())

response = requests.delete(url + '/' + uuid, headers=headers)
assert response.status_code == 204
