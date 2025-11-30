import os

import boto3

# AWS
DYNAMODB = boto3.resource("dynamodb")
CONFIG_TABLE = DYNAMODB.Table(os.getenv("CONFIG_TABLE"))


def handler(event, context):
    """
    Lee la tabla de configuraciones y retorna una lista de spiders habilidatos.
    """
    response = CONFIG_TABLE.scan()
    items = response.get("Items", [])

    enabled = []
    for it in items:
        if it.get("enabled", True):
            lambda_name = it.get("lambda_name")
            if not lambda_name:
                continue  # Skip if no lambda name

            enabled.append(
                {
                    "id": it.get("id"),
                    "lambda_name": lambda_name,
                    "config": it.get("config", {}),
                }
            )

    return {
        "spiders": enabled,
    }
