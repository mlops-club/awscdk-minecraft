"""Boilerplate stack to make sure the CDK is set up correctly."""
from typing import List, Optional

from aws_cdk import aws_batch_alpha as batch
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class BatchJobQueue(Construct):
    """Class to create a batch job queue.

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

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        default_vpc = lookup_default_vpc(scope=self, id_prefix=self.node.id)

        fargate_compute_environment: batch.ComputeEnvironment = make_fargate_compute_environment(
            scope,
            id_prefix=construct_id,
            vpc=default_vpc,
        )

        self.job_queue = make_batch_job_queue(
            scope=self,
            id_prefix=self.node.id,
            priority=1,
            compute_environments=[fargate_compute_environment],
        )


def lookup_default_vpc(scope: Construct, id_prefix: str) -> ec2.Vpc:
    """Look up the default VPC for the account.

    Parameters
    ----------
    scope : Construct
        The scope of the stack.
    id_prefix : str
        The prefix to use for the ID of the VPC.

    Returns
    -------
    ec2.Vpc
        The default VPC for the account.
    """
    return ec2.Vpc.from_lookup(scope=scope, id=f"{id_prefix}", is_default=True)


def make_fargate_compute_environment(
    scope: Construct, id_prefix: str, vpc: ec2.Vpc
) -> batch.ComputeEnvironment:
    """Create a Fargate compute environment.

    Parameters
    ----------
    scope : Construct
        The scope of the stack.
    id_prefix : str
        The prefix to use for the ID of the compute environment.
    vpc : ec2.Vpc
        The VPC to use for the compute environment.

    Returns
    -------
    batch.ComputeEnvironment
        The compute environment.
    """
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
    """Create a batch job queue.

    Parameters
    ----------
    scope : Construct
        The scope of the stack.
    id_prefix : str
        The prefix to use for the ID of the job queue.
    compute_environments : List[batch.ComputeEnvironment]
        The compute environments to use for the job queue.
    priority : Optional[int], optional
        The priority of the job queue, by default 1

    Returns
    -------
    batch.JobQueue
        The job queue.
    """
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
