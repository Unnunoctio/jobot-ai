import asyncio

from spider import BNESpider


def handler(event, context):
    # TODO: Get spider config
    spider_config = event.get("config", {})
    spider = BNESpider(spider_config)

    # TODO: Get offers from bne
    offers = asyncio.run(spider.run())

    # TODO: Return offers
    return offers
