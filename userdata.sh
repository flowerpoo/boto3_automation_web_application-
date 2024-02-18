#!/bin/bash
sudo apt update 
sudo apt-get install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
sudo apt install awscli -y
sudo rm -rf /var/www/html/*
sudo aws s3 cp s3://first-bucket-poo-web/index.html /var/www/html/index.html
sudo systemctl restart nginx