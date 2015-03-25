Development
===========

Vagrant environment
-------------------

The `Vagrant <https://www.vagrantup.com/>`_ environment and the `Ansible <http://www.ansible.com/home>`_
playbook is used only for local tests and development of the application.

The installation of Vagrant is described at https://docs.vagrantup.com/v2/installation/index.html.

To speedup the provisioning you can install the Vagrant plugin `vagrant-cachier <https://github.com/fgrehm/vagrant-cachier>`_.

.. code::

    $ vagrant plugin install vagrant-cachier

Bootstrap the Vagrant environment.

.. code::

    $ vagrant up

Now it is possible to login with SSH.

.. code::

    $ vagrant ssh

Open a new screen or tmux session. Aftwards run the api, worker, and producer
services in the foreground, each service in a separate window.

* :code:`sh run_api.sh`
* :code:`sh run_producer.sh`
* :code:`sh run_worker.sh`

RabbitMQ server
~~~~~~~~~~~~~~~

The webinterface of the RabbitMQ server is reachable on TCP port :code:`15672`. The login is
possible with the user :code:`guest` and the password :code:`guest`.

MySQL server
~~~~~~~~~~~~

The password of the user :code:`root` is :code:`secretsecret`. The password of the user :code:`faafo`
for the database :code:`faafo` is also :code:`secretsecret`.

Virtual environment
-------------------

Create a new virtual environment, install all required dependencies and
the application itself.

.. code::

    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ python setup.py install

Open a new screen or tmux session. Aftwards run the api, worker, and producer
services in the foreground, each service in a separate window.

.. code::

    $ source .venv/bin/activate; faafo-api
    $ source .venv/bin/activate; faafo-worker
    $ source .venv/bin/activate; faafo-producer
