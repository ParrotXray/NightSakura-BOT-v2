#!/bin/bash
cd /home
apt-get update
apt-get upgrade -y
apt install tzdata
apt install python3.10 -y 
apt install python3-pip -y
pip3 install -r requirements.txt
python3 main.py