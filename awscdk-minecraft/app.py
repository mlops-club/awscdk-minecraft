import os
from aws_cdk import App, Environment

from cdk_minecraft.example_stack import ExampleStack

# for development, use account/region from cdk cli
DEV_ENV = Environment(account=os.environ["AWS_ACCOUNT_ID"], region=os.getenv("AWS_REGION"))

APP = App()

ExampleStack(APP, "awscdk-metaflow-dev", env=DEV_ENV)

APP.synth()
