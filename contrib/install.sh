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

    # NOTE(berendt): support for centos/rhel/fedora/opensuse/sles will be added in the future

    source /etc/os-release
    RUN_DEMO=0
    INSTALL_MESSAGING=0
    INSTALL_FAAFO=0
    RUN_WORKER=0
    RUN_API=0
    URL_DATABASE='sqlite:////tmp/sqlite.db'
    URL_MESSAGING='rabbit://guest:guest@localhost:5672/'
    URL_API='http://127.0.0.1'
    while getopts amdi:r: FLAG; do
        case $FLAG in
            i)
                case $OPTARG in
                    messaging)
                        INSTALL_MESSAGING=1
                    ;;
                    faafo)
                        INSTALL_FAAFO=1
                    ;;
                esac
            ;;
            r)
                case $OPTARG in
                    demo)
                        RUN_DEMO=1
                    ;;
                    api)
                        RUN_API=1
                    ;;
                    worker)
                        RUN_WORKER=1
                    ;;
                esac
            ;;
            a)
                URL_API=$OPTARG
            ;;

            m)
                URL_MESSAGING=$OPTARG
            ;;

            d)
                URL_DATABASE=$OPTARG
            ;;

            *)
                echo "error: unknown option $FLAG"
                exit 1
            ;;
        esac
    done

    if [[ $INSTALL_MESSAGING -eq 1 ]]; then
        if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
            sudo apt-get install -y rabbitmq-server
        else
            echo "error: distribution $ID not supported"
            exit 1
        fi
    fi

    if [[ $INSTALL_FAAFO -eq 1 ]]; then
        if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
            sudo apt-get update
            sudo apt-get install -y python-dev python-pip supervisor git zlib1g-dev
        #elif [[ $ID = 'centos' || $ID = 'fedora' || $ID = 'rhel' ]]; then
        #    sudo yum install -y python-devel python-pip
        #elif [[ $ID = 'opensuse' || $ID = 'sles' ]]; then
        #    sudo zypper install -y python-devel python-pip
        else
            echo "error: distribution $ID not supported"
            exit 1
        fi

        git clone https://git.openstack.org/stackforge/faafo
        cd faafo
        sudo pip install -r requirements.txt
        sudo python setup.py install

        sudo sed -i -e "s#transport_url = .*#transport_url = $URL_MESSAGING#" /etc/faafo/faafo.conf
        sudo sed -i -e "s#database_url = .*#database_url = $URL_DATABASE#" /etc/faafo/faafo.conf
        sudo sed -i -e "s#endpoint_url = .*#endpoint_url = $URL_API#" /etc/faafo/faafo.conf
    fi


    if [[ $RUN_API -eq 1 ]]; then
        echo "
[program:faafo_api]
command=$(which faafo-api)
priority=10" | sudo tee -a /etc/supervisor/conf.d/faafo.conf
    fi

    if [[ $RUN_WORKER -eq 1 ]]; then
        echo "
[program:faafo_worker]
command=$(which faafo-worker)
priority=20" | sudo tee -a /etc/supervisor/conf.d/faafo.conf
    fi

    sudo supervisorctl reload

    if [[ $RUN_DEMO -eq 1 && $RUN_API -eq 1 ]]; then
        for i in $(seq 1 10); do
            faafo --endpoint-url $URL_API --debug
            sleep 1
        done
    fi

else
    exit 1
fi
