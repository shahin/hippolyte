from scrapy import log
from scrapy.http import HtmlResponse
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_meta_refresh
from scrapy.exceptions import IgnoreRequest
from scrapy.conf import settings

from scrapy.selector import HtmlXPathSelector


class AmznMediaTypeMiddleware(object):
    """Ignore any item review pages that are not of the allowed media type."""

    def __init__(self):
        self.allowed_types = settings['AMZN_ALLOWED_MEDIA_TYPES']

    def process_response(self, request, response, spider):

        hxs = HtmlXPathSelector(response)
        try:
            media_type = hxs.select("//ul[@id='nav-subnav']/li[@class='nav-subnav-item nav-category-button']/a/text()").extract()[0]
            request.meta['MediaType'] = media_type.strip()

            if request.meta['MediaType'] in self.allowed_types:
                return response
            else:
                raise IgnoreRequest("Media type ("+request.meta['MediaType']+") not allowed.")
        except IndexError:
            raise IgnoreRequest("Media type not found.")
