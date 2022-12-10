import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from cdk_minecraft import MinecraftPaasStack


@pytest.fixture(scope="module")
def example_template(dev_env):  # noqa: D103
    app = App()
    stack = MinecraftPaasStack(app, "my-stack-test", env=dev_env)
    template = Template.from_stack(stack)
    yield template


def test_no_buckets_found(example_template):  # noqa: D103
    example_template.resource_count_is("AWS::S3::Bucket", 0)
