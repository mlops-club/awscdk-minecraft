"""Boilerplate stack to make sure the CDK is set up correctly."""

from pathlib import Path
from string import Template

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct

THIS_DIR = Path(__file__).parent
USER_DATA_SH_TEMPLATE_FPATH = THIS_DIR / "../../resources/user-data.sh"


def render_user_data_script(minecraft_semantic_version: str) -> str:
    """Render the user data script for the EC2 instance.

    Parameters
    ----------
    minecraft_semantic_version : str
        The semantic version of the minecraft server to deploy.

    Returns
    -------
    str
        The rendered user data script.
    """
    return Template(USER_DATA_SH_TEMPLATE_FPATH.read_text()).substitute(
        {
            "MINECRAFT_SERVER_SEMANTIC_VERSION": minecraft_semantic_version,
        }
    )


class ServerStack(Stack):
    """Stack responsible for creating the running minecraft server on AWS.

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
    bucket : s3.Bucket
        The bucket where the server files will be stored.
    """

    def __init__(self, scope: Construct, construct_id: str, minecraft_server_version: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(scope=self, id="MinecraftServer")

        _vpc = ec2.Vpc.from_lookup(scope=self, is_default=True, id="defaultVpc")

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
            render_user_data_script(minecraft_semantic_version=minecraft_server_version)
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

        cloudwatch.Alarm(
            scope=self,
            id="MinecraftServerCpuAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/EC2",
                metric_name="CPUUtilization",
                dimensions={"InstanceId": _ec2.instance_id},
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
            scope=self,
            id="MinecraftServerMemoryAlarm",
            metric=cloudwatch.Metric(
                namespace="System/Linux",
                metric_name="MemoryUtilization",
                dimensions={"InstanceId": _ec2.instance_id},
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
            scope=self,
            id="MinecraftServerDiskAlarm",
            metric=cloudwatch.Metric(
                namespace="System/Linux",
                metric_name="DiskSpaceUtilization",
                dimensions={"InstanceId": _ec2.instance_id},
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
            scope=self,
            id="MinecraftServerNetworkAlarm",
            metric=cloudwatch.Metric(
                namespace="System/Linux",
                metric_name="NetworkIn",
                dimensions={"InstanceId": _ec2.instance_id},
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
            scope=self,
            id="MinecraftServerOpenConnectionsAlarm",
            metric=cloudwatch.Metric(
                namespace="System/Linux",
                metric_name="NetworkIn",
                dimensions={"InstanceId": _ec2.instance_id},
                statistic="Average",
                period=cdk.Duration.minutes(1),
            ),
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=80,
            evaluation_periods=1,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            alarm_description="Alarm if number of open connections is greater than 80% for 1 minute",
        )
