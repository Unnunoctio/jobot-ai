import asyncio

from spider import GetOnBoardSpider


def handler(event, context):
    # TODO: Get spider config
    spider_config = event.get("config", {})
    spider = GetOnBoardSpider(spider_config)

    # TODO: Get offers
    offers = asyncio.run(spider.run())

    # TODO: Return new offers
    return offers
