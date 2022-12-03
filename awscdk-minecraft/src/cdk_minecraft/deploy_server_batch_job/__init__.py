"""
Prepares a docker-container capable of deploying the minecraft server using AWS CDK.

The docker-container runs on AWS Batch. The constructs created in this module
build a docker image with two things inside:

- the AWS CDK CLI
- a python package containing an ``aws_cdk.App`` that can deploy the
  minecraft server using ``cdk deploy``

Once this image is built, the constructs in this module stage the docker image
in AWS ECR (elastic container registry).

An ``AWS::Batch::JobDefinition`` is created that is aware of this uploaded docker image.
The ARN of the JobDefinition can be used in the AWS SDK e.g. ``boto3`` to trigger
the container to run, which executes the script and provisions a Minecraft server.

By supplying a different command to the container on startup, the same Docker
image can be used to destroy the created Minecraft server.
"""
