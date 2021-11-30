import scrapy
from scrapy.loader import ItemLoader
from web_crawlers.items import Product
from web_crawlers.items import ProductSKU
from web_crawlers.items import ProductLoader
from web_crawlers.items import ProductSKULoader


class Europe361Crawl(scrapy.Spider):
    name = "europe361_crawl"
    base_url = "https://store.361europe.com"
    start_urls = ["https://store.361europe.com/shop"]

    def parse(self, response):
        product_urls = response.xpath(
            "//div[contains(@id,'products')]/div/a/@href").getall()
        for prd_url in product_urls:
            yield response.follow(prd_url, self.parse_product)
        next_page = response.xpath(
            "//link[contains(@rel,'next')]/@href").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        loader = ProductLoader(response=response)
        categories = response.xpath(
            "//div[contains(@id,'breadcrumbs')]//div/a/@title").getall()
        values_date = {
            "gender": "unisex",
            "market": "Europe",
            "retailer": "Store 361Europe",
            "retailer_sku": "",
            "brand": "361",
            "spider_name": self.name,
            "url_original": response.url,
            "currency": "Euro"
        }
        if len(categories)>2:
            loader.replace_value("gender", categories[1])
            loader.add_value("category", categories[2:])

        xpath_data = {
            "name": "//h1[contains(@itemprop,'name')]/text()",
            "product_hash":response.xpath(
                "//input[contains(@name,'product_id')]/@value").get(),
            "description":response.xpath(
                "//div[contains(@id,'description')]").get(),
            "url":response.xpath(
                "//link[contains(@rel,'canonical')]/@href").get(),
            "price":response.xpath(
                "//meta[contains(@itemprop,'price')]/@content").get()
        }

        data = {**values_date, **xpath_data}
        for key, value in data.items():
            loader.add_value(key, value)
        meta = {}
        urls = response.xpath(
            "//div[contains(@id,'colors')]/a/@href").getall()
        colors =  response.xpath(
            "//div[contains(@id,'colors')]/a/@title").getall()

        if colors:
            meta["color"] = colors.pop()
        meta["colors"] = colors
        meta["loader"] = loader.load_item()

        if urls:
            url = urls.pop()
            meta["urls"] = urls
            yield response.follow(url=url, callback=self.get_product_variant,
                                  meta=meta)
        else:
            response.meta = meta
            self.get_product_variant(response)

    def get_product_variant(self, response):
        product_loader = ProductLoader(item=response.meta.get("loader"),
        response=response)
        price = response.xpath(
            "//meta[contains(@itemprop,'price')]/@content").get()
        skus = response.xpath("//div[contains(@id,'sizes')]/div")
        image_urls = response.xpath(
            "//div[contains(@id,'thumbs')]/a/@href").getall()
        image_urls = [f"{self.base_url}{url}" for url in image_urls]
        product_loader.add_value("image_urls", image_urls)
        product_loader.add_value("skus",self.get_skus(response))

        if response.meta.get("urls"):
            url = response.meta.get("urls").pop()
            colors = response.meta.get("colors")
            color = colors and colors.pop()
            response.meta["loader"] = product_loader.load_item()
            response.meta["color"] = color
            yield response.follow(url=url, callback=self.get_product_variant,
                                  meta=response.meta)
        else:
            yield product_loader.load_item()

    def get_skus(self,response):
        price = response.xpath(
            "//meta[contains(@itemprop,'price')]/@content").get()
        skus = response.xpath("//div[contains(@id,'sizes')]/div")
        color = response.meta.get("color")

        for sku in skus:
            loader = ProductSKULoader(response=response)
            values_data = {
                "price": price,
                "currency": "Euro",
                "color": color,
                "sku_id": sku.xpath("@data-id").get(),
                "size": sku.xpath("text()").get(),
                "out_of_stock": True if sku.css('.sold') else False
            }
            
            for key, value in values_data.items():
                loader.add_value(key, value)

            yield loader.load_item()
