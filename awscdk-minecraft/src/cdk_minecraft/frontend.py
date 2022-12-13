"""This module contains utilities for deploying the Minecraft frontend website to an S3 bucket."""

from aws_prototyping_sdk.static_website import StaticWebsite
from cdk_minecraft.constants import MINECRAFT_PLATFORM_FRONTEND_STATIC_WEBSITE__DIR
from constructs import Construct


def make_minecraft_platform_frontend_static_website(
    scope: Construct,
    id_prefix: str,
) -> StaticWebsite:
    """Deploy the static minecraft platform frontend web files to a S3/CloudFront static site."""
    return StaticWebsite(
        scope=scope,
        id=f"{id_prefix}MinecraftPlatformFrontend",
        website_content_path=str(MINECRAFT_PLATFORM_FRONTEND_STATIC_WEBSITE__DIR),
        # distribution_props=cloudfront.DistributionProps(
        #     # USA, Canada, Europe, & Israel.
        #     price_class=cloudfront.PriceClass.PRICE_CLASS_100,
        #     default_behavior=cloudfront.BehaviorOptions(origin=cloudfront.Origin)
        # )
    )
