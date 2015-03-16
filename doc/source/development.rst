Development
===========

Vagrant environment
-------------------

The `Vagrant <https://www.vagrantup.com/>`_ environment and the `Ansible <http://www.ansible.com/home>`_
playbook is used only for local tests and development of the application.

The installation of Vagrant is described at https://docs.vagrantup.com/v2/installation/index.html.

The Vagrant plugin `vagrant-hostmanager <https://github.com/smdahlen/vagrant-hostmanager>`_ is required.

.. code::

    $ vagrant plugin install vagrant-hostmanager

To speedup the provisioning you can install the Vagrant plugin `vagrant-cachier <https://github.com/fgrehm/vagrant-cachier>`_.

.. code::

    $ vagrant plugin install vagrant-cachier

Bootstrap the Vagrant environment.

.. code::

    $ vagrant up

The RabbitMQ server and the MySQL server are running on the machine :code:`service.`

There is a machine for each service of the tutorial application:

* :code:`api` - :code:`vagrant ssh api` - :code:`sh run_api.sh`
* :code:`producer` - :code:`vagrant ssh producer` - :code:`sh run_producer.sh`
* :code:`tracker` - :code:`vagrant ssh tracker` - :code:`sh run_tracker.sh`
* :code:`worker` - :code:`vagrant ssh worker` - :code:`sh run_worker.sh`

RabbitMQ server
~~~~~~~~~~~~~~~

The webinterface of the RabbitMQ server is reachable on TCP port :code:`15672`. The login is
possible with the user :code:`guest` and the password :code:`secretsecret`.

MySQL server
~~~~~~~~~~~~

The password of the user :code:`root` is :code:`secretsecret`. The password of the user :code:`tutorial`
for the database :code:`tutorial` is also :code:`secretsecret`.

Virtual environment
-------------------

Create a new virtual environment, install all required dependencies and
the application itself.

.. code::

    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ python setup.py install

Now open a new screen or tmux session. Aftwards run the api, worker, producer, and
tracker services in the foreground, each service in a separate window.

.. code::

    $ source .venv/bin/activate; faafo-api
    $ source .venv/bin/activate; faafo-worker
    $ source .venv/bin/activate; faafo-tracker
    $ source .venv/bin/activate; faafo-producer
