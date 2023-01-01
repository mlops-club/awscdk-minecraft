from typing import Dict, Optional

import boto3
from mypy_boto3_cloudformation import CloudFormationClient
from mypy_boto3_cloudformation.literals import StackStatusType
from mypy_boto3_cloudformation.type_defs import DescribeStacksOutputTypeDef
from loguru import logger


def try_get_cloud_formation_stack_status(
    stack_name: str, aws_region: Optional[str] = None
) -> Optional["StackStatusType"]:
    """
    Try to get the status of the CloudFormation stack.

    :param stack_name: The name of the CloudFormation stack.
    :param aws_region: The AWS region in which the CloudFormation stack exists.

    :return: The status of the CloudFormation stack. If the stack does not exist, returns None.
    """
    cfn_client: CloudFormationClient = boto3.client("cloudformation", region_name=aws_region)
    try:
        response: "DescribeStacksOutputTypeDef" = cfn_client.describe_stacks(StackName=stack_name)
        stack_status: "StackStatusType" = response["Stacks"][0]["StackStatus"]
    except cfn_client.exceptions.ClientError as err:
        stack_status = None
        logger.error(f"Error getting CloudFormation stack status: {err}")
    return stack_status


def try_get_cloud_formation_stack_outputs(
    stack_name: str, aws_region: Optional[str] = None
) -> Optional[Dict[str, str]]:
    """
    Try to get the outputs of the CloudFormation stack.

    Note: we *highly* recommended you create a `typing.TypedDict` subclass to represent the outputs
    of the particular stack you are querying. That way you can get autocompletion against your stack outputs.

    :param stack_name: The name of the CloudFormation stack.
    :param aws_region: The AWS region in which the CloudFormation stack exists.

    :return: The outputs of the CloudFormation stack. If the stack does not exist, returns None.
    It will be a dict of the form:

    ```python
    {
        "OutputKey1": "OutputValue1",
        "OutputKey2": "OutputValue2",
    }
    ```
    """
    cfn_client: CloudFormationClient = boto3.client("cloudformation", region_name=aws_region)
    try:
        response: "DescribeStacksOutputTypeDef" = cfn_client.describe_stacks(StackName=stack_name)
        outputs: dict = {
            output["OutputKey"]: output["OutputValue"] for output in response["Stacks"][0]["Outputs"]
        }
    except cfn_client.exceptions.ClientError as err:
        outputs = None
        logger.error(f"Error getting CloudFormation stack outputs: {err}")
    return outputs


def get_cloudform_output_value(cloud_form_stack_name: str, cloud_form_key_name: str) -> str:
    """
    Return the cloud form output value for the provided output name.

    :param cloud_form_stack_name: name of the cloud formation stack
    :param cloud_form_key_name: key for cloudformation output key value pair

    :return: cloudformation output value for the provided key name
    """
    stack_outputs: Dict[str, str] = try_get_cloud_formation_stack_outputs(cloud_form_stack_name)
    stack_value = stack_outputs[cloud_form_key_name]
    return stack_value
