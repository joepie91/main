#!/bin/bash

apt-get remove -y grub-legacy grub-common
apt-get -f install
apt-get update
