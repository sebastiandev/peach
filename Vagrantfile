# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 4024
    vb.cpus = 4
  end

  config.vm.define "biyuya-server", primary: true do |machine|
    machine.vm.hostname = "biyuya-server"
    machine.vm.network "private_network", ip: "192.168.50.2"
    machine.vm.network "forwarded_port", guest: 8080, host: 8080
    machine.vm.network "forwarded_port", guest: 3000, host: 3000
    machine.vm.network "forwarded_port", guest: 35729, host: 35729
    machine.vm.provision :shell do |s|
        s.privileged = false
        s.path = "vm/provision"
    end
  end
end
