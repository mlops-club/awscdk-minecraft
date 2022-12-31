"""Job definition for the batch job that will deploy the Minecraft server on EC2."""

from aws_cdk import Stack
from aws_cdk import aws_batch_alpha as batch_alpha
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from cdk_minecraft.constants import AWSCDK_MINECRAFT_SERVER_DEPLOYER__DIR
from cdk_minecraft.deploy_server_batch_job.server_backup_docker_image import MinecraftServerBackupServiceImage
from constructs import Construct


def make_minecraft_ec2_deployment__batch_job_definition(
    scope: Construct,
    id_prefix: str,
    backups_bucket_name: str,
) -> batch_alpha.JobDefinition:
    """Create a batch job definition to deploy a Minecraft server on EC2.

    Parameters
    ----------
    scope : Construct
        The scope of the stack.
    id_prefix : str
        The prefix to use for the id of the job definition.
        The id will be of the form f"{id_prefix}JobDefinition".

    Returns
    -------
    batch_alpha.JobDefinition
        The job definition.
    """
    execution_role: iam.Role = make_batch_execution_role(scope=scope, id_prefix=id_prefix)
    job_role: iam.Role = make_cdk_deployment_role(scope=scope, id_prefix=id_prefix)

    stack = Stack.of(scope)

    backup_service_image = MinecraftServerBackupServiceImage(
        scope=scope, id=f"{id_prefix}MinecraftServerBackupServiceImage", ensure_unique_ids=True
    )

    return batch_alpha.JobDefinition(
        scope=scope,
        id=f"{id_prefix}CdkMinecraftEc2DeploymentJD",
        container=batch_alpha.JobDefinitionContainer(
            image=ecs.ContainerImage.from_asset(
                directory=str(AWSCDK_MINECRAFT_SERVER_DEPLOYER__DIR),
                platform=ecr_assets.Platform.LINUX_AMD64,
            ),
            command=["cdk", "deploy", "--app", "'python3 /app/app.py'", "--require-approval=never"],
            job_role=job_role,
            execution_role=execution_role,
            log_configuration=batch_alpha.LogConfiguration(
                log_driver=batch_alpha.LogDriver.AWSLOGS,
                options={
                    # With the awslogs-group option, you can specify the log group that the awslogs log driver
                    # sends its log streams to. If this isn't specified, aws/batch/job is used.
                    "awslogs-group": "minecraft-server-deployment-job",
                    # Specify whether you want the log group automatically created. If this option isn't specified, it defaults to false.
                    "awslogs-create-group": "true",
                },
            ),
            assign_public_ip=True,
            environment={
                "AWS_ACCOUNT_ID": stack.account,
                "AWS_REGION": stack.region,
                "BACKUP_SERVICE_ECR_REPO_ARN": backup_service_image.ecr_repo_arn,
                "BACKUP_SERVICE_DOCKER_IMAGE_URI": backup_service_image.image_uri,
                "MINECRAFT_SERVER_BACKUPS_BUCKET_NAME": backups_bucket_name,
            },
            vcpus=1,
            memory_limit_mib=2 * 1024,
        ),
        platform_capabilities=[batch_alpha.PlatformCapabilities.FARGATE],
    )


def make_cdk_deployment_role(scope: Construct, id_prefix: str) -> iam.Role:
    """Grant batch job privileges to run CDK commands to handle resources.

    Parameters
    ----------
    scope : Construct
        The scope of the stack.
    id_prefix : str
        The prefix to use for the id of the role.
        The id will be of the form f"{id_prefix}CdkDeploymentRole".

    Returns
    -------
    iam.Role
        The role granting the necessary privileges for CDK commands.
    """
    return iam.Role(
        scope=scope,
        id=f"{id_prefix}CdkDeployRole",
        assumed_by=iam.ServicePrincipal(service="ecs-tasks.amazonaws.com"),
        managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")],
    )


def make_batch_execution_role(scope: Construct, id_prefix: str) -> iam.Role:
    """Create a role that can be assumed by the batch job to execute the CDK commands.

    Parameters
    ----------
    scope : Construct
        The scope of the stack.
    id_prefix : str
        The prefix to use for the id of the role.
        The id will be of the form f"{id_prefix}BatchExecutionRole".

    Returns
    -------
    iam.Role
        The role granting the necessary privileges for CDK commands.
    """
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
                                # "logs:CreateLogStream",
                                # "logs:PutLogEvents",
                                # from AWS docs
                                "ec2:DescribeAccountAttributes",
                                "ec2:DescribeInstances",
                                "ec2:DescribeInstanceAttribute",
                                "ec2:DescribeSubnets",
                                "ec2:DescribeSecurityGroups",
                                "ec2:DescribeKeyPairs",
                                "ec2:DescribeImages",
                                "ec2:DescribeImageAttribute",
                                "ec2:DescribeInstanceStatus",
                                "ec2:DescribeSpotInstanceRequests",
                                "ec2:DescribeSpotFleetInstances",
                                "ec2:DescribeSpotFleetRequests",
                                "ec2:DescribeSpotPriceHistory",
                                "ec2:DescribeVpcClassicLink",
                                "ec2:DescribeLaunchTemplateVersions",
                                "ec2:CreateLaunchTemplate",
                                "ec2:DeleteLaunchTemplate",
                                "ec2:RequestSpotFleet",
                                "ec2:CancelSpotFleetRequests",
                                "ec2:ModifySpotFleetRequest",
                                "ec2:TerminateInstances",
                                "ec2:RunInstances",
                                "autoscaling:DescribeAccountLimits",
                                "autoscaling:DescribeAutoScalingGroups",
                                "autoscaling:DescribeLaunchConfigurations",
                                "autoscaling:DescribeAutoScalingInstances",
                                "autoscaling:CreateLaunchConfiguration",
                                "autoscaling:CreateAutoScalingGroup",
                                "autoscaling:UpdateAutoScalingGroup",
                                "autoscaling:SetDesiredCapacity",
                                "autoscaling:DeleteLaunchConfiguration",
                                "autoscaling:DeleteAutoScalingGroup",
                                "autoscaling:CreateOrUpdateTags",
                                "autoscaling:SuspendProcesses",
                                "autoscaling:PutNotificationConfiguration",
                                "autoscaling:TerminateInstanceInAutoScalingGroup",
                                "ecs:DescribeClusters",
                                "ecs:DescribeContainerInstances",
                                "ecs:DescribeTaskDefinition",
                                "ecs:DescribeTasks",
                                "ecs:ListAccountSettings",
                                "ecs:ListClusters",
                                "ecs:ListContainerInstances",
                                "ecs:ListTaskDefinitionFamilies",
                                "ecs:ListTaskDefinitions",
                                "ecs:ListTasks",
                                "ecs:CreateCluster",
                                "ecs:DeleteCluster",
                                "ecs:RegisterTaskDefinition",
                                "ecs:DeregisterTaskDefinition",
                                "ecs:RunTask",
                                "ecs:StartTask",
                                "ecs:StopTask",
                                "ecs:UpdateContainerAgent",
                                "ecs:DeregisterContainerInstance",
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "logs:DescribeLogGroups",
                                "iam:GetInstanceProfile",
                                "iam:GetRole",
                            ],
                            "Resource": "*",
                        }
                    ],
                }
            ),
        )
    )

    return role
