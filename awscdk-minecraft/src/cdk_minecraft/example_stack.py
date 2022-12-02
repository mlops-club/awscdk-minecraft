"""Boilerplate stack to make sure the CDK is set up correctly."""


from aws_cdk import Stack
from constructs import Construct


class ExampleStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)