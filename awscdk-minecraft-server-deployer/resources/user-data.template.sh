#!/bin/bash

# TODO: consider using try/catch expressions as shown in this SO answer: https://stackoverflow.com/questions/22009364/is-there-a-try-catch-command-in-bash
# to return a failure cfn-signal or success.

# This script is a templated string. All occurreces of "[dollar sign]<some var name>" will be substituted
# with other values by the CDK code.

# make the logged output of this user-data script available in the EC2 console
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

# print the commands this script runs as they are executed
set -x

export WORKDIR=/minecraft
mkdir -p "$$WORKDIR"
cd "$$WORKDIR"

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

# login to ECR and pull the minecraft server backup/restore image
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
docker pull "$BACKUP_SERVICE_DOCKER_IMAGE_URI"

# prepare a docker-compose.yml that runs the minecraft server and the backup service
cat << EOF > "$$WORKDIR/docker-compose.yml"
version: '3.7'
services:
    minecraft:
        # image docs: https://github.com/itzg/docker-minecraft-server
        image: itzg/minecraft-server
        restart: unless-stopped
        container_name: minecraft
        ports:
            - "25565:25565"
        environment:
            EULA: "TRUE"
            TYPE: "PAPER"
            VERSION: "$MINECRAFT_SERVER_SEMANTIC_VERSION"
        volumes:
            - ./minecraft-data:/data

    # by default, this container will inherit the same IAM role as the EC2 host
    minecraft-backup:
        # aws s3 backup image with awscli and python3
        image: "$BACKUP_SERVICE_DOCKER_IMAGE_URI"
        restart: unless-stopped
        volumes:
            - ./minecraft-data:/minecraft-data
        command: backup-on-interval
        environment:
            BACKUPS_BUCKET: "$MINECRAFT_SERVER_BACKUPS_BUCKET_NAME"
            SERVER_DATA_DIR: /minecraft-data
            BACKUPS_S3_PREFIX: minecraft-server-backups
            BACKUP_INTERVAL_SECONDS: "$BACKUP_INTERVAL_SECONDS"
EOF

# restore from backup if $RESTORE_FROM_MOST_RECENT_BACKUP is set to "true"
if [ "$RESTORE_FROM_MOST_RECENT_BACKUP" = "true" ]; then
    docker-compose run minecraft-backup restore || echo "Failed to restore from backup. Starting fresh..."
fi

##########################################
# --- Start up the with docker swarm --- #
##########################################

# create a docker stack
# docker network create minecraft-server
docker-compose up -d
