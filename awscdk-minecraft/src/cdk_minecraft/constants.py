"""Constant values used by the entire project."""

from pathlib import Path

THIS_DIR = Path(__file__).parent
RESOURCES_DIR = THIS_DIR / "resources"

AWSCDK_MINECRAFT_SERVER_DEPLOYER__DIR = RESOURCES_DIR / "awscdk-minecraft-server-deployer"
MINECRAFT_PLATFORM_BACKEND_API__DIR = RESOURCES_DIR / "minecraft-platform-backend-api"
MINECRAFT_PLATFORM_FRONTEND_STATIC_WEBSITE__DIR = RESOURCES_DIR / "minecraft-platform-frontend-static"
MINECRAFT_PLATFORM_BACKUP_SERVICE__DIR = RESOURCES_DIR / "minecraft-platform-backup-service"
