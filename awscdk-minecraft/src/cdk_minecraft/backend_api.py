"""Stack defining an API Gateway mapping to a Lambda function with the FastAPI app."""


from textwrap import dedent

import aws_cdk as cdk
from aws_cdk import CfnOutput
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from cdk_minecraft.constants import MINECRAFT_PLATFORM_BACKEND_API__DIR
from constructs import Construct

REACT_LOCALHOST = "http://localhost:3000"
SERVER_CLOUD_FORMATION_STACK_NAME = "awscdk-minecraft-server"


class MinecraftPaaSRestApi(Construct):
    """An API Gateway mapping to a Lambda function with the backend code inside."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        provision_server_state_machine_arn: str,
        deprovision_server_state_machine_arn: str,
        frontend_cors_url: str,
        authorizer: apigw.CfnAuthorizer = None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        cdk.Stack.of(self)

        #: lambda function containing the minecraft FastAPI application code
        fast_api_function: lambda_.Function = make_fast_api_function(
            scope=self,
            id_prefix=construct_id,
            provision_server_state_machine_arn=provision_server_state_machine_arn,
            deprovision_server_state_machine_arn=deprovision_server_state_machine_arn,
            frontend_cors_url=frontend_cors_url,
        )

        api = apigw.RestApi(self, f"{construct_id}RestApi")
        proxy: apigw.Resource = api.root.add_resource(path_part="{proxy+}")

        proxy.add_method(
            http_method="ANY",
            integration=apigw.LambdaIntegration(
                handler=fast_api_function,
                proxy=True,
            ),
            authorizer=authorizer,
        )

        add_cors_options_method(resource=proxy, frontend_cors_url=frontend_cors_url)

        self.role: iam.Role = fast_api_function.role
        self.url: str = api.url

        CfnOutput(self, "EndpointURL", value=api.url)


def add_cors_options_method(
    resource: apigw.Resource,
    frontend_cors_url: str,
) -> None:
    """Add an OPTIONS method to the resource to allow CORS requests."""
    resource.add_method(
        http_method="OPTIONS",
        integration=make_cors_preflight_mock_integration(frontend_cors_url=frontend_cors_url),
        authorization_type=apigw.AuthorizationType.NONE,
        method_responses=[
            apigw.MethodResponse(
                status_code="200",
                response_parameters={
                    # True means that the method response header will be passed through from the integration response.
                    # Just because the MockIntegration returns values, does not mean those values make it
                    # to the client making the request. Here, we must explicitly declare headers, payload fields,
                    # etc. that we want to pass back to the user.
                    "method.response.header.Access-Control-Allow-Headers": True,
                    "method.response.header.Access-Control-Allow-Methods": True,
                    "method.response.header.Access-Control-Allow-Origin": True,
                    "method.response.header.Content-Type": True,
                },
            )
        ],
    )


def make_cors_preflight_mock_integration(frontend_cors_url: str) -> apigw.MockIntegration:
    """
    Create a MockIntegration that will be used for the OPTIONS method to return correct CORS headers during the preflight request.

    This web app helps you determine what your CORS setup should be for api gateway: https://cors.serverlessland.com/
    """
    mock_integration = apigw.MockIntegration(
        passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
        request_templates={
            "application/json": '{"statusCode": 200}',
        },
        integration_responses=[
            apigw.IntegrationResponse(
                status_code="200",
                # response_parameters contains static values that are returned by the Mock integration
                # at every single request. You can use this to set a response body, but in this case
                # we are only setting headers.
                response_parameters={
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,PUT,POST,DELETE'",
                    "method.response.header.Access-Control-Allow-Origin": f"'{frontend_cors_url}'",
                    "method.response.header.Content-Type": "'application/json'",
                },
                response_templates={
                    # API Gateway only supports specifying a single CORS origin for the Access-Control-Allow-Origin header;
                    # but it's useful for development to include http://localhost:3000 so that we can hit the production
                    # API from our local frontend. We can't do a comma-separated list of origins like "https://<prod url>,http://localhost:3000`",
                    # API gateway only supports one specific origin or '*'--but '*' is not allowed when credentials are passed
                    # with HTTP requests such as we are doing with AWS cognito.
                    #
                    # So, we use this template written with the "Apache Velocity Templating Language"
                    # (similar to Jinja, but has syntax for setting variables). AWS exposes certain variables such as $ whose
                    # values we can use in our template.
                    #
                    # This template transforms the headers/payload that come out of the MockIntegration. In this case,
                    # it transforms the fixed content we hard coded in "response_parameters" ^^^. That way we can
                    # choose which origin to return in the final response.
                    "application/json": dedent(
                        f"""\
                        #set($origin = $input.params("Origin"))
                        #if($origin == "")
                            #set($origin = $input.params("origin"))
                        #end
                        #if($origin == "{REACT_LOCALHOST}" || $origin == "{frontend_cors_url}")
                            #set($context.responseOverride.header.Access-Control-Allow-Origin = $origin)
                        #end
                        """
                    ),
                },
            )
        ],
        content_handling=apigw.ContentHandling.CONVERT_TO_TEXT,
        credentials_passthrough=True,
    )

    return mock_integration


def make_fast_api_function(
    scope: Construct,
    id_prefix: str,
    provision_server_state_machine_arn: str,
    deprovision_server_state_machine_arn: str,
    frontend_cors_url: str,
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
            "DEPLOY_SERVER_STATE_MACHINE_ARN": provision_server_state_machine_arn,
            "DESTROY_SERVER_STATE_MACHINE_ARN": deprovision_server_state_machine_arn,
            "FRONTEND_CORS_URL": frontend_cors_url,
            "ENVIRONMENT": "production",
            # TODO: get these values from variables that are guaranteed to be of the
            # correct values.
            "CLOUD_FORMATION_SERVER_IP_OUTPUT_KEY_NAME": "MinecraftServerIp",
            "CLOUD_FORMATION_STACK_NAME": SERVER_CLOUD_FORMATION_STACK_NAME,
        },
    )

    grant_cloudformation_stack_read_access(
        stack_name=SERVER_CLOUD_FORMATION_STACK_NAME,
        role=fast_api_function.role,
        stack_region=cdk.Stack.of(scope).region,
        stack_account=cdk.Stack.of(scope).account,
    )

    return fast_api_function


def grant_cloudformation_stack_read_access(
    stack_name: str,
    role: iam.Role,
    stack_region: str,
    stack_account: str,
):
    """
    Give the given role permission to read the outputs of the given cloudformation stack.

    This is necessary because the lambda function needs to read the outputs of the cloudformation stack
    in order to know the IP address of the minecraft server.
    """
    role.add_to_policy(
        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["cloudformation:Describe*", "cloudformation:Get*", "cloudformation:List*"],
            resources=[f"arn:aws:cloudformation:{stack_region}:{stack_account}:stack/{stack_name}*"],
        )
    )
