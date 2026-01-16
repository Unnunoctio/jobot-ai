from botocore.exceptions import ClientError
from mypy_boto3_s3.client import S3Client


class UserExperienceLoader:
    """Handles loading user experience data from S3."""

    @staticmethod
    def load(client: S3Client, bucket_name: str, key: str) -> str:
        """Load user experience data from S3."""

        try:
            response = client.get_object(Bucket=bucket_name, Key=key)
            content = response["Body"].read().decode("utf-8")

            if not content.strip():
                raise ValueError("User experience file is empty")

            return content
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            print(f"Error loading user experience: {error_code} - {e}")
            raise
        except Exception as e:
            print(f"Unexpected error loading user experience: {e}")
            raise
