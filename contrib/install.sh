#!/bin/bash

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

if [[ -e /etc/os-release ]]; then

    # install faafo from PyPi

    # NOTE(berendt): support for centos/fedora/opensuse/sles will be added in the future

    source /etc/os-release
    if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
        sudo apt-get update
        sudo apt-get install -y python-dev python-pip supervisor
    #elif [[ $ID = 'centos' || $ID = 'fedora' || $ID = 'rhel' ]]; then
    #    sudo yum install -y python-devel python-pip
    #elif [[ $ID = 'opensuse' || $ID = 'sles' ]]; then
    #    sudo zypper install -y python-devel python-pip
    else
        echo "error: distribution $ID not supported"
        exit 1
    fi

    sudo pip install faafo
    
    if [[ $(echo $* | grep messaging) ]]; then
        if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
            sudo apt-get install -y rabbitmq-server
        fi
    fi

    if [[ $(echo $* | grep api ) ]]; then
        echo "
[program:faafo_api]
command=$(which faafo-api)
priority=10" | sudo tee -a /etc/supervisor/conf.d/faafo.conf
    fi

    if [[ $(echo $* | grep worker ) ]]; then
        echo "
[program:faafo_worker]
command=$(which faafo-worker)
priority=20" | sudo tee -a /etc/supervisor/conf.d/faafo.conf
    fi


    sudo supervisorctl reload

else
    exit 1
fi
