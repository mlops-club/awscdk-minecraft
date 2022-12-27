"""This module contains utilities for deploying the Minecraft frontend website to an S3 bucket."""

import hashlib
import json

from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment
from aws_prototyping_sdk.static_website import StaticWebsite
from cdk_minecraft.constants import MINECRAFT_PLATFORM_FRONTEND_STATIC_WEBSITE__DIR
from constructs import Construct


def create_config_json_file_in_static_site_s3_bucket(
    scope: Construct,
    id_prefix: str,
    backend_url: str,
    cognito_user_pool_id: str,
    cognito_app_client_id: str,
    cognito_hosted_ui_app_client_allowed_scopes: str,
    cognito_user_pool_region: str,
    cognito_hosted_ui_redirect_sign_in_url: str,
    cognito_hosted_ui_redirect_sign_out_url: str,
    cognito_hosted_ui_fqdn: str,
    static_site_bucket: s3.Bucket,
    static_site_construct: Construct,
) -> s3_deployment.BucketDeployment:
    config_json_contents = {
        "backend_api_url": backend_url,
        "cognito_user_pool_id": cognito_user_pool_id,
        "cognito_hosted_ui_app_client_id": cognito_app_client_id,
        "cognito_hosted_ui_app_client_allowed_scopes": cognito_hosted_ui_app_client_allowed_scopes,
        "cognito_hosted_ui_fqdn": cognito_hosted_ui_fqdn,
        "cognito_user_pool_region": cognito_user_pool_region,
        "cognito_hosted_ui_redirect_sign_in_url": cognito_hosted_ui_redirect_sign_in_url,
        "cognito_hosted_ui_redirect_sign_out_url": cognito_hosted_ui_redirect_sign_out_url,
    }

    config_json_s3_files = s3_deployment.BucketDeployment(
        scope=scope,
        id=hash_string_deterministically(json.dumps(config_json_contents)),
        # id="new-id",
        sources=[
            s3_deployment.Source.json_data(
                obj=config_json_contents,
                object_key="static/config.json",
            ),
        ],
        destination_bucket=static_site_bucket,
        exclude=["*"],
        include=["static/config.json"],
    )

    # the config.json file created by this function should be created
    # *after* the entire static site is deployed so that the config.json
    # created by this function does not get overwritten by a config.json
    # in the static site files
    config_json_s3_files.node.add_dependency(static_site_construct)

    return config_json_s3_files


def make_minecraft_platform_frontend_static_website(
    scope: Construct,
    id_prefix: str,
) -> StaticWebsite:
    """Deploy the static minecraft platform frontend web files to a S3/CloudFront static site."""
    return StaticWebsite(
        scope=scope,
        id=f"{id_prefix}MinecraftPlatformFrontend",
        website_content_path=str(MINECRAFT_PLATFORM_FRONTEND_STATIC_WEBSITE__DIR),
        # distribution_props=cloudfront.D
        # distribution_props=cloudfront.DistributionProps(
        #     # USA, Canada, Europe, & Israel.
        #     price_class=cloudfront.PriceClass.PRICE_CLASS_100,
        #     default_behavior=cloudfront.BehaviorOptions(origin=cloudfront.Origin),
        # ),
    )


def hash_string_deterministically(string: str) -> str:
    """Hash a string deterministically.

    Parameters
    ----------
    string : str
        The string to hash.

    Returns
    -------
    str
        The hashed string.
    """
    hashed_string: str = hashlib.sha256(string.encode("utf-8")).hexdigest()
    hashed_string_without_numbers = "".join([char for char in hashed_string if not char.isdigit()])
    return hashed_string_without_numbers
