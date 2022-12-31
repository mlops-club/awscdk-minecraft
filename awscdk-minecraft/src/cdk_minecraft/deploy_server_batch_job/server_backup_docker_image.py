"""AWS CDK construct that builds the docker image for the Minecraft server backup service."""

from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ecr_assets as ecr_assets

import cdk_ecr_deployment as ecr_deployment
from constructs import Construct
from cdk_minecraft.constants import MINECRAFT_PLATFORM_BACKUP_SERVICE__DIR


class MinecraftServerBackupServiceImage(Construct):
    def __init__(self, scope: "Construct", id: str, ensure_unique_ids: bool = False) -> None:
        """Build the docker image for the Minecraft server backup service."""
        super().__init__(scope, id)

        self.namer = lambda name: f"{id}-{name}" if ensure_unique_ids else name

        # build the backup-service docker image
        minecraft_server_backup_service_image = ecr_assets.DockerImageAsset(
            scope=scope,
            id=self.namer("MinecraftBackupServiceImage"),
            directory=str(MINECRAFT_PLATFORM_BACKUP_SERVICE__DIR),
            platform=ecr_assets.Platform.LINUX_AMD64,
        )

        # create an ECR repo to upload the image to
        self._ecr_repo = ecr.Repository(
            scope=scope,
            id=self.namer("MinecraftBackupServiceEcrRepo"),
        )

        # push the image to the ECR repo
        ecr_deployment.ECRDeployment(
            scope=scope,
            id=self.namer("MinecraftBackupServiceEcrDeployment"),
            src=ecr_deployment.DockerImageName(minecraft_server_backup_service_image.image_uri),
            dest=ecr_deployment.DockerImageName(self._ecr_repo.repository_uri),
        )

        self.image_uri = self._ecr_repo.repository_uri
        """Use this in 'docker pull <image_uri>' to pull the image from ECR."""

        self.ecr_repo_arn = self._ecr_repo.repository_arn
        """Use this to grant access to the ECR repo to other roles."""
