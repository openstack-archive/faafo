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

Vagrant.configure(2) do |config|
  config.vm.box = 'ubuntu/trusty64'
  config.vm.provider 'virtualbox' do |vb|
    vb.customize ['modifyvm', :id, '--memory', '1024']
    vb.customize ['modifyvm', :id, '--cpus', '1']
  end

  config.vm.provider 'openstack' do |os|
    os.username = "YOUR USERNAME"
    os.api_key         = "YOUR API KEY"           # e.g. "#{ENV['OS_PASSWORD']}"
    os.flavor          = /m1.tiny/                # Regex or String
    os.image           = /Ubuntu/                 # Regex or String
    os.endpoint        = "KEYSTONE AUTH URL"      # e.g. "#{ENV['OS_AUTH_URL']}/tokens"
    os.keypair_name    = "YOUR KEYPAIR NAME"      # as stored in Nova
    os.ssh_username    = "SSH USERNAME"           # login for the VM
    os.security_groups = ['ssh', 'http']
  end

  config.ssh.shell = 'bash -c "BASH_ENV=/etc/profile exec bash"'
  config.cache.scope = :box if Vagrant.has_plugin?('vagrant-cachier')
  config.vm.hostname = 'faafo'
  config.vm.provision 'ansible' do |ansible|
    ansible.playbook = 'ansible/playbook.yaml'
  end
  config.vm.network 'forwarded_port', guest: 80, host: 8000
  config.vm.network 'forwarded_port', guest: 5000, host: 5000
  config.vm.network 'forwarded_port', guest: 15_672, host: 15_672

  if Vagrant.has_plugin?('vagrant-openstack-plugin')
    config.vm.provider "openstack" do |v, override|
      override.vm.box_url = "https://github.com/cloudbau/vagrant-openstack-plugin/raw/master/dummy.box"
      override.vm.box = "dummy"
    end
  end


end
