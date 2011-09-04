# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy import log
from scrapy import signals
from scrapy.conf import settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy.contrib.exporter import JsonLinesItemExporter
from scrapy.contrib.exporter import CsvItemExporter

from hippolyte.items import AmznReviewItem,AmznCustomerItem,AmznProductItem

class AmznJsonPipeline(object):

    def __init__(self):

        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_opened(self,spider):

        reviews_file_name = settings.get('OUTPUT_PATH')+'/reviews'+spider.uid+'.json'
        self.reviews_file = open(reviews_file_name,'w')

        products_file_name = settings.get('OUTPUT_PATH')+'/products'+spider.uid+'.json'
        self.products_file = open(products_file_name,'w')

        customers_file_name = settings.get('OUTPUT_PATH')+'/customers'+spider.uid+'.json'
        self.customers_file = open(customers_file_name,'w')

        # set up a separate exporter for each item type
        self.exporters = {}
        self.exporters['AmznReviewItem'] = JsonLinesItemExporter(
            self.reviews_file)
        self.exporters['AmznProductItem'] = JsonLinesItemExporter(
            self.products_file)
        self.exporters['AmznCustomerItem'] = JsonLinesItemExporter(
            self.customers_file)

    def spider_closed(self,spider):
        self.reviews_file.close()
        self.products_file.close()
        self.customers_file.close()
        log.msg('Closed files.',level=log.DEBUG)

    def process_item(self, item, spider):
        '''
        Write each item to a different JSON file depending on it's type.
        '''

        self.exporters[item.__class__.__name__].export_item(item)

        return item


class AmznCsvPipeline(object):

    def __init__(self):

        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_opened(self,spider):

        reviews_file_name = settings.get('OUTPUT_PATH')+'/reviews'+spider.uid+'.csv'
        self.reviews_file = open(reviews_file_name,'w')

        products_file_name = settings.get('OUTPUT_PATH')+'/products'+spider.uid+'.csv'
        self.products_file = open(products_file_name,'w')

        customers_file_name = settings.get('OUTPUT_PATH')+'/customers'+spider.uid+'.csv'
        self.customers_file = open(customers_file_name,'w')

        # set up a separate exporter for each item type
        self.exporters = {}
        self.exporters['AmznReviewItem'] = CsvItemExporter(
            self.reviews_file)
        self.exporters['AmznProductItem'] = CsvItemExporter(
            self.products_file)
        self.exporters['AmznCustomerItem'] = CsvItemExporter(
            self.customers_file)

    def spider_closed(self,spider):
        self.reviews_file.close()
        self.products_file.close()
        self.customers_file.close()
        log.msg('Closed files.',level=log.DEBUG)

    def process_item(self, item, spider):
        '''
        Write each item to a different file depending on it's type.
        '''

        self.exporters[item.__class__.__name__].export_item(item)

        return item
