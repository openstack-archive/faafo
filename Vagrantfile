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

BOX = "ubuntu/trusty64"

Vagrant.configure(2) do |config|
  config.vm.box = BOX
  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.vm.synced_folder 'src', '/home/vagrant/src'
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--memory", "2048"]
    vb.customize ["modifyvm", :id, "--cpus", "4"]
  end
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end
  config.vm.define "tutorial", primary: true do |tutorial|
    tutorial.vm.hostname= "tutorial"
    tutorial.vm.provision "ansible" do |ansible|
      ansible.playbook = "ansible/playbook.yaml"
    end
  end
end
