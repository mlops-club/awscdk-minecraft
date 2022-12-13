"""Stack defining an API Gateway mapping to a Lambda function with the FastAPI app."""


import aws_cdk as cdk
from aws_cdk import CfnOutput
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from cdk_minecraft.constants import MINECRAFT_PLATFORM_BACKEND_API__DIR
from constructs import Construct

# API_SUBDOMAIN = "api.rootski.io"



class MinecraftPaaSRestApi(Construct):
    """An API Gateway mapping to a Lambda function with the backend code inside."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        provision_server_state_machine_arn: str,
        # authorizer: apigw.CfnAuthorizer,
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
            # default_method_options=apigw.MethodOptions(
            #     authorization_type=apigw.AuthorizationType.COGNITO,
            #     authorizer=authorizer,
            # ),
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
    """
    Create a lambda function with the FastAPI app.

    To prepare the python depencies for the lambda function, this stack
    will essentially run the following command:

    .. code:: bash

        docker run \
            --rm \
            -v "path/to/awscdk-minecraft-api:/assets_input" \
            -v "path/to/cdk.out/asset.<some hash>:/assets_output" \
            lambci/lambda:build-python3.8 \
            /bin/bash -c "... several commands to install the requirements to /assets_output ..."

    The reason for using docker to install the requirements is because the "lambci/lambda:build-pythonX.X" image
    uses the same underlying operating system as is used in the real AWS Lambda runtime. This means that
    python packages that rely on compiled C/C++ binaries will be compiled correctly for the AWS Lambda runtime.
    If we did not do it this way, packages such as pandas, numpy, psycopg2-binary, asyncpg, sqlalchemy, and others
    relying on C/C++ bindings would not work when uploaded to lambda.

    We use the ``lambci/*`` images instead of the images maintained by AWS CDK because the AWS CDK images
    were failing to correctly install C/C++ based python packages. An extra benefit of using ``lambci/*`` over
    the AWS CDK images is that the ``lambci/*`` images are in docker hub so they can be pulled without doing any
    sort of ``docker login`` command before executing this script. The AWS CDK images are stored in public.ecr.aws
    which requires a ``docker login`` command to be run first.
    """
    fast_api_function = lambda_.Function(
        scope,
        id=f"{id_prefix}MinecraftPaaSRestApiLambda",
        timeout=cdk.Duration.seconds(30),
        memory_size=512,
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler="index.handler",
        code=lambda_.Code.from_asset(
            path=str(MINECRAFT_PLATFORM_BACKEND_API__DIR),
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
