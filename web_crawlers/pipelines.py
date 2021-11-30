from itemadapter import ItemAdapter
import requests
import json
import logging

logger = logging.getLogger(__name__)


def map_list_data(data, field_name):
    mapped_data = []
    for each in data or []:
        mapped_data.append({field_name: each})
    return mapped_data


class ProductPipeline:
    def process_item(self, item, spider):
        url = 'http://127.0.0.1:8000/products/add'
        item['image_urls'] = map_list_data(item.get('image_urls'), 'url')
        item['category'] = map_list_data(item.get('category'), 'category')
        item['description'] = map_list_data(item.get('description'),
                                            'description')
        adapter = ItemAdapter(item)
        json_string = json.dumps(adapter.asdict())
        json_serialized_obj = json.loads(json_string)
        status = requests.post(url, json=json_serialized_obj)
        if status.status_code != 201:
            logger.info(json_serialized_obj['url'])
            logger.info(status.json())
