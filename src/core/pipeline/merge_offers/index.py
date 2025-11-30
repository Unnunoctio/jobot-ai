import os

import boto3

# AWS
DYNAMODB_CLIENT = boto3.client("dynamodb")
SEEN_OFFERS_TABLE = boto3.resource("dynamodb").Table(os.getenv("SEEN_OFFERS_TABLE"))


def handler(event, context):
    """
    Obtiene una lista de ofertas, filtra las ofertas ya vistas y separa las nuevas ofertas en lotes de 5.
    """
    # TODO: Obtener y aplanar el array de offers
    offers = event.get("offers", [])
    offers = [o for sublist in offers for o in sublist]

    # TODO: Filtrar las ofertas que ya se han visto
    new_offers = filter_new_offers(offers)

    if not new_offers or len(new_offers) == 0:
        return {
            "batches": None,
        }

    # TODO: Separar en lotes de 5
    batches = [new_offers[i : i + 5] for i in range(0, len(new_offers), 5)]

    return {
        "batches": batches,
    }


def filter_new_offers(offers: list[dict]) -> list[dict]:
    # Filter offers that are not in seen_offers_table
    BATCH_SIZE = 100
    offer_urls = [o["url"] for o in offers]
    seen_offers = set()

    for i in range(0, len(offers), BATCH_SIZE):
        chunk = offer_urls[i : i + BATCH_SIZE]

        response = DYNAMODB_CLIENT.batch_get_item(RequestItems={SEEN_OFFERS_TABLE.name: {"Keys": [{"url": {"S": url}} for url in chunk]}})

        items = response.get("Responses", {}).get(SEEN_OFFERS_TABLE.name, [])
        for item in items:
            seen_offers.add(item["url"]["S"])

    return [o for o in offers if o["url"] not in seen_offers]
