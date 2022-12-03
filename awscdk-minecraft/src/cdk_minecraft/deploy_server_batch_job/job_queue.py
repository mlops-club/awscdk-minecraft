"""Boilerplate stack to make sure the CDK is set up correctly."""
from typing import List, Optional

from aws_cdk import aws_batch_alpha as batch
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class BatchJobQueue(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        default_vpc = lookup_default_vpc(scope=self, id_prefix=self.node.id)

        fargate_compute_environment: batch.ComputeEnvironment = make_fargate_compute_environment(
            scope,
            id_prefix=construct_id,
            vpc=default_vpc,
        )

        self.job_queue = make_batch_job_queue(
            scope=self, id_prefix=self.node.id, priority=1, compute_environments=[fargate_compute_environment]
        )


def lookup_default_vpc(scope: Construct, id_prefix: str) -> ec2.Vpc:
    return ec2.Vpc.from_lookup(scope=scope, id=f"{id_prefix}", is_default=True)


def make_fargate_compute_environment(
    scope: Construct, id_prefix: str, vpc: ec2.Vpc
) -> batch.ComputeEnvironment:
    return batch.ComputeEnvironment(
        scope,
        id=f"{id_prefix}-fargate-compute-environment",
        service_role=None,
        compute_resources=batch.ComputeResources(
            type=batch.ComputeResourceType.FARGATE,
            vpc=vpc,
            maxv_cpus=8,
        ),
    )


def make_batch_job_queue(
    scope: Construct,
    id_prefix: str,
    compute_environments: List[batch.ComputeEnvironment],
    priority: Optional[int] = 1,
) -> batch.JobQueue:
    return batch.JobQueue(
        scope=scope,
        id=f"{id_prefix}-job-queue",
        enabled=True,
        compute_environments=[
            batch.JobQueueComputeEnvironment(compute_environment=comp_env, order=idx + 1)
            for idx, comp_env in enumerate(compute_environments)
        ],
        priority=priority,
    )
