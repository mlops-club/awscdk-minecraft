"""This module contains utilities for deploying the Minecraft frontend website to an S3 bucket."""

import hashlib
import json
from typing import Optional

from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as cloudfront_origins
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
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
    top_level_hosted_zone: route53.IHostedZone,
    tls_cert: Optional[acm.ICertificate] = None,
) -> StaticWebsite:
    """Deploy the static minecraft platform frontend web files to a S3/CloudFront static site."""
    optional_kwargs = {}
    if None not in [top_level_hosted_zone, tls_cert]:
        website_bucket = s3.Bucket(scope, id=f"{id_prefix}WebsiteBucket")
        optional_kwargs["website_bucket"] = website_bucket
        optional_kwargs["distribution_props"] = cloudfront.DistributionProps(
            default_behavior=cloudfront.BehaviorOptions(
                origin=cloudfront_origins.S3Origin(website_bucket),
            ),
            domain_names=[f"minecraft-paas.{top_level_hosted_zone.zone_name}"],
            certificate=tls_cert,
        )

    static_website = StaticWebsite(
        scope=scope,
        id=f"{id_prefix}MinecraftPlatformFrontend",
        website_content_path=str(MINECRAFT_PLATFORM_FRONTEND_STATIC_WEBSITE__DIR),
        **optional_kwargs,
    )

    # add a DNS record for the frontend
    if None not in [top_level_hosted_zone, tls_cert]:
        route53.ARecord(
            scope=scope,
            id=f"{scope.node.id}FrontendARecord",
            zone=top_level_hosted_zone,
            target=route53.RecordTarget.from_alias(
                alias_target=route53_targets.CloudFrontTarget(
                    distribution=static_website.cloud_front_distribution,
                )
            ),
            record_name=f"minecraft-paas.{top_level_hosted_zone.zone_name}",
        )

    return static_website


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
