"""Entrypoint for the AWS CDK Minecraft Server Deployer."""

import os

from aws_cdk import App, Environment
from minecraft_server_deployer import ServerStack

AWS_REGION = os.environ["AWS_REGION"]
AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]

from datetime import datetime

print(f"[{datetime.now()}] Running app.py for Account {AWS_ACCOUNT_ID}, Region {AWS_REGION}")

# for development, use account/region from CDK CLI
CDK_ENV = Environment(account=AWS_ACCOUNT_ID, region=AWS_REGION)
APP = App()

ServerStack(APP, "awscdk-minecraft-server", env=CDK_ENV)

APP.synth()
