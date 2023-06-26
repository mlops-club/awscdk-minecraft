from typing import Optional

import aws_cdk as cdk
from cdk_minecraft.construct_ import MinecraftPaas
from constructs import Construct


class MinecraftPaasStack(cdk.Stack):
    """Class to create a stack for the Minecraft PaaS.

    :param scope: The scope of the stack
    :param construct_id: The ID of the stack
    :param cognito_domain_name: a domain name for the cognito login page e.g. `mlops-club-login` \
        any URL compatible string will do as long as it is globally unique within AWS (no one else has taken it)
    :param minecraft_data_bucket_name: Optionally pass the name to a pre-existing S3 Bucket that \
        the server will load/save the minecraft game data backups to.
    :param ssh_key_pair_name: Optionally pass the name of an existing EC2 SSH keypair to use for the \
        connect to the minecraft EC2 instance whenever it is running. The keypair needs to be created \
        manually in the AWS console or via the AWS CLI in order to be referenced here. WARNING! This stack \
        will not validate that the keypair exists, so not setting it will mysteriously cause the deployments \
        from the Minecraft PaaS web UI to fail.

        ```bash
        # create a new keypair from ~/.ssh/id_rsa.pub
        SSH_KEY_PAIR_NAME=my-keypair
        aws ec2 import-key-pair --key-name $SSH_KEY_PAIR_NAME --public-key-material file://~/.ssh/id_rsa.pub
        ```
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

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        login_page_domain_name_prefix: str,
        minecraft_data_bucket_name: Optional[str] = None,
        ssh_key_pair_name: Optional[str] = None,
        top_level_custom_domain_name: Optional[str] = None,
        minecraft_server_version: Optional[str] = None,
        ec2_instance_type: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.minecraft_paas = MinecraftPaas(
            self,
            construct_id=scope.node.id + "-minecraft-paas",
            login_page_domain_name_prefix=login_page_domain_name_prefix,
            minecraft_data_bucket_name=minecraft_data_bucket_name,
            ssh_key_pair_name=ssh_key_pair_name,
            top_level_custom_domain_name=top_level_custom_domain_name,
            minecraft_server_version=minecraft_server_version,
            ec2_instance_type=ec2_instance_type,
        )
