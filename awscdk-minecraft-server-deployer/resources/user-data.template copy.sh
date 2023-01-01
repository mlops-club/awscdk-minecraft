#!/bin/bash

# TODO: consider using try/catch expressions as shown in this SO answer: https://stackoverflow.com/questions/22009364/is-there-a-try-catch-command-in-bash
# to return a failure cfn-signal or success.

# This script is a templated string. All occurreces of "[dollar sign]<some var name>" will be substituted
# with other values by the CDK code.

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
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose

# initialize docker and docker-swarm daemons
service docker start
docker swarm init

# install aws cli
yum install -y python3
pip3 install awscli --upgrade --user

# login to ECR and pull the minecraft server backup/restore image
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin "630013828440.dkr.ecr.us-west-2.amazonaws.com"
docker pull "630013828440.dkr.ecr.us-west-2.amazonaws.com/awscdk-minecraft-mcdeployjobdefinitionminecraftserverbackupserviceimageminecraftbackupserviceecrrepo192beeb7-jwnlifcq2rzf"

# prepare a docker-compose.yml that runs the minecraft server and the backup service
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
            VERSION: "1.19.3"
        volumes:
            - ./minecraft-data:/data
        networks:
        - minecraft-server
        deploy:
            replicas: 1

    # by default, this container will inherit the same IAM role as the EC2 host
    minecraft-backup:
        # aws s3 backup image with awscli and python3
        image: "630013828440.dkr.ecr.us-west-2.amazonaws.com/awscdk-minecraft-mcdeployjobdefinitionminecraftserverbackupserviceimageminecraftbackupserviceecrrepo192beeb7-jwnlifcq2rzf"
        volumes:
            - ./minecraft-data:/minecraft-data
        command: backup-on-interval
        environment:
            BACKUPS_BUCKET: "awscdk-minecraft-minecraftserverbackupsbucketce8b-18lbuip34jg7v"
            SERVER_DATA_DIR: /minecraft-data
            BACKUPS_S3_PREFIX: minecraft-server-backups
            BACKUP_INTERVAL_SECONDS: "600"
        deploy:
            replicas: 1

networks:
    minecraft-server:
        driver: overlay
        name: minecraft-server
EOF

# restore from backup if true is set to "true"
if [ "true" = "true" ]; then
    docker-compose run minecraft-backup restore || echo "Failed to restore from backup. Starting fresh..."
    docker network rm minecraft-server
fi


##########################################
# --- Start up the with docker swarm --- #
##########################################

# create a docker stack
# docker network create minecraft-server
docker stack deploy -c docker-compose.yml minecraft