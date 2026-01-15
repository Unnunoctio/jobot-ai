import asyncio

from spider import TrabajandoSpider


def handler(event, context):
    # TODO: Get spider config
    spider_config = event.get("config", {})
    spider = TrabajandoSpider(spider_config)

    # TODO: Get offers
    offers = asyncio.run(spider.run())

    # TODO: Return offers
    return offers
