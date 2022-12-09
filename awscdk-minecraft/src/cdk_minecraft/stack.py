"""Boilerplate stack to make sure the CDK is set up correctly."""


from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_batch_alpha as batch_alpha
from cdk_minecraft.deploy_server_batch_job.job_definition import (
    make_minecraft_ec2_deployment__batch_job_definition,
)
from cdk_minecraft.deploy_server_batch_job.job_queue import BatchJobQueue
from cdk_minecraft.deploy_server_batch_job.state_machine import ProvisionMinecraftServerStateMachine
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
            self,
            "CdkDockerBatchEnv",
        ).job_queue

        minecraft_server_deployer_job_definition: batch_alpha.JobDefinition = (
            make_minecraft_ec2_deployment__batch_job_definition(
                scope=self,
                id_prefix="McDeployJobDefinition-",
            )
        )

        mc_deployment_state_machine = ProvisionMinecraftServerStateMachine(
            self,
            construct_id=f"{construct_id}ProvisionMcStateMachine",
            job_queue_arn=job_queue.job_queue_arn,
            deploy_or_destroy_mc_server_job_definition_arn=minecraft_server_deployer_job_definition.job_definition_arn,
        )

        CfnOutput(
            self,
            id="MinecraftDeployerJobDefinitionArn",
            value=minecraft_server_deployer_job_definition.job_definition_arn,
        )
        CfnOutput(
            self,
            id="MinecraftDeployerJobDefinitionName",
            value=minecraft_server_deployer_job_definition.job_definition_name,
        )
        CfnOutput(
            self,
            id="MinecraftDeployerJobQueueArn",
            value=job_queue.job_queue_arn,
        )
        CfnOutput(
            self,
            id="MinecraftDeployerJobQueueName",
            value=job_queue.job_queue_name,
        )
        CfnOutput(
            self,
            id="StateMachineArn",
            value=mc_deployment_state_machine.state_machine.state_machine_arn,
        )
