#!/bin/bash
PACKAGES="python-bluez bluetooth python-pip"
sudo apt-get update
sudo apt-get install $PACKAGES -y
pip install  paho-mqtt
sudo python setup.py install
sudo cp beta.service  /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/beta.service
sudo systemctl daemon-reload
sudo systemctl enable beta.service
sudo service beta start
