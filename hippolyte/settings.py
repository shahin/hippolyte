# Scrapy settings for hippolyte project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'hippolyte'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['hippolyte.spiders']
NEWSPIDER_MODULE = 'hippolyte.spiders'
DEFAULT_ITEM_CLASS = 'hippolyte.items.HippolyteItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

