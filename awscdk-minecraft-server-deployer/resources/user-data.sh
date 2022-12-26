#!/bin/bash

# print the commands this script runs as they are executed
set -x

export WORKDIR=/minecraft
mkdir -p "$WORKDIR"
cd "$WORKDIR"

#########################################
# --- Install CLI tool dependencies --- #
#########################################

yum update -y
yum install -y docker

# install docker-compose and make the binary executable
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$$(uname -s)-$$(uname -m) -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose

# initialize docker and docker-swarm daemons
service docker start
docker swarm init

# install aws cli
yum install -y python3
pip3 install awscli --upgrade --user

# prepare a docker-compose.yml that runs the
cat << EOF > "$WORKDIR/docker-compose.yml"
version: '3.7'
services:
    minecraft:
        # image docs: https://github.com/itzg/docker-minecraft-server
        image: itzg/minecraft-server
        restart: always
        ports:
            - "25565:25565"
        environment:
            EULA: "TRUE"
            TYPE: "PAPER"
            VERSION: "$MINECRAFT_SERVER_SEMANTIC_VERSION"
        networks:
        - minecraft-server
        deploy:
            replicas: 1

networks:
    minecraft-server:
        driver: overlay
        name: minecraft-server
EOF


##########################################
# --- Start up the with docker swarm --- #
##########################################

# create a docker stack
# docker network create minecraft-server
docker stack deploy -c docker-compose.yml minecraft
