from typing import Any, Dict, List, Optional

from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import Table


class ConfigLoader:
    """Handles loading and validation of spider configurations."""

    def __init__(self, table: Table):
        self.table = table

    def load_enabled_spiders(self) -> List[Dict[str, Any]]:
        """Load all enabled spider configurations with validation."""

        try:
            response = self.table.scan()
            items = response.get("Items", [])

            while "LastEvaluatedKey" in response:
                response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                items.extend(response.get("Items", []))

            enabled_spiders = []
            for item in items:
                spider = self._validate_and_parse_config(item)
                if spider:
                    enabled_spiders.append(spider)

            return enabled_spiders
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            print(f"DynamoDB error loading config: {error_code} - {e}")
            raise
        except Exception as e:
            print(f"Unexpected error loading config: {e}")
            raise

    def _validate_and_parse_config(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Validate and parse a single spider configuration."""

        if not item.get("enabled", True):
            return None

        spider_id = item.get("id")
        lambda_name = item.get("lambda_name")

        if not spider_id:
            print(f"Config missing spider ID field: {item}")
            return None

        if not lambda_name:
            print(f"Spider {spider_id} missing lambda name, skipping")
            return None

        return {
            "id": spider_id,
            "enabled": item.get("enabled", True),
            "lambda_name": lambda_name,
            "config": item.get("config", {}),
        }
