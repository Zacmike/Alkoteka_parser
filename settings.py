# Scrapy settings for alkoteka_parser project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "alkoteka_parser"

SPIDER_MODULES = ["alkoteka_parser.spiders"]
NEWSPIDER_MODULE = "alkoteka_parser.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "alkoteka_parser (+http://www.yourdomain.com)"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36'
# Obey robots.txt rules
ROBOTSTXT_OBEY = False
COOKIES_ENABLED = True
# Concurrency and throttling settings
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 3
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

DEFAULT_REQUEST_HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'ru,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Sec-Ch-Ua': '"Chromium";v="136", "YaBrowser";v="25.6", "Not.A/Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}
# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "alkoteka_parser.middlewares.AlkotekaParserSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "alkoteka_parser.middlewares.AlkotekaParserDownloaderMiddleware": 543,
#}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.offsite.OffsiteMiddleware': 500,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 510,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 520,
    'alkoteka_parser.middlewares.ProxyMiddleware': 530,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 540,
    'alkoteka_parser.middlewares.RegionMiddleware': 545,
    'alkoteka_parser.middlewares.RotateUserAgentMiddleware': 550,
    'alkoteka_parser.middlewares.CustomRetryMiddleware': 560,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 570,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 580,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 590,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 600,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 610,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
}

RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "alkoteka_parser.pipelines.AlkotekaParserPipeline": 300,
#}

ITEM_PIPELINES = {
    'alkoteka_parser.pipelines.AlkotekaPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REGION_CITY = 'krasnodar'

PROXY_LIST = [
    'http://95.31.35.210:3629',
    'http://85.175.144.214:8080',
    'http://85.175.219.236:1080'
]
USER_PROXY = False

LOG_LEVEL = 'INFO'
FEED_EXPORT_ENCODING = "utf-8"
FEEDS = {
    'result.json': {
        'format': 'json',
        'encoding': 'utf8',
        'overwrite': True,
        'indent': 4,
    }
}
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# Дополнительные настройки для стабильной работы
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Настройки для обхода блокировок
DOWNLOAD_TIMEOUT = 30
RANDOMIZE_DOWNLOAD_DELAY = True
