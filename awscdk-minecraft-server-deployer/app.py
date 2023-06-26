"""Entrypoint for the AWS CDK Minecraft Server Deployer."""

import os
from datetime import datetime

from aws_cdk import App, Environment
from minecraft_server_deployer import ServerStack

AWS_REGION = os.environ["AWS_REGION"]
AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]

MINECRAFT_SERVER_VERSION = os.environ.get("MINECRAFT_SERVER_VERSION", "1.19.3")
BACKUP_SERVICE_ECR_REPO_ARN = os.environ["BACKUP_SERVICE_ECR_REPO_ARN"]
BACKUP_SERVICE_DOCKER_IMAGE_URI = os.environ["BACKUP_SERVICE_DOCKER_IMAGE_URI"]
MINECRAFT_SERVER_BACKUPS_BUCKET_NAME = os.environ["MINECRAFT_SERVER_BACKUPS_BUCKET_NAME"]
SSH_KEY_PAIR_NAME = os.environ.get("SSH_KEY_PAIR_NAME", None)
CUSTOM_TOP_LEVEL_DOMAIN_NAME = os.environ.get("CUSTOM_TOP_LEVEL_DOMAIN_NAME", None)
EC2_INSTANCE_TYPE = os.environ.get("EC2_INSTANCE_TYPE", None)

print(f"[{datetime.now()}] Running app.py for Account {AWS_ACCOUNT_ID}, Region {AWS_REGION}")

# for development, use account/region from CDK CLI
CDK_ENV = Environment(account=AWS_ACCOUNT_ID, region=AWS_REGION)
APP = App()

ServerStack(
    APP,
    "awscdk-minecraft-server",
    minecraft_server_version=MINECRAFT_SERVER_VERSION,
    backup_service_ecr_repo_arn=BACKUP_SERVICE_ECR_REPO_ARN,
    backup_service_docker_image_uri=BACKUP_SERVICE_DOCKER_IMAGE_URI,
    minecraft_server_backups_bucket_name=MINECRAFT_SERVER_BACKUPS_BUCKET_NAME,
    ssh_key_pair_name=SSH_KEY_PAIR_NAME,
    custom_top_level_domain_name=CUSTOM_TOP_LEVEL_DOMAIN_NAME,
    ec2_instance_type=EC2_INSTANCE_TYPE,
    env=CDK_ENV,
)

APP.synth()
