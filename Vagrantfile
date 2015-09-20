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
    vb.memory = 1024
    vb.cpus = 1
  end
  config.ssh.shell = 'bash -c "BASH_ENV=/etc/profile exec bash"'
  config.cache.scope = :box if Vagrant.has_plugin?('vagrant-cachier')
  config.vm.provision "shell",
    inline: "apt-get update && apt-get upgrade -y"

  config.vm.define "services", primary: true do |node|
    node.vm.hostname= "services"
    node.vm.network :private_network, ip: '10.0.88.10'
    node.vm.provision "shell",
      inline: "/vagrant/contrib/install.sh -i messaging -i database"
    node.vm.network 'forwarded_port', guest: 15_672, host: 15_672
  end

  config.vm.define "api" do |node|
    node.vm.hostname= "api"
    node.vm.network :private_network, ip: '10.0.88.20'
    node.vm.provision "shell",
      inline: "/vagrant/contrib/install.sh -i faafo -r api -d 'mysql://faafo:password@10.0.88.10:3306/faafo' -m 'amqp://guest:guest@10.0.88.10:5672/'"
    node.vm.network 'forwarded_port', guest: 80, host: 1080
  end

  config.vm.define "worker" do |node|
    node.vm.hostname= "worker"
    node.vm.network :private_network, ip: '10.0.88.30'
    node.vm.provision "shell",
      inline: "/vagrant/contrib/install.sh -i faafo -r worker -m 'amqp://guest:guest@10.0.88.10:5672/' -e 'http://10.0.88.20'"
  end

end
