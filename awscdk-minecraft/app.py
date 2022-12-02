import os
from aws_cdk.core import App, Environment

from cdk_minecraft.example_stack import ExampleStack

# for development, use account/region from cdk cli
DEV_ENV = Environment(account=os.environ["AWS_ACCOUNT_ID"], region=os.getenv("AWS_REGION"))

APP = App()

ExampleStack(APP, "awscdk-metaflow-dev", env=DEV_ENV)

APP.synth()


# from aws_cdk import aws_batch_alpha as batch
# from aws_cdk import aws_ec2 as ec2
# from constructs import Construct
# from typing import List, Optional

# from cdk_metaflow.utils import make_namer_fn, TNamerFn


# def make_fargate_compute_environment(
#     scope: Construct,
#     id_prefix: str,
#     vpc_with_metadata_service: ec2.Vpc,
# ) -> batch.ComputeEnvironment:
#     make_id: TNamerFn = make_namer_fn(id_prefix)
#     return batch.ComputeEnvironment(
#         scope,
#         id=make_id("fargate-compute-environment"),
#         service_role=None,
#         compute_resources=batch.ComputeResources(
#             type=batch.ComputeResourceType.FARGATE,
#             vpc=vpc_with_metadata_service,
#             maxv_cpus=8,
#         ),
#     )


# def make_batch_job_queue(
#     scope: Construct,
#     id_prefix: str,
#     compute_environments: List[batch.ComputeEnvironment],
#     priority: Optional[int] = 1
# ) -> batch.JobQueue:
#     make_id: TNamerFn = make_namer_fn(id_prefix)
#     return batch.JobQueue(
#         scope=scope,
#         id=make_id("job-queue"),
#         enabled=True,
#         compute_environments=[
#             batch.JobQueueComputeEnvironment(
#                 compute_environment=comp_env, order=idx + 1
#             )
#             for idx, comp_env in enumerate(compute_environments)
#         ],
#         priority=priority,
#     )