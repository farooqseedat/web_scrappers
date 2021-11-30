import json
import re
import scrapy

from scrapy.loader import ItemLoader
from web_crawlers.items import Product
from web_crawlers.items import ProductSKU
from web_crawlers.items import ProductLoader
from web_crawlers.items import ProductSKULoader


class GlamorousUkCrawl(scrapy.Spider):
    name = 'glamorous-uk-crawl'
    base_url_prefix = 'https://www.glamorous.com/collections'
    start_urls = [
        f"{base_url_prefix}/new-in#",
        f"{base_url_prefix}/clothing#"
        f"{base_url_prefix}/mystery-bags#",
        f"{base_url_prefix}/dresses#",
        f"{base_url_prefix}/pretty-in-peach#",
        f"{base_url_prefix}/shoes#",
        f"{base_url_prefix}/accessories#",
        f"{base_url_prefix}/sale#"
    ]

    def parse(self, response):
        product_urls = response.xpath(
            "//div[contains(@id,'bc-sf-filter-products')]//a/@href").getall()
        for prd_url in product_urls:
            yield response.follow(prd_url, self.parse_product)
        next_page = response.xpath(
            "//link[contains(@rel,'next')]/@href").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_product(self,response):
        loader = ProductLoader(response=response)
        image_urls = response.xpath(
            "//div[contains(@id,'thumbnails')]//div/img/@src"
        ).getall()
        image_urls = ["https:" + url for url in image_urls]
        json_str = response.xpath(
            "//script[contains(@type,'text/javascript')]/text()").re(
            "productJson:(.*),")
        product_hash = ""
        price = ""
        if(json_str):
            parsed_json = json.loads(json_str[0])
            price = parsed_json.get("price")
            product_hash = parsed_json.get("id")

        values_data = {
            "url_original": response.url,
            "brand": "Glamorous",
            "market": "UK",
            "gender": "women",
            "retailer": "glamorous-uk",
            "category": response.url.split('/')[4],
            "spider_name": self.name,
            "image_urls": image_urls,
            "product_hash":product_hash,
            "price":price,
            "skus": self.get_skus(response)
        }

        xpath_data = {
            "name": response.xpath("//h2[has-class('name')]").get(),
            "retailer_sku": response.xpath(
                "//p[contains(@id,'sku')]/span[contains(@itemprop,'sku')]/text()").get(),
            "category": response.xpath("//h2[has-class('name')]").get(),
            "url": response.xpath(
                "//link[contains(@rel,'canonical')]/@href").get(),
            "description": response.xpath(
                "//div[contains(@id,'tab-description')]//p").get(),
            "currency": response.xpath(
                "//meta[contains(@property,'og:price:currency')]/@content").get()
        }
        data = {**values_data, **xpath_data}

        for key, value in data.items():
                loader.add_value(key, value)

        yield loader.load_item()

    def get_skus(self,response):
        script = response.xpath(
            "//script[contains(@type,'text/javascript')]/text()").get()
        json_str = re.findall('"variants":(.*?}])', script)
        if not json_str:
            return
        parsed_json = json.loads(json_str[0])
        product_variants = []
        for prdVariants in parsed_json:
            loader = ProductSKULoader(response=response)
            values_data = {
                "price": prdVariants.get("price"),
                "color":"",
                "sku_id": prdVariants.get("id"),
                "size": prdVariants.get("title"),
                "out_of_stock": False if prdVariants.get("available") else True,
                "currency": 'GBP'
            }
            for key, value in values_data.items():
                loader.add_value(key, value)

            yield loader.load_item()

