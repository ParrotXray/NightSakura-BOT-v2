#!/bin/bash
cd /home
apt-get update
apt-get upgrade -y
apt install tzdata
apt install tesseract-ocr -y 
apt install libtesseract-dev -y
apt install ffmpeg -y
ffmpeg
apt install git
git config --global --add safe.directory "*"
apt install python3.10 -y 
apt install python3-pip -y
pip3 install -r requirements.txt
python3 Bot.py