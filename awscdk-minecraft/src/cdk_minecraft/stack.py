"""Boilerplate stack to make sure the CDK is set up correctly."""


from aws_cdk import Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct
from aws_cdk import aws_batch_alpha as batch_alpha
from aws_cdk import aws_ecs as ecs
from aws_cdk import CfnOutput

from cdk_minecraft.deploy_server_batch_job.job_queue import BatchJobQueue
from cdk_minecraft.deploy_server_batch_job.job_definition import make_minecraft_ec2_deployment__batch_job_definition


class MinecraftPaasStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        job_queue: batch_alpha.JobQueue = BatchJobQueue(
            self,
            "CdkDockerBatchEnv",
        ).job_queue

        minecraft_server_deployer_job_definition: batch_alpha.JobDefinition = make_minecraft_ec2_deployment__batch_job_definition(
            scope=self,
            id_prefix="McDeployJobDefinition-",
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




