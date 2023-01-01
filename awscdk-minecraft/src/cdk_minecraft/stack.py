"""Boilerplate stack to make sure the CDK is set up correctly."""


from typing import List

import aws_cdk as cdk

# coginto imports, user pool and client
# coginto imports, user pool and client
# imports for lambda functions and API Gateway
from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_batch_alpha as batch_alpha
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_prototyping_sdk.static_website import StaticWebsite
from cdk_minecraft.backend_api import MinecraftPaaSRestApi
from cdk_minecraft.deploy_server_batch_job.deprovision_state_machine import (
    DeprovisionMinecraftServerStateMachine,
)
from cdk_minecraft.deploy_server_batch_job.job_definition import (
    make_minecraft_ec2_deployment__batch_job_definition,
)
from cdk_minecraft.deploy_server_batch_job.job_queue import BatchJobQueue
from cdk_minecraft.deploy_server_batch_job.provision_state_machine import ProvisionMinecraftServerStateMachine
from cdk_minecraft.frontend import (
    create_config_json_file_in_static_site_s3_bucket,
    make_minecraft_platform_frontend_static_website,
)
from constructs import Construct


class MinecraftPaasStack(Stack):
    """Class to create a stack for the Minecraft PaaS.

    :param scope: The scope of the stack
    :param construct_id: The ID of the stack
    :param **kwargs: Additional arguments to pass to the stack

    :ivar job_queue: The job queue for the batch jobs
    :ivar minecraft_server_deployer_job_definition: The job definition for the batch jobs
    :ivar mc_deployment_state_machine: The state machine to deploy a Minecraft server
    :ivar mc_destruction_state_machine: The state machine to destroy a Minecraft server
    :ivar frontend_static_site: The static website for the frontend
    :ivar frontend_url: The URL of the frontend
    :ivar cognito_service: The Cognito service for the frontend
    :ivar mc_rest_api: The REST API for the Minecraft PaaS
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """Backups"""
        backups_bucket = s3.Bucket(
            scope=self,
            id="MinecraftServerBackupsBucket",
            # TODO: make this RETAIN later
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        """State machines"""
        job_queue: batch_alpha.JobQueue = BatchJobQueue(
            scope=self,
            construct_id="CdkDockerBatchEnv",
        ).job_queue

        minecraft_server_deployer_job_definition: batch_alpha.JobDefinition = (
            make_minecraft_ec2_deployment__batch_job_definition(
                scope=self,
                id_prefix="McDeployJobDefinition-",
                backups_bucket_name=backups_bucket.bucket_name,
            )
        )

        mc_deployment_state_machine = ProvisionMinecraftServerStateMachine(
            scope=self,
            construct_id=f"{construct_id}ProvisionMcStateMachine",
            job_queue_arn=job_queue.job_queue_arn,
            deploy_mc_server_job_definition_arn=minecraft_server_deployer_job_definition.job_definition_arn,
        )

        mc_destruction_state_machine = DeprovisionMinecraftServerStateMachine(
            scope=self,
            construct_id=f"{construct_id}DeprovisionMcStateMachine",
            job_queue_arn=job_queue.job_queue_arn,
            destroy_mc_server_job_definition_arn=minecraft_server_deployer_job_definition.job_definition_arn,
        )

        """Frontend"""
        frontend_static_site: StaticWebsite = make_minecraft_platform_frontend_static_website(
            scope=self,
            id_prefix=construct_id,
        )
        frontend_url = f"https://{frontend_static_site.cloud_front_distribution.domain_name}"

        """OAuth identity provider"""
        # add an API Gateway endpoint to interact with the lambda function
        cognito_service = MinecraftCognitoConstruct(
            scope=self, construct_id="MinecraftCognitoService", frontend_url=frontend_url
        )
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            scope=self,
            id="CognitoAuthorizer",
            cognito_user_pools=[cognito_service.user_pool],
        )

        """Backend REST API"""
        # create lambda for the rest API and attach authorizer to API Gateway
        mc_rest_api = MinecraftPaaSRestApi(
            scope=self,
            construct_id="MinecraftPaaSRestAPI",
            provision_server_state_machine_arn=mc_deployment_state_machine.state_machine.state_machine_arn,
            deprovision_server_state_machine_arn=mc_destruction_state_machine.state_machine.state_machine_arn,
            frontend_cors_url=frontend_url,
            authorizer=authorizer,
        )

        # add role to lambda to allow it to start the state machine
        mc_deployment_state_machine.state_machine.grant_start_execution(mc_rest_api.role)
        mc_destruction_state_machine.state_machine.grant_start_execution(mc_rest_api.role)

        # add the states:ListExecutions permission for the deployment state machine to the mc_rest_api role
        grant_list_executions_to_role(
            id_prefix=f"{self.node.id}-deploy-",
            role=mc_rest_api.role,
            state_machine_arn=mc_deployment_state_machine.state_machine.state_machine_arn,
        )
        grant_list_executions_to_role(
            id_prefix=f"{self.node.id}-destroy-",
            role=mc_rest_api.role,
            state_machine_arn=mc_destruction_state_machine.state_machine.state_machine_arn,
        )

        """Frontend Configuration"""
        create_config_json_file_in_static_site_s3_bucket(
            scope=self,
            id_prefix=construct_id,
            backend_url=mc_rest_api.url,
            cognito_app_client_id=cognito_service.client.user_pool_client_id,
            cognito_hosted_ui_app_client_allowed_scopes=cognito_service.allowed_oauth_scopes,
            cognito_user_pool_id=cognito_service.user_pool.user_pool_id,
            static_site_bucket=frontend_static_site.website_bucket,
            static_site_construct=frontend_static_site,
            cognito_user_pool_region=Stack.of(cognito_service.user_pool).region,
            cognito_hosted_ui_redirect_sign_in_url=frontend_url,
            cognito_hosted_ui_redirect_sign_out_url=frontend_url,
            cognito_hosted_ui_fqdn=cognito_service.fully_qualified_domain_name,
        )

        CfnOutput(
            scope=self,
            id="FrontendUrl",
            value=frontend_url,
        )
        CfnOutput(
            scope=self,
            id="FrontendStaticSiteBucketName",
            value=frontend_static_site.website_bucket.bucket_name,
        )
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
            id="DeployStateMachineArn",
            value=mc_deployment_state_machine.state_machine.state_machine_arn,
        )
        CfnOutput(
            scope=self,
            id="DestroyStateMachineArn",
            value=mc_destruction_state_machine.state_machine.state_machine_arn,
        )

        # pass the endpoint of the state machine to the lambda

        # create a cognito service with user pool and plug that into the APIGateway
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/UserPool.html
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/Authorizer.html


def grant_list_executions_to_role(id_prefix: str, role: iam.Role, state_machine_arn: str) -> None:
    """Add the states:ListExecutions permission for the deployment state machine to the mc_rest_api role."""
    role.attach_inline_policy(
        iam.Policy(
            scope=role,
            id=f"{id_prefix}-ListExecutionsPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=["states:List*", "states:Describe*", "states:Get*"],
                    # resources=[f"{state_machine_arn}*"],
                    resources=["*"],
                    effect=iam.Effect.ALLOW,
                ),
            ],
        )
    )


class MinecraftCognitoConstruct(Construct):
    """Class to create authentication for the Minecraft PaaS."""

    def __init__(self, scope: Construct, construct_id: str, frontend_url: str) -> None:
        super().__init__(scope, construct_id)

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
        )

        # add a client to the user pool, handle JWT tokens
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/UserPoolClient.html
        allowed_oauth_scopes = [
            cognito.OAuthScope.EMAIL,
            cognito.OAuthScope.OPENID,
            cognito.OAuthScope.PROFILE,
            cognito.OAuthScope.COGNITO_ADMIN,
        ]
        self.client = self.user_pool.add_client(
            "MinecraftUserPoolClient",
            user_pool_client_name="MinecraftUserPoolClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True, admin_user_password=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True, implicit_code_grant=True),
                scopes=allowed_oauth_scopes,
                callback_urls=["http://localhost:3000", frontend_url],
                logout_urls=["http://localhost:3000", frontend_url],
            ),
            id_token_validity=Duration.days(1),
            access_token_validity=Duration.days(1),
            refresh_token_validity=Duration.days(1),
            prevent_user_existence_errors=True,
        )

        self.allowed_oauth_scopes: List[str] = [scope.scope_name for scope in allowed_oauth_scopes]

        read_scope = cognito.ResourceServerScope(
            scope_name="minecraft.read", scope_description="minecraft read scope"
        )
        resource_server = cognito.UserPoolResourceServer(
            scope=self,
            id="minecraft-resource-server",
            identifier="minecraft-api-resource-server",
            user_pool=self.user_pool,
            scopes=[read_scope],
        )

        client_read_scope = cognito.OAuthScope.resource_server(resource_server, read_scope)

        self.client_credentials = self.user_pool.add_client(
            "MinecraftClientCredentialsClient",
            user_pool_client_name="MinecraftClientCredentialsClient",
            generate_secret=True,
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True, admin_user_password=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(client_credentials=True),
                scopes=[client_read_scope],
                callback_urls=["https://localhost:3000", frontend_url],
                logout_urls=["https://localhost:3000", frontend_url],
            ),
            id_token_validity=Duration.days(1),
            access_token_validity=Duration.days(1),
            refresh_token_validity=Duration.days(1),
            prevent_user_existence_errors=True,
        )

        # add a domain to the user pool
        self.domain = self.user_pool.add_domain(
            id="MinecraftUserPoolDomain",
            cognito_domain=cognito.CognitoDomainOptions(domain_prefix="minecraft-user-pool"),
        )

        self.fully_qualified_domain_name = f"{self.domain.domain_name}.auth.{scope.region}.amazoncognito.com"

        # add a CfnOutput to get the user pool domain
        CfnOutput(
            scope=scope,
            id="MinecraftUserPoolDomain",
            value=self.domain.domain_name,
        )
