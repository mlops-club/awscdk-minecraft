import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_stepfunctions as sfn
from constructs import Construct

# construct


def make_lambda_that_validates_input_of_the_provision_server_state_machine(
    scope: Construct,
) -> lambda_.Function:

    # define the lambda function
    return lambda_.Function(
        scope,
        "ProvisionMcServerInputValidator",
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler="index.handler",
        code=lambda_.Code.from_asset("src/cdk_minecraft/deploy_server_batch_job"),
        timeout=cdk.Duration.seconds(30),
    )
