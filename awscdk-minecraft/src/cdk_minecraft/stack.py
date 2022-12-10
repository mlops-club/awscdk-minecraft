"""Boilerplate stack to make sure the CDK is set up correctly."""


# coginto imports, user pool and client
# coginto imports, user pool and client
# imports for lambda functions and API Gateway
from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_batch_alpha as batch_alpha
from aws_cdk import aws_cognito as cognito
from cdk_minecraft.deploy_server_batch_job.job_definition import (
    make_minecraft_ec2_deployment__batch_job_definition,
)
from cdk_minecraft.deploy_server_batch_job.job_queue import BatchJobQueue
from cdk_minecraft.deploy_server_batch_job.state_machine import ProvisionMinecraftServerStateMachine
from cdk_minecraft.lambda_rest_api import MinecraftPaaSRestApi
from constructs import Construct


class MinecraftPaasStack(Stack):
    """Class to create a stack for the Minecraft PaaS.

    Parameters
    ----------
    scope : Construct
        The scope of the stack.
    construct_id : str
        The name of the stack, should be unique per App.
    **kwargs
        Any additional arguments to pass to the Stack constructor.

    Attributes
    ----------
    job_queue : batch.JobQueue
        The job queue.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        job_queue: batch_alpha.JobQueue = BatchJobQueue(
            scope=self,
            construct_id="CdkDockerBatchEnv",
        ).job_queue

        minecraft_server_deployer_job_definition: batch_alpha.JobDefinition = (
            make_minecraft_ec2_deployment__batch_job_definition(
                scope=self,
                id_prefix="McDeployJobDefinition-",
            )
        )

        mc_deployment_state_machine = ProvisionMinecraftServerStateMachine(
            scope=self,
            construct_id=f"{construct_id}ProvisionMcStateMachine",
            job_queue_arn=job_queue.job_queue_arn,
            deploy_or_destroy_mc_server_job_definition_arn=minecraft_server_deployer_job_definition.job_definition_arn,
        )

        mc_rest_api = MinecraftPaaSRestApi(
            scope=self,
            construct_id="MinecraftPaaSRestAPI",
            provision_server_state_machine_arn=mc_deployment_state_machine.state_machine.state_machine_arn,
        )
        # add role to lambda to allow it to start the state machine
        mc_deployment_state_machine.state_machine.grant_start_execution(mc_rest_api.role)

        CfnOutput(
            scope=self,
            id="MinecraftDeployerJobDefinitionArn",
            value=minecraft_server_deployer_job_definition.job_definition_arn,
        )
        CfnOutput(
            scope=self,
            id="MinecraftDeployerJobDefinitionName",
            value=minecraft_server_deployer_job_definition.job_definition_name,
        )
        CfnOutput(
            scope=self,
            id="MinecraftDeployerJobQueueArn",
            value=job_queue.job_queue_arn,
        )
        CfnOutput(
            scope=self,
            id="MinecraftDeployerJobQueueName",
            value=job_queue.job_queue_name,
        )
        CfnOutput(
            scope=self,
            id="StateMachineArn",
            value=mc_deployment_state_machine.state_machine.state_machine_arn,
        )

        # add an API Gateway endpoint to interact with the lambda function
        # and add an authorizer to the API Gateway
        # cognito_service = MinecraftCognitoConstruct(scope=self, construct_id="MinecraftCognitoService")
        # authorizer = apigw.CognitoUserPoolsAuthorizer(
        #     scope=self,
        #     id="CognitoAuthorizer",
        #     cognito_user_pools=[cognito_service.user_pool],
        # )

        # pass the endpoint of the state machine to the lambda

        # create a cognito service with user pool and plug that into the APIGateway
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/UserPool.html
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/Authorizer.html


class MinecraftCognitoConstruct(Construct):
    """Class to create authentication for the Minecraft PaaS."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create a user pool, do not allow users to sign up themselves.
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/UserPool.html

        self.user_pool = cognito.UserPool(
            scope=scope,
            id="MinecraftUserPool",
            user_pool_name="MinecraftUserPool",
            self_sign_up_enabled=False,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes={
                "email": {"required": True, "mutable": True},
            },
            custom_attributes={
                "minecraft_username": cognito.StringAttribute(min_len=3, max_len=16, mutable=True)
            },
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_digits=False,
                require_lowercase=False,
                require_uppercase=False,
                require_symbols=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        # add a client to the user pool, handle JWT tokens
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/UserPoolClient.html
        self.client = self.user_pool.add_client(
            "MinecraftUserPoolClient",
            user_pool_client_name="MinecraftUserPoolClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True, admin_user_password=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True, implicit_code_grant=True),
                scopes=[cognito.OAuthScope.EMAIL, cognito.OAuthScope.OPENID],
                callback_urls=["https://localhost:3000"],
                logout_urls=["https://localhost:3000"],
            ),
            id_token_validity=Duration.days(1),
            access_token_validity=Duration.days(1),
            refresh_token_validity=Duration.days(1),
            prevent_user_existence_errors=True,
        )
        self.client.apply_removal_policy(RemovalPolicy.DESTROY)

        # add a domain to the user pool
        self.domain = self.user_pool.add_domain(
            id="MinecraftUserPoolDomain",
            cognito_domain=cognito.CognitoDomainOptions(domain_prefix="minecraft-user-pool"),
        )

        # add a CfnOutput to get the user pool domain
        CfnOutput(
            scope=scope,
            id="MinecraftUserPoolDomain",
            value=self.domain.domain_name,
        )
