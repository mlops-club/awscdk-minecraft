"""Boilerplate stack to make sure the CDK is set up correctly."""

from pathlib import Path
from string import Template

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct

THIS_DIR = Path(__file__).parent
USER_DATA_SH_TEMPLATE_FPATH = (THIS_DIR / "../../resources/user-data.template.sh").resolve()


class ServerStack(Stack):
    """Stack responsible for creating the running minecraft server on AWS.

    :param scope: The scope of the stack.
    :param construct_id: The ID of the stack.
    :param minecraft_server_version: The semantic version of the Minecraft server to install.
    :param backup_service_ecr_repo_arn: The ARN of the ECR repository for the backup service.
    :param backup_service_docker_image_uri: The URI of the Docker image in ECR for the backup service.
    :param minecraft_server_backups_bucket_name: The name of the S3 bucket to store backups in.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        minecraft_server_version: str,
        backup_service_ecr_repo_arn: str,
        backup_service_docker_image_uri: str,
        minecraft_server_backups_bucket_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        _vpc = ec2.Vpc.from_lookup(scope=self, id="DefaultVpc", is_default=True)

        # set up security group to allow inbound traffic on port 25565 for anyone
        _sg = ec2.SecurityGroup(
            scope=self,
            id="MinecraftServerSecurityGroup",
            vpc=_vpc,
            allow_all_outbound=True,
        )
        _sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(25565),
            description="Allow inbound traffic on port 25565",
        )
        _sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="Allow inbound traffic on port 22",
        )
        # allow all outbound traffic
        _sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic(),
            description="Allow all outbound traffic",
        )

        # create iam role for ec2 instance using AmazonSSMManagedInstanceCore
        _iam_role = iam.Role(
            scope=self,
            id="MinecraftServerIamRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        _iam_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        # fill in user data script
        _user_data_script = ec2.UserData.custom(
            render_user_data_script(
                minecraft_semantic_version=minecraft_server_version,
                backup_service_docker_image_uri=backup_service_docker_image_uri,
                minecraft_server_backups_bucket_name=minecraft_server_backups_bucket_name,
                # TODO: receive this as a parameter rather than hardcoding it
                restore_from_most_recent_backup=True,
                aws_account_id=self.account,
                aws_region=self.region,
            )
        )

        _ec2 = ec2.Instance(
            scope=self,
            id="MinecraftServerInstance",
            vpc=_vpc,
            instance_type=ec2.InstanceType("t2.medium"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            user_data=_user_data_script,
            user_data_causes_replacement=True,
            role=_iam_role,
            security_group=_sg,
        )
        grant_ecr_pull_access(
            ecr_repo_arn=backup_service_ecr_repo_arn, role=_ec2.role, repo_construct_id="BackupServiceEcrRepo"
        )
        grant_s3_read_write_access(
            bucket_name=minecraft_server_backups_bucket_name,
            role=_ec2.role,
            bucket_construct_id="MinecraftServerBackupsBucket",
        )

        # add stack output for ip address of the ec2 instance
        cdk.CfnOutput(
            scope=self,
            id="MinecraftServerIp",
            value=_ec2.instance_public_ip,
            description="The public IP address of the Minecraft server",
        )

        add_alarms_to_stack(scope=self, ec2_instance_id=_ec2.instance_id)


def grant_ecr_pull_access(ecr_repo_arn: str, role: iam.Role, repo_construct_id: str):
    """Grant the given role access to pull docker images from the given ECR repo."""
    ecr_repo = ecr.Repository.from_repository_arn(scope=role, id=repo_construct_id, repository_arn=ecr_repo_arn)
    ecr_repo.grant_pull(role)


def render_user_data_script(
    minecraft_semantic_version: str,
    backup_service_docker_image_uri: str,
    minecraft_server_backups_bucket_name: str,
    aws_account_id: str,
    aws_region: str,
    restore_from_most_recent_backup: bool = True,
    backup_interval_seconds: int = 60 * 10,
) -> str:
    """Render the user data script for the EC2 instance.

    :param minecraft_semantic_version: The semantic version of the Minecraft server to install.
    :param backup_service_docker_image_uri: The URI of the Docker image in ECR for the backup service.
    """
    return Template(USER_DATA_SH_TEMPLATE_FPATH.read_text()).substitute(
        {
            "MINECRAFT_SERVER_SEMANTIC_VERSION": minecraft_semantic_version,
            "BACKUP_SERVICE_DOCKER_IMAGE_URI": backup_service_docker_image_uri,
            "RESTORE_FROM_MOST_RECENT_BACKUP": str(restore_from_most_recent_backup).lower(),
            "MINECRAFT_SERVER_BACKUPS_BUCKET_NAME": minecraft_server_backups_bucket_name,
            "AWS_ACCOUNT_ID": aws_account_id,
            "AWS_REGION": aws_region,
            "BACKUP_INTERVAL_SECONDS": str(backup_interval_seconds),
        }
    )


def grant_s3_read_write_access(bucket_name: str, role: iam.Role, bucket_construct_id: str):
    """Grant the given role read/write access to the given S3 bucket."""
    bucket = s3.Bucket.from_bucket_name(scope=role, id=bucket_construct_id, bucket_name=bucket_name)
    bucket.grant_read_write(role)


def add_alarms_to_stack(scope: Construct, ec2_instance_id: str) -> None:
    """Add alarms to the stack.

    Parameters
    ----------
    scope : Construct
        The scope of the stack.
    ec2_instance_id : str
        The ID of the EC2 instance to monitor.

    Returns
    -------
    None
    """
    cloudwatch.Alarm(
        scope=scope,
        id="MinecraftServerCpuAlarm",
        metric=cloudwatch.Metric(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions_map={"InstanceId": ec2_instance_id},
            statistic="Average",
            period=cdk.Duration.minutes(1),
        ),
        comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        threshold=80,
        evaluation_periods=1,
        treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        alarm_description="Alarm if CPU usage is greater than 80% for 1 minute",
    )

    cloudwatch.Alarm(
        scope=scope,
        id="MinecraftServerMemoryAlarm",
        metric=cloudwatch.Metric(
            namespace="System/Linux",
            metric_name="MemoryUtilization",
            dimensions_map={"InstanceId": ec2_instance_id},
            statistic="Average",
            period=cdk.Duration.minutes(1),
        ),
        comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        threshold=80,
        evaluation_periods=1,
        treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        alarm_description="Alarm if memory usage is greater than 80% for 1 minute",
    )

    cloudwatch.Alarm(
        scope=scope,
        id="MinecraftServerDiskAlarm",
        metric=cloudwatch.Metric(
            namespace="System/Linux",
            metric_name="DiskSpaceUtilization",
            dimensions_map={"InstanceId": ec2_instance_id},
            statistic="Average",
            period=cdk.Duration.minutes(1),
        ),
        comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        threshold=80,
        evaluation_periods=1,
        treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        alarm_description="Alarm if disk usage is greater than 80% for 1 minute",
    )

    cloudwatch.Alarm(
        scope=scope,
        id="MinecraftServerNetworkAlarm",
        metric=cloudwatch.Metric(
            namespace="System/Linux",
            metric_name="NetworkIn",
            dimensions_map={"InstanceId": ec2_instance_id},
            statistic="Average",
            period=cdk.Duration.minutes(1),
        ),
        comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        threshold=80,
        evaluation_periods=1,
        treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        alarm_description="Alarm if network usage is greater than 80% for 1 minute",
    )

    cloudwatch.Alarm(
        scope=scope,
        id="MinecraftServerOpenConnectionsAlarm",
        metric=cloudwatch.Metric(
            namespace="System/Linux",
            metric_name="NetworkIn",
            dimensions_map={"InstanceId": ec2_instance_id},
            statistic="Average",
            period=cdk.Duration.minutes(1),
        ),
        comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        threshold=80,
        evaluation_periods=1,
        treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        alarm_description="Alarm if number of open connections is greater than 80% for 1 minute",
    )


if __name__ == "__main__":
    print(
        render_user_data_script(
            minecraft_semantic_version="1.16.5",
            backup_service_docker_image_uri="some-image-uri",
            minecraft_server_backups_bucket_name="some-bucket-name",
            restore_from_most_recent_backup=True,
            aws_account_id="some-aws-account-id",
            aws_region="some-aws-region",
        )
    )
