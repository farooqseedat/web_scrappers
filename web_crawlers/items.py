import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join, Identity
from w3lib.html import remove_tags


def format_links(source):
    return source.split(',')


def clean_text(text):
    lines = text.split('\n')
    cleaned_text = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            cleaned_text.append(stripped_line)
    return cleaned_text


def convert_to_int(text):
    if isinstance(text, int):
        return text
    num = ""
    for character in text:
        if character.isdigit():
            num += character
    return int(num)


class ProductSKU(scrapy.Item):
    price = scrapy.Field()
    color = scrapy.Field()
    currency = scrapy.Field()
    size = scrapy.Field()
    out_of_stock = scrapy.Field()
    sku_id = scrapy.Field()


class Product(scrapy.Item):
    gender = scrapy.Field()
    currency = scrapy.Field()
    market = scrapy.Field()
    retailer = scrapy.Field()
    retailer_sku = scrapy.Field()
    category = scrapy.Field()
    brand = scrapy.Field()
    url = scrapy.Field()
    url_original = scrapy.Field()
    product_hash = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    image_urls = scrapy.Field()
    skus = scrapy.Field()
    price = scrapy.Field()
    spider_name = scrapy.Field()


class ProductLoader(ItemLoader):
    default_item_class = Product
    default_output_processor = Join(',')
    default_input_processor = MapCompose(remove_tags)
    image_urls_in = MapCompose(format_links)
    image_urls_out = Identity()
    price_in = MapCompose(convert_to_int)
    price_out = TakeFirst()
    skus_in = MapCompose(serializer=ProductSKU)
    skus_out = Identity()
    product_hash_in = MapCompose(str)
    product_hash_out = TakeFirst()
    description_in = MapCompose(remove_tags, clean_text)
    description_out = Identity()
    category_out = Identity()


class ProductSKULoader(ItemLoader):
    default_item_class = ProductSKU
    default_output_processor = Join(',')
    default_input_processor = MapCompose(remove_tags)
    price_in = MapCompose(convert_to_int)
    price_out = TakeFirst()
    out_of_stock_in = MapCompose(str)
    sku_id_in = MapCompose(str)
