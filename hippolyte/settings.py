# Scrapy settings for amzn project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
# Or you can copy and paste them from where they're defined in Scrapy:
# 
#     scrapy/conf/default_settings.py
#

BOT_NAME = 'hippolyte'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['hippolyte.spiders']
NEWSPIDER_MODULE = 'hippolyte.spiders'
DEFAULT_ITEM_CLASS = 'hippolyte.items.AmznReviewItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = ['hippolyte.pipelines.AmznCsvPipeline']

LOG_LEVEL = 'INFO'

AMZN_DEPTH_STATS = 1
AMZN_DEPTH_LIMIT = 1
SPIDER_MIDDLEWARES = {
    "hippolyte.spidermiddlewares.AmznDepthMiddleware" : 950,
}


AMZN_ALLOWED_MEDIA_TYPES = ["Books","Your Amazon.com"]
DOWNLOADER_MIDDLEWARES = {
    "hippolyte.downloadermiddlewares.AmznMediaTypeMiddleware" : 25,
}


try:
    from local_settings import *
except ImportError:
    pass
