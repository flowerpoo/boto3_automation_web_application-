#!/bin/bash
sudo apt-get update 
sudo apt-get install nginx -y
aws s3 cp s3://first-bucket-poo-web/index.html /tmp/index.html
sudo systemctl start nginx
sudo rm -rf /var/www/html/*
sudo cp /tmp/index.html /var/www/html/index.html
sudo systemctl restart nginx