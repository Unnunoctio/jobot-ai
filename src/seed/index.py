import json

import boto3

TABLE_NAME = "SpiderConfigTable"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

resp = table.scan(Limit=1)
if resp.get("Items"):
    print("Table already seeded")
    exit(0)

with open("src/seed/seed.json", "r") as f:
    items = json.load(f)

with table.batch_writer() as batch:
    for item in items:
        batch.put_item(Item=item)

print("Seeded successfully")
