import os

from aws_cdk import App, Environment
from minecraft_server_deployer.server_stack import ServerStack

# for development, use account/region from cdk cli
CDK_ENV = Environment(account=os.environ["AWS_ACCOUNT_ID"], region=os.getenv("AWS_REGION"))
APP = App()

ServerStack(APP, "awscdk-minecraft-server", env=CDK_ENV)

APP.synth()
