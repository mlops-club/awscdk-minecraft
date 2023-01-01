#!/bin/bash

# This script provides a few different arguments that use the AWS CLI
# to perform various actions on the S3 bucket that stores the Minecraft
# server data. The script is intended to be run on the EC2 host that
# runs the Minecraft server.

# print the commands this script runs as they are executed
# set -x

# fail if any command fails
set -e


export BACKUPS_BUCKET=${BACKUPS_BUCKET?Must supply BACKUPS_BUCKET}
export SERVER_DATA_DIR=${SERVER_DATA_DIR:-/minecraft/minecraft-data}
export BACKUPS_S3_PREFIX=${BACKUPS_S3_PREFIX:-minecraft-backups}
export BACKUP_INTERVAL_SECONDS=${BACKUP_INTERVAL_SECONDS:-3600}

# echo a string of the form "<ISO timestamp>--minecraft-backup.zip"
function make-new-backup-name() {
    echo "$(date -u +"%Y-%m-%dT%H:%M:%S")--minecraft-backup.zip"
}

# create a backup of the Minecraft server data
function backup-to-s3() {
    echo "zipping Minecraft server data at $SERVER_DATA_DIR..."

    BACKUP_NAME=$(make-new-backup-name)

    cd "$SERVER_DATA_DIR"
    zip -r "../$BACKUP_NAME" ./*
    cd "$SERVER_DATA_DIR/.."

    echo "uploading Minecraft server data to s3://$BACKUPS_BUCKET/$BACKUPS_S3_PREFIX/$BACKUP_NAME..."
    aws s3 cp "$BACKUP_NAME" "s3://$BACKUPS_BUCKET/$BACKUPS_S3_PREFIX/$BACKUP_NAME"

    echo "cleaning up artifact"
    rm "$BACKUP_NAME"
}

# start an infinite loop that backs up the server files on a regular interval
function backup-to-s3-on-interval() {
    while true; do
        sleep $BACKUP_INTERVAL_SECONDS
        backup-to-s3
    done
}

function restore-latest-backup-from-s3() {
    LATEST_BACKUP_S3_KEY=$(get-latest-backup-s3-key)
    echo "downloading Minecraft server data from s3://$BACKUPS_BUCKET/$BACKUPS_S3_PREFIX/$LATEST_BACKUP_S3_KEY ..."
    aws s3 cp "s3://$BACKUPS_BUCKET/$BACKUPS_S3_PREFIX/$LATEST_BACKUP_S3_KEY" .

    echo "extracting Minecraft server data from $LATEST_BACKUP_S3_KEY to $SERVER_DATA_DIR..."
    unzip -o "$LATEST_BACKUP_S3_KEY" -d "$SERVER_DATA_DIR"
}

function get-latest-backup-s3-key() {
    aws s3 ls "s3://$BACKUPS_BUCKET/$BACKUPS_S3_PREFIX/" | \
        sort | \
        tail -1 | \
        awk '{print $4}'
}

# echo a string of the form "<ISO timestamp>--minecraft-backup.zip"
function make-new-backup-name() {
    echo "$(date -u +"%Y-%m-%dT%H:%M:%S")--minecraft-backup.zip"
}

get-latest-backup-s3-key

function main() {
    case "$1" in
        "backup")
            backup-to-s3
            ;;
        "restore")
            restore-latest-backup-from-s3
            ;;
        "list-backups")
            aws s3 ls "s3://$BACKUPS_BUCKET/$BACKUPS_S3_PREFIX"
            ;;
        "delete-backup")
            BACKUP_S3_KEY=$2
            aws s3 rm "s3://$BACKUPS_BUCKET/$BACKUPS_S3_PREFIX/$BACKUP_S3_KEY"
            ;;
        "backup-on-interval")
            backup-to-s3-on-interval
            ;;
        *)
            echo "Valid commands are: backup, restore, list-backups, delete-backup, backup-on-interval. Got $1."
            ;;
    esac
}

echo $1
main "$@"
