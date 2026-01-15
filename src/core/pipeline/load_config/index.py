import os

import boto3
from core.config_loader import ConfigLoader

# AWS resources
dynamodb = boto3.resource("dynamodb")
config_table = dynamodb.Table(os.getenv("CONFIG_TABLE") or "")


def handler(event, context):
    """
    Lambda handler: Load enabled spider configurations from DynamoDB.

    Returns:
        Dict: { "spiders": [...] } or { "spiders": [], "error": str }
    """

    try:
        loader = ConfigLoader(config_table)
        enabled_spiders = loader.load_enabled_spiders()

        if not enabled_spiders:
            print("No enabled spiders found in configuration")

        return {
            "spiders": enabled_spiders,
        }
    except Exception as e:
        print(f"Error in LoadConfig handler: {e}")
        return {
            "spiders": [],
            "error": str(e),
        }
