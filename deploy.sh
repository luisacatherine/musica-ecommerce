#!/bin/bash

eval "$(ssh-agent =s)" &&
ssh-add -k ~/.ssh/id_rsa &&
cd /home/ubuntu/musica/musica-ecommerce
git pull

source ~/profile
echo "$DOCKERHUB_PASS" | docker login --username $DOCKERHUB_USER --password-stdin
sudo docker stop musica
sudo docker rm musica
sudo docker rmi luisacatherine/musica
sudo docker run -d --name musica -p 5000:5000 luisacatherine/musica:latest