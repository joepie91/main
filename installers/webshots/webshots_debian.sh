#!/bin/bash
apt-get update
apt-get install -y lua50 liblua5.1-0-dev python python-setuptools git-core openssl libssl-dev bzip2 build-essential
if [ $? -ne 0 ]; then echo "[X] Installing dependencies failed. Exiting..."; exit 1; fi

easy_install pip
if [ $? -ne 0 ]; then echo "[X] Installing pip failed. Exiting..."; exit 1; fi

pip install seesaw
if [ $? -ne 0 ]; then echo "[X] Installing seesaw failed. Exiting..."; exit 1; fi

useradd -m archiveteam
if [ $? -ne 0 ]; then echo "[X] Creating archiveteam user failed. Exiting..."; exit 1; fi

wget -O /home/archiveteam/setup.sh http://cryto.net/projects/webshots/setup.sh
if [ $? -ne 0 ]; then echo "[X] Retrieving the user setup script failed. Exiting..."; exit 1; fi

chown archiveteam:archiveteam /home/archiveteam/setup.sh
if [ $? -ne 0 ]; then echo "[X] Chowning the setup script failed. Exiting..."; exit 1; fi

chmod +x /home/archiveteam/setup.sh
if [ $? -ne 0 ]; then echo "[X] Chmodding the setup script failed. Exiting..."; exit 1; fi

su -c "/home/archiveteam/setup.sh" archiveteam
