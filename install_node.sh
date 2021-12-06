#!/bin/bash

wget -q -O node-v10.19.0-linux-x64.tar.gz https://nodejs.org/download/release/v10.19.0/node-v10.19.0-linux-x64.tar.gz
sudo tar -C /usr/local -zxvf node-v10.19.0-linux-x64.tar.gz
rm node-v10.19.0-linux-x64.tar.gz
sudo ln -s -f /usr/local/node-v10.19.0-linux-x64/bin/node /usr/local/bin/node
sudo ln -s -f /usr/local/node-v10.19.0-linux-x64/bin/npm /usr/local/bin/npm
sudo npm install -g vue-cli
sudo ln -s -f /usr/local/node-v10.19.0-linux-x64/bin/vue /usr/local/bin/vue
sudo ln -s -f /usr/local/node-v10.19.0-linux-x64/bin/vue-init /usr/local/bin/vue-init 
sudo ln -s -f /usr/local/node-v10.19.0-linux-x64/bin/vue-list /usr/local/bin/vue-list
npm config set registry https://registry.npm.taobao.org
npm config get registry
