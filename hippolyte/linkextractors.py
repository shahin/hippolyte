"""
Link extractors for customer review pages and item review pages.
"""

import re

from scrapy.selector import HtmlXPathSelector
from scrapy.link import Link
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.python import FixedSGMLParser, unique as unique_list, str_to_unicode
from scrapy.utils.url import safe_url_string, urljoin_rfc, canonicalize_url, url_is_from_any_domain
from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor,BaseSgmlLinkExtractor

_re_type = type(re.compile("", 0))

_matches = lambda url, regexs: any((r.search(url) for r in regexs))
_is_valid_url = lambda url: url.split('://', 1)[0] in set(['http', 'https', 'file'])

class NoRepeatLinkExtractor(SgmlLinkExtractor):

    def __init__(self, allow=(), deny=(), allow_domains=(), deny_domains=(), restrict_xpaths=(), 
                 tags=('a', 'area'), attrs=('href'), canonicalize=True, unique=True, process_value=None,
                 ignore_set=set()):

        self.ignore_set = ignore_set

        SgmlLinkExtractor.__init__(self, allow=allow, deny=deny,
                allow_domains=allow_domains, deny_domains=deny_domains,
                restrict_xpaths=restrict_xpaths, tags=tags, attrs=attrs,
                canonicalize=canonicalize, unique=unique, process_value=process_value)


    def _ignore_identifier(self,identifier):

        if identifier in self.ignore_set:
            return True
        else:
            self.ignore_set.add(identifier)
            return False

            
class CustomerLinkExtractor(NoRepeatLinkExtractor):

    def _process_links(self, links):
        links = [link for link in links if _is_valid_url(link.url)]

        if self.allow_res:
            links = [link for link in links if _matches(link.url, self.allow_res)]
        if self.deny_res:
            links = [link for link in links if not _matches(link.url, self.deny_res)]
        if self.allow_domains:
            links = [link for link in links if url_is_from_any_domain(link.url, self.allow_domains)]
        if self.deny_domains:
            links = [link for link in links if not url_is_from_any_domain(link.url, self.deny_domains)]

        new_links = []
        for link in links:
            CustomerId = link.url.split('/')[6]
            if not self._ignore_identifier(CustomerId):
                log.msg("Found CustomerId: "+CustomerId,level=log.DEBUG)
                new_links.append(link)

        links = new_links

        if self.canonicalize:
            for link in links:
                link.url = canonicalize_url(link.url)

        links = BaseSgmlLinkExtractor._process_links(self, links)
        return links


class ItemReviewLinkExtractor(NoRepeatLinkExtractor):

    def _process_links(self, links):
        links = [link for link in links if _is_valid_url(link.url)]

        if self.allow_res:
            links = [link for link in links if _matches(link.url, self.allow_res)]
        if self.deny_res:
            links = [link for link in links if not _matches(link.url, self.deny_res)]
        if self.allow_domains:
            links = [link for link in links if url_is_from_any_domain(link.url, self.allow_domains)]
        if self.deny_domains:
            links = [link for link in links if not url_is_from_any_domain(link.url, self.deny_domains)]

        new_links = []
        for link in links:
            ASIN = link.url.split('/')[5]
            if not self._ignore_identifier(ASIN):
                log.msg("Found ASIN: "+ASIN,level=log.DEBUG)
                link.url = "http://www.amazon.com/product-reviews/"+ASIN+"/ref%3Ddp_top_cm_cr_acr_txt?ie=UTF8&showViewpoints=0"
                new_links.append(link)

        links = new_links

        if self.canonicalize:
            for link in links:
                link.url = canonicalize_url(link.url)

        links = BaseSgmlLinkExtractor._process_links(self, links)
        return links


