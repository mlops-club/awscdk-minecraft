"""Boilerplate stack to make sure the CDK is set up correctly."""


from aws_cdk import Stack
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

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(self, "MinecraftServer")
