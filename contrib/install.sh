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

    # NOTE(berendt): support for CentOS/RHEL/openSUSE/SLES will be added in the future

    source /etc/os-release

    INSTALL_DATABASE=0
    INSTALL_FAAFO=0
    INSTALL_MESSAGING=0
    RUN_API=0
    RUN_DEMO=0
    RUN_WORKER=0
    URL_DATABASE='sqlite:////tmp/sqlite.db'
    URL_ENDPOINT='http://127.0.0.1'
    URL_MESSAGING='amqp://guest:guest@localhost:5672/'

    while getopts e:m:d:i:r: FLAG; do
        case $FLAG in
            i)
                case $OPTARG in
                    messaging)
                        INSTALL_MESSAGING=1
                    ;;
                    database)
                        INSTALL_DATABASE=1
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
            e)
                URL_ENDPOINT=$OPTARG
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

    if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
        sudo apt-get update
    elif [[ $ID = 'fedora' ]]; then
        sudo dnf update -y
    fi

    if [[ $INSTALL_DATABASE -eq 1 ]]; then
        if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server python-mysqldb
            sudo sed -i -e "/bind-address/d" /etc/mysql/my.cnf
            sudo service mysql restart
        elif [[ $ID = 'fedora' ]]; then
            sudo dnf install -y mariadb-server python-mysql
            printf "[mysqld]\nbind-address = 127.0.0.1\n" | sudo tee /etc/my.cnf.d/faafo.conf
            sudo systemctl enable mariadb
            sudo systemctl start mariadb
        else
            echo "error: distribution $ID not supported"
            exit 1
        fi
        sudo mysqladmin password password
        sudo mysql -uroot -ppassword mysql -e "CREATE DATABASE IF NOT EXISTS faafo; GRANT ALL PRIVILEGES ON faafo.* TO 'faafo'@'%' IDENTIFIED BY 'password';"
        URL_DATABASE='mysql://root:password@localhost/faafo'
    fi

    if [[ $INSTALL_MESSAGING -eq 1 ]]; then
        if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
            sudo apt-get install -y rabbitmq-server
        elif [[ $ID = 'fedora' ]]; then
            sudo dnf install -y rabbitmq-server
            sudo systemctl enable rabbitmq-server
            sudo systemctl start rabbitmq-server
        else
            echo "error: distribution $ID not supported"
            exit 1
        fi
    fi

    if [[ $INSTALL_FAAFO -eq 1 ]]; then
        if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
            sudo apt-get install -y python-dev python-pip supervisor git zlib1g-dev libmysqlclient-dev
        elif [[ $ID = 'fedora' ]]; then
            sudo dnf install -y python-devel python-pip supervisor git zlib-devel mariadb-devel gcc which
            sudo systemctl enable supervisord
            sudo systemctl start supervisord
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
        sudo sed -i -e "s#endpoint_url = .*#endpoint_url = $URL_ENDPOINT#" /etc/faafo/faafo.conf
    fi


    if [[ $RUN_API -eq 1 ]]; then
        faafo_api="
[program:faafo_api]
command=$(which faafo-api)
priority=10"

        if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
            echo "$faafo_api" | sudo tee -a /etc/supervisor/conf.d/faafo.conf
        elif [[ $ID = 'fedora' ]]; then
            echo "$faafo_api" | sudo tee -a /etc/supervisord.d/faafo.ini
        else
            echo "error: distribution $ID not supported"
            exit 1
        fi
    fi

    if [[ $RUN_WORKER -eq 1 ]]; then
        faafo_worker="
[program:faafo_worker]
command=$(which faafo-worker)
priority=20"

        if [[ $ID = 'ubuntu' || $ID = 'debian' ]]; then
            echo "$faafo_worker" | sudo tee -a /etc/supervisor/conf.d/faafo.conf
        elif [[ $ID = 'fedora' ]]; then
            echo "$faafo_worker" | sudo tee -a /etc/supervisord.d/faafo.ini
        else
            echo "error: distribution $ID not supported"
            exit 1
        fi
    fi

    if [[ $RUN_WORKER -eq 1 || $RUN_API -eq 1 ]]; then
        sudo supervisorctl reload
        sleep 5
    fi

    if [[ $RUN_DEMO -eq 1 && $RUN_API -eq 1 ]]; then
        faafo --endpoint-url $URL_ENDPOINT --debug create
    fi

else
    exit 1
fi
