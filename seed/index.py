import json

import boto3
from botocore.exceptions import ClientError

DYNAMODB = boto3.resource("dynamodb")
CONFIG_TABLE = DYNAMODB.Table("SpiderConfigTable")

S3_CLIENT = boto3.client("s3")
S3_BUCKET_NAME = "jobot-ai"


def seed_config_table():
    try:
        with open("seed/seed.json", "r") as f:
            items = json.load(f)

        with CONFIG_TABLE.batch_writer() as batch:
            for item in items:
                # put_item en DynamoDB = INSERT o UPDATE (upsert)
                batch.put_item(Item=item)

        print(f"Seed ejecutado correctamente ({len(items)} items)")

    except ClientError as e:
        print("Error al seedear la tabla:", e)
    except FileNotFoundError:
        print("Archivo seed.json no encontrado")


def add_user_experience():
    try:
        S3_CLIENT.head_bucket(Bucket=S3_BUCKET_NAME)
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "404":
            region = boto3.session.Session().region_name
            if region == "us-east-1":
                S3_CLIENT.create_bucket(Bucket=S3_BUCKET_NAME)
            else:
                S3_CLIENT.create_bucket(Bucket=S3_BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": region})  # type: ignore
        else:
            print(f"Error al verificar el bucket: {e}")

    try:
        S3_CLIENT.upload_file("seed/user_experience.txt", S3_BUCKET_NAME, "user_experience.txt", ExtraArgs={"ContentType": "text/plain"})

        print("User experience added successfully")
    except ClientError as e:
        print(f"Error al subir el archivo: {e}")


if __name__ == "__main__":
    seed_config_table()
    add_user_experience()
