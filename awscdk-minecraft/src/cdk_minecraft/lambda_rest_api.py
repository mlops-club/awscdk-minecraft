"""Stack defining an API Gateway mapping to a Lambda function with the FastAPI app."""

from pathlib import Path

import aws_cdk as cdk
from aws_cdk import CfnOutput
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

# API_SUBDOMAIN = "api.rootski.io"

THIS_DIR = Path(__file__).parent
MINECRAFT_PAAS_BACKEND_API_DIR = THIS_DIR / "../../../awscdk-minecraft-api"


class MinecraftPaaSRestApi(Construct):
    """An API Gateway mapping to a Lambda function with the backend code inside."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        provision_server_state_machine_arn: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        cdk.Stack.of(self)

        #: lambda function containing the minecraft FastAPI application code
        fast_api_function: lambda_.Function = make_fast_api_function(
            scope=self,
            id_prefix=construct_id,
            provision_server_state_machine_arn=provision_server_state_machine_arn,
        )

        self.role: iam.Role = fast_api_function.role

        #: API Gateway that proxies all incoming requests to the fast_api_function
        self.rest_api = apigw.LambdaRestApi(
            scope=self,
            id="Endpoint",
            handler=fast_api_function,
            proxy=True,
        )

        CfnOutput(
            self,
            "EndpointURL",
            value=self.rest_api.url,
        )


def make_fast_api_function(
    scope: Construct,
    id_prefix: str,
    provision_server_state_machine_arn: str,
) -> lambda_.Function:
    fast_api_function = lambda_.Function(
        scope,
        id=f"{id_prefix}MinecraftPaaSRestApiLambda",
        timeout=cdk.Duration.seconds(30),
        memory_size=512,
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler="index.handler",
        code=lambda_.Code.from_asset(
            path=str(MINECRAFT_PAAS_BACKEND_API_DIR),
            bundling=cdk.BundlingOptions(
                # learn about this here:
                # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/README.html#bundling-asset-code
                # Using this lambci image makes it so that dependencies with C-binaries compile correctly for the lambda runtime.
                # The AWS CDK python images were not doing this. Relevant dependencies are: pandas, asyncpg, and psycogp2-binary.
                image=cdk.DockerImage.from_registry(image="lambci/lambda:build-python3.8"),
                command=[
                    "bash",
                    "-c",
                    "mkdir -p /asset-output"
                    # + "&& pip install -r ./aws-lambda/requirements.txt -t /asset-output"
                    + "&& pip install .[lambda] --target /asset-output"
                    + "&& cp ./aws-lambda/index.py /asset-output"
                    # + "&& rm -rf /asset-output/boto3 /asset-output/botocore",
                ],
            ),
        ),
        environment={
            "DEPLOY_SERVER_STEP_FUNCTIONS_STATE_MACHINE_ARN": provision_server_state_machine_arn,
            "ENVIRONMENT": "prod",
        },
    )

    return fast_api_function
