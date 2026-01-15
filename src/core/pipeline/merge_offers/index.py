import os

import boto3
from core.offer_merger import OfferMerger

# AWS Resources
dynamodb_client = boto3.client("dynamodb")
dynamodb_resource = boto3.resource("dynamodb")
seen_offers_table = dynamodb_resource.Table(os.getenv("SEEN_OFFERS_TABLE") or "")


def handler(event, context):
    """
    Lambda handler: Merge offers from spiders and filter seen ones.

    Input:
        event["offers"]: List of lists of offers from each spider

    Returns:
        Dict: { "batches": [[...], [...], ...] } or { "batches": None }
    """

    try:
        offers = event.get("offers", [])
        if not offers:
            print("No offers provided in event")
            return {
                "batches": None,
            }

        merger = OfferMerger(dynamodb_client, seen_offers_table, seen_offers_table.name)
        result = merger.process_offers(offers)

        return result
    except Exception as e:
        print(f"Error in MergeOffers handler: {e}")
        return {
            "batches": None,
        }
