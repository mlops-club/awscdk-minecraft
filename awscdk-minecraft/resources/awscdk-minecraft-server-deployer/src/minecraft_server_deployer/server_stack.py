"""Boilerplate stack to make sure the CDK is set up correctly."""


from textwrap import dedent

from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct


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

    def __init__(self, scope: Construct, construct_id: str, version="1.19.3", **kwargs) -> None:
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

        ec2.Instance(
            scope=self,
            id="MinecraftServerInstance",
            vpc=_vpc,
            instance_type=ec2.InstanceType("t2.medium"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            user_data=ec2.UserData.custom(
                dedent(
                    f"""\
#!/bin/bash

cat << EOF > /home/ec2-user/docker-compose.yml
version: '3.7'
services:
    minecraft:
        image: itzg/minecraft-server
        restart: always
        ports:
            - 25565:25565
        environment:
            EULA: "TRUE"
            VERSION: "{version}"
        networks:
        - minecraft-server
        deploy:
            replicas: 1

EOF

cat << EOF > /home/ec2-user/setup.sh
#!/bin/bash
yum update -y
yum install -y docker

# install docker-compose and make the binary executable
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose

service docker start

# install aws cli
yum install -y python3
pip3 install awscli --upgrade --user
# install aws s3 sync
yum install -y s3fs-fuse

cd /home/ec2-user
# initialize docker swarm
docker swarm init
# create a docker stack
docker stack deploy -c docker-compose.yml minecraft
EOF

sudo chmod +x /home/ec2-user/setup.sh
sudo /home/ec2-user/setup.sh
                """
                )
            ),
            user_data_causes_replacement=True,
            role=_iam_role,
            security_group=_sg,
        )
