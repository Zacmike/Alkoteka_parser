import json
from itemadapter import ItemAdapter


class AlkotekaPipeline:
    #обработка и валидация данных
    
    def process_item(self, item, spider):
        self._validate_required_fields(item)
        
        self._clean_data(item)
        
        self._convert_types(item)
        
        return item
    
    def _validate_required_fields(self, item):
        required_fields = [
            'timestamp', 'RPC', 'url', 'title', 'brand', 'section', 'price_data', 'stock', 'metadata', 'variants'
        ]
        
        for field in required_fields:
            if field not in item:
                if item[field] == 'variants':
                    item[field] = 1
                elif field == 'timestamp':
                    import time
                    item[field] = int(time.time())
                else:
                    item[field] = self._get_default_value(field)
                    
    def _get_default_value(self, field):
        defaults = {
            'RPC': 'unknown',
            'url': '',
            'title': 'Неизвестный товар',
            'marketing_tags': [],
            'brand': 'Не указан',
            'section': [],
            'price_data': {'current': 0.0, 'original': 0.0, 'sale_tag': ''},
            'stock': {'in_stock': False, 'count': 0},
            'assets': {'main_image': '', 'set_images': [], 'view360': [], 'video': []},
            'metadata': {'__description': ''},
            'variants': 1
        }
        return defaults.get(field, '')
    
    
    def _clean_data(self, item):
        if 'title' in item and isinstance(item['title'], str):
            item['title'] = item['title'].strip()
            
        if 'brand' in item and isinstance(item['brand'], str):
            item['brand'] = item['brand'].strip()
            
        if '__description' in item.get('metadata', {}):
            desc = item['metadata']['__description']
            if isinstance(desc, str):
                item['metadata']['__description'] = desc.strip()
                
    def _convert_types(self, item):
        if 'price_data' in item:
            price_data = item['price_data']
            for k in ['current', 'original']:
                if k in price_data:
                    if isinstance(price_data[k], str):
                        price_str = price_data[k].replace(' ', '').replace('₽', '').replace(',', '.')
                        
                        try:
                            price_data[k] = float(price_str)
                        except (ValueError, TypeError):
                            price_data[k] = 0.0
                            
        if 'stock' in item and 'count' in item['stock']:
            if isinstance(item['stock']['count'], str):
                try:
                    item['stock']['count'] = int(item['stock']['count'])
                except (ValueError, TypeError):
                    item['stock']['count'] = 0
                    
class JsonWritePipeline:
    #запись в JSON
    
    def open_spider(self, spider):
        self.file = open('result.json', 'w', encoding='utf8')
        self.file.write('[\n')
        self.first_item = True
        
    def close_spider(self, spider):
        self.file.write('[\n')
        self.file.close()
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False, indent=2)
        if not self.first_item:
            line = ',\n' + line
            
        else:
            self.first_item = False
        self.file.write(line)
        return item