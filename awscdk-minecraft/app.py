import os

from aws_cdk import App, Environment
from cdk_minecraft import MinecraftPaasStack

# for development, use account/region from cdk cli
DEV_ENV = Environment(account=os.environ["AWS_ACCOUNT_ID"], region=os.getenv("AWS_REGION"))

APP = App()

MinecraftPaasStack(APP, "awscdk-minecraft", login_page_domain_name_prefix="minecraft-user-pool", env=DEV_ENV)

APP.synth()
