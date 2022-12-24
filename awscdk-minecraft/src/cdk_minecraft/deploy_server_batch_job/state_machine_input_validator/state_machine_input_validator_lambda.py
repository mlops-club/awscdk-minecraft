from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_python_alpha as lambda_python
from constructs import Construct

THIS_DIR = Path(__file__).parent
MC_SERVER_PROVISION_SFN__INPUT_VALIDATOR__SRC_DIR = THIS_DIR / "resources"


def make_lambda_that_validates_input_of_the_provision_server_state_machine(
    scope: Construct, id_prefix: str
) -> lambda_python.PythonFunction:

    # define the lambda function
    return lambda_python.PythonFunction(
        scope,
        f"{id_prefix}ProvisionMcServerInputValidator",
        entry=str(MC_SERVER_PROVISION_SFN__INPUT_VALIDATOR__SRC_DIR),
        handler="handler",
        index="index.py",
        runtime=lambda_.Runtime.PYTHON_3_8,
        timeout=cdk.Duration.seconds(30),
        bundling=lambda_python.BundlingOptions(
            image=cdk.DockerImage.from_registry(image="lambci/lambda:build-python3.8"),
        ),
    )
