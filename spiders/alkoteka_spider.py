import scrapy
import json
import time
from urllib.parse import urljoin, urlparse
import re


class AlkotekaSpider(scrapy.Spider):
    name = 'alkoteka'
    allowed_domains = ['alkoteka.com']
    
    #UUID
    KRASNODAR_UUID = '4a70f9e0-46ae-11e7-83ff-00155d026416'
    
    categories = [
        'slaboalkogolnye-napitki-2',
        'vino', 
        'krepkiy-alkogol'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36'
    }

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'ru,en;q=0.9',
        }
        
        #запросы для категорий
        for category_slug in self.categories:
            api_url = f'https://alkoteka.com/web-api/v1/product'
            params = {
                'city_uuid': self.KRASNODAR_UUID,
                'page': 1,
                'per_page': 20,
                'root_category_slug': category_slug
            }
            
            url_with_params = f"{api_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            yield scrapy.Request(
                url=url_with_params,
                callback=self.parse_api_response,
                headers=headers,
                meta={
                    'category_slug': category_slug,
                    'page': 1,
                    'headers': headers
                }
            )

    def parse_api_response(self, response):
        #парсинг
        category_slug = response.meta.get('category_slug')
        current_page = response.meta.get('page', 1)
        headers = response.meta.get('headers')
        
        self.logger.info(f"Парсинг API ответа для категории {category_slug}, страница {current_page}")
        
        try:
            data = json.loads(response.text)
            
            if not data.get('success'):
                self.logger.error(f"API вернул ошибку для {category_slug}: {data}")
                return
            
            products = data.get('results', [])
            if not products:
                self.logger.warning(f"Нет товаров в ответе API для {category_slug}")
                return
            
            self.logger.info(f"Найдено {len(products)} товаров на странице {current_page}")
            
            for product_data in products:
                item = self.create_item_from_api(product_data, category_slug)
                yield item
            
            meta = data.get('meta', {})
            current_page_meta = meta.get('current_page', current_page)
            has_more_pages = meta.get('has_more_pages', False)
            total_pages = meta.get('last_page', 1)
            
            self.logger.info(f"Пагинация: страница {current_page_meta}, есть еще: {has_more_pages}, всего страниц: {total_pages}")
            
            if has_more_pages and current_page < total_pages:
                next_page = current_page + 1
                self.logger.info(f"Переходим на страницу {next_page} для категории {category_slug}")
                
                api_url = f'https://alkoteka.com/web-api/v1/product'
                params = {
                    'city_uuid': self.KRASNODAR_UUID,
                    'page': next_page,
                    'per_page': 20,
                    'root_category_slug': category_slug
                }
                
                url_with_params = f"{api_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
                
                yield scrapy.Request(
                    url=url_with_params,
                    callback=self.parse_api_response,
                    headers=headers,
                    meta={
                        'category_slug': category_slug,
                        'page': next_page,
                        'headers': headers
                    }
                )
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON для {category_slug}: {e}")
            with open(f'debug_api_response_{category_slug}_{current_page}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)

    def create_item_from_api(self, product_data, category_slug):
        
        #структура товара
        item = {
            "timestamp": int(time.time()),
            "RPC": str(product_data.get('id', '')),
            "url": "",
            "title": "",
            "marketing_tags": [],
            "brand": "",
            "section": [category_slug],
            "price_data": {
                "current": 0.0,
                "original": 0.0,
                "sale_tag": ""
            },
            "stock": {
                "in_stock": False,
                "count": 0
            },
            "assets": {
                "main_image": "",
                "set_images": [],
                "view360": [],
                "video": []
            },
            "metadata": {
                "__description": ""
            },
            "variants": 0
        }
        
        item['RPC'] = str(product_data.get('id', product_data.get('uuid', '')))
        item['title'] = product_data.get('name', product_data.get('title', ''))
        item['brand'] = product_data.get('brand', product_data.get('manufacturer', ''))
        
        url = product_data.get('url', product_data.get('link', ''))
        if url:
            if not url.startswith('http'):
                item['url'] = urljoin('https://alkoteka.com', url)
            else:
                item['url'] = url
        
        description = product_data.get('description', product_data.get('short_description', ''))
        if description:
            item['metadata']['__description'] = description
        

        price_current = product_data.get('price', product_data.get('current_price', 0))
        price_original = product_data.get('original_price', product_data.get('old_price', price_current))
        
        if price_current:
            try:
                item['price_data']['current'] = float(price_current)
            except (ValueError, TypeError):
                pass
        
        if price_original:
            try:
                item['price_data']['original'] = float(price_original)
            except (ValueError, TypeError):
                pass
        
        if not item['price_data']['original'] and item['price_data']['current']:
            item['price_data']['original'] = item['price_data']['current']
        
        #расчет скидки
        if (item['price_data']['original'] > item['price_data']['current'] and 
            item['price_data']['current'] > 0):
            discount = (1 - item['price_data']['current'] / item['price_data']['original']) * 100
            item['price_data']['sale_tag'] = f"Скидка {discount:.0f}%"
        
        #наличие товара
        in_stock = product_data.get('in_stock', product_data.get('available', True))
        item['stock']['in_stock'] = bool(in_stock)
        
        stock_count = product_data.get('stock_count', product_data.get('quantity', 0))
        if stock_count:
            try:
                item['stock']['count'] = int(stock_count)
            except (ValueError, TypeError):
                pass
        
        main_image = product_data.get('image', product_data.get('photo', product_data.get('picture', '')))
        if main_image:
            if not main_image.startswith('http'):
                main_image = urljoin('https://alkoteka.com', main_image)
            item['assets']['main_image'] = main_image
            item['assets']['set_images'] = [main_image]
        
        images = product_data.get('images', product_data.get('photos', []))
        if images and isinstance(images, list):
            all_images = []
            for img in images:
                if isinstance(img, str):
                    img_url = img
                elif isinstance(img, dict):
                    img_url = img.get('url', img.get('src', ''))
                else:
                    continue
                
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = urljoin('https://alkoteka.com', img_url)
                    all_images.append(img_url)
            
            if all_images:
                item['assets']['set_images'] = all_images
                if not item['assets']['main_image']:
                    item['assets']['main_image'] = all_images[0]
        
        
        tags = []
        
        tag_fields = ['tags', 'labels', 'badges', 'promotions']
        for field in tag_fields:
            field_value = product_data.get(field, [])
            if isinstance(field_value, list):
                for tag in field_value:
                    if isinstance(tag, str):
                        tags.append(tag)
                    elif isinstance(tag, dict):
                        tag_name = tag.get('name', tag.get('title', ''))
                        if tag_name:
                            tags.append(tag_name)
        
        if item['price_data']['sale_tag']:
            tags.append('Скидка')
        
        if product_data.get('is_new'):
            tags.append('Новинка')
        if product_data.get('is_popular'):
            tags.append('Популярный')
        if product_data.get('is_recommended'):
            tags.append('Рекомендуем')
        
        item['marketing_tags'] = list(set(tags))
        
        
        variants = product_data.get('variants', product_data.get('options', []))
        if isinstance(variants, list):
            item['variants'] = len(variants)
        elif isinstance(variants, dict):
            item['variants'] = len(variants)
        
        exclude_fields = [
            'id', 'uuid', 'name', 'title', 'brand', 'manufacturer', 'url', 'link',
            'description', 'short_description', 'price', 'current_price', 'original_price',
            'old_price', 'in_stock', 'available', 'stock_count', 'quantity',
            'image', 'photo', 'picture', 'images', 'photos', 'tags', 'labels',
            'badges', 'promotions', 'variants', 'options', 'is_new', 'is_popular',
            'is_recommended'
        ]
        
        for key, value in product_data.items():
            if key not in exclude_fields and isinstance(value, (str, int, float, bool)):
                item['metadata'][key] = str(value)
        
        self.logger.debug(f"Создан товар: {item['title']} (ID: {item['RPC']}, Цена: {item['price_data']['current']})")
        
        return item