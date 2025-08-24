import random
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


class RegionMiddleware:
    def process_request(self, request, spider):
        #печеньки
        krasnodar_cookies = {
            'alkoteka_age_confirm': 'true',
            'alkoteka_locality': '{"uuid":"4a70f9e0-46ae-11e7-83ff-00155d026416","name":"Краснодар","slug":"krasnodar","longitude":"38.975996","latitude":"45.040216","accented":true}',
            'alkoteka_geo': 'true'
        }
        
        for key, value in krasnodar_cookies.items():
            request.cookies[key] = value
        
        return None


class RotateUserAgentMiddleware:
    
    def __init__(self):
        self.user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = ua
        return None


class ProxyMiddleware:
    
    def __init__(self):
        self.proxy_list = [
        ]
        self.proxy_index = 0

    def process_request(self, request, spider):
        if self.proxy_list:
            proxy = self.proxy_list[self.proxy_index]
            self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
            request.meta['proxy'] = proxy
            spider.logger.info(f'Используется прокси: {proxy}')
        return None


class CustomRetryMiddleware(RetryMiddleware):
    #повторные запросы
    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            spider.logger.warning(f'Повторный запрос для {request.url}: {reason}')
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            spider.logger.warning(f'Повторный запрос из-за исключения {request.url}: {exception}')
            return self._retry(request, exception, spider)