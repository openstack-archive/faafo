# -*- mode: ruby -*-
# vi: set ft=ruby :

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

BOX = 'ubuntu/trusty64'

Vagrant.configure(2) do |config|
  config.vm.box = BOX
  config.vm.provider 'virtualbox' do |vb|
    vb.customize ['modifyvm', :id, '--memory', '1024']
    vb.customize ['modifyvm', :id, '--cpus', '1']
  end
  config.ssh.shell = 'bash -c "BASH_ENV=/etc/profile exec bash"'
  config.cache.scope = :box if Vagrant.has_plugin?('vagrant-cachier')
  config.hostmanager.enabled = true
  config.hostmanager.include_offline = true
  config.vm.define 'service', primary: true do |service|
    service.vm.hostname = 'service'
    service.vm.provision 'ansible' do |ansible|
      ansible.playbook = 'ansible/playbook.yaml'
      ansible.tags = %w(database messaging)
    end
    service.vm.network :private_network, ip: '10.15.15.10'
    service.vm.network 'forwarded_port', guest: 15_672, host: 15_672
  end
  config.vm.define 'worker' do |worker|
    worker.vm.hostname = 'worker'
    worker.vm.network :private_network, ip: '10.15.15.20'
    worker.vm.provision 'ansible' do |ansible|
      ansible.playbook = 'ansible/playbook.yaml'
      ansible.tags = 'worker'
    end
  end
  config.vm.define 'tracker' do |tracker|
    tracker.vm.hostname = 'tracker'
    tracker.vm.network :private_network, ip: '10.15.15.30'
    tracker.vm.provision 'ansible' do |ansible|
      ansible.playbook = 'ansible/playbook.yaml'
      ansible.tags = 'tracker'
    end
  end
  config.vm.define 'producer' do |producer|
    producer.vm.hostname = 'producer'
    producer.vm.network :private_network, ip: '10.15.15.40'
    producer.vm.provision 'ansible' do |ansible|
      ansible.playbook = 'ansible/playbook.yaml'
      ansible.tags = 'producer'
    end
  end
  config.vm.define 'api' do |api|
    api.vm.hostname = 'api'
    api.vm.network :private_network, ip: '10.15.15.50'
    api.vm.provision 'ansible' do |ansible|
      ansible.playbook = 'ansible/playbook.yaml'
      ansible.tags = 'api'
    end
    api.vm.network 'forwarded_port', guest: 5000, host: 5000
  end
  config.vm.define 'webinterface' do |webinterface|
    webinterface.vm.hostname = 'webinterface'
    webinterface.vm.network :private_network, ip: '10.15.15.60'
    webinterface.vm.provision 'ansible' do |ansible|
      ansible.playbook = 'ansible/playbook.yaml'
      ansible.tags = 'webinterface'
    end
    webinterface.vm.network 'forwarded_port', guest: 80, host: 8000
  end
end
