from pathlib import Path

from aws_cdk import aws_batch_alpha as batch_alpha
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from constructs import Construct

THIS_DIR = Path(__file__).parent
DOCKERIZED_AWS_CDK_BUILD_CONTEXT = (THIS_DIR / "../../../resources/awscdk-minecraft-server-deployer").resolve()

# class ExampleStack(Construct):
#     def __init__(
#         self, scope: Construct, construct_id: str, **kwargs
#     ) -> None:
#         super().__init__(scope, construct_id, **kwargs)


def make_minecraft_ec2_deployment__batch_job_definition(
    scope: Construct, id_prefix: str
) -> batch_alpha.JobDefinition:

    execution_role: iam.Role = make_batch_execution_role(scope=scope, id_prefix=id_prefix)
    job_role: iam.Role = make_cdk_deployment_role(scope=scope, id_prefix=id_prefix)

    return batch_alpha.JobDefinition(
        scope=scope,
        id=f"{id_prefix}CdkMinecraftEc2DeploymentJD",
        container=batch_alpha.JobDefinitionContainer(
            image=ecs.ContainerImage.from_asset(
                directory=str(DOCKERIZED_AWS_CDK_BUILD_CONTEXT),
                platform=ecr_assets.Platform.LINUX_AMD64,
            ),
            command=["cdk", "deploy", "--app", "'python3 /app/app.py'"],
            job_role=job_role,
            execution_role=execution_role,
            log_configuration=batch_alpha.LogConfiguration(
                log_driver=batch_alpha.LogDriver.AWSLOGS,
            ),
        ),
        platform_capabilities=[batch_alpha.PlatformCapabilities.FARGATE],
    )


def make_cdk_deployment_role(scope: Construct, id_prefix: str) -> iam.Role:
    """Grant the running batch job sufficient privileges to run CDK commands to provision/destroy resources."""
    return iam.Role(
        scope=scope,
        id=f"{id_prefix}CdkDeployRole",
        assumed_by=iam.ServicePrincipal(service="ecs-tasks.amazonaws.com"),
        managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")],
    )


def make_batch_execution_role(scope: Construct, id_prefix: str) -> iam.Role:
    role = iam.Role(
        scope=scope,
        id=f"{id_prefix}BatchRole",
        assumed_by=iam.ServicePrincipal(service="ecs-tasks.amazonaws.com"),
    )

    role.attach_inline_policy(
        policy=iam.Policy(
            scope=scope,
            id=f"{id_prefix}EcsPolicy",
            document=iam.PolicyDocument.from_json(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "ecr:GetAuthorizationToken",
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Resource": "*",
                        }
                    ],
                }
            ),
        )
    )

    return role
