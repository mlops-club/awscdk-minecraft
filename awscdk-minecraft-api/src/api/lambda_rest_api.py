"""Stack defining an API Gateway mapping to a Lambda function with the FastAPI app."""

from enum import Enum
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_apigateway as api_gateway
from aws_cdk import aws_certificatemanager as certificatemanager
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_s3 as s3
from constructs import Construct


class LambdaRestApiStack(cdk.Stack):
    """An API Gateway mapping to a Lambda function with the backend code inside."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        #: lambda function containing the minecraft FastAPI application code
        self.fast_api_function: lambda_.Function = self.make_fast_api_function()

    def make_fast_api_function(self) -> lambda_.Function:
        fast_api_function = lambda_.Function(
            self,
            "Rootski-FastAPI-Lambda",
            timeout=cdk.Duration.seconds(30),
            memory_size=512,
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=lambda_.Code.from_asset(
                path=str(ROOTSKI_LAMBDA_CODE_DIR),
                bundling=cdk.BundlingOptions(
                    # learn about this here:
                    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/README.html#bundling-asset-code
                    # Using this lambci image makes it so that dependencies with C-binaries compile correctly for the lambda runtime.
                    # The AWS CDK python images were not doing this. Relevant dependencies are: pandas, asyncpg, and psycogp2-binary.
                    image=cdk.DockerImage.from_registry(
                        image="lambci/lambda:build-python3.8"),
                    command=[
                        "bash",
                        "-c",
                        "mkdir -p /asset-output"
                        + "&& pip install -r ./aws-lambda/requirements.txt -t /asset-output"
                        + "&& pip install . -t /asset-output"
                        # TODO: Check that this works
                        + "&& cp -r ./src/rootski/resources /asset-output/rootski/resources/"
                        + "&& cp aws-lambda/index.py /asset-output"
                        + "&& rm -rf /asset-output/boto3 /asset-output/botocore",
                    ],
                ),
            ),
            environment={
                "ROOTSKI__FETCH_VALUES_FROM_AWS_SSM": "true",
                "ROOTSKI__ENVIRONMENT": "prod",
                # /tmp is the only writable location in the lambda file system
                "ROOTSKI__STATIC_ASSETS_DIR": "/tmp",
                "ROOTSKI__OBJECT_CACHE_BUCKET_NAME": morphemes_json_bucket.bucket_name,
            },
        )

        return fast_api_function
