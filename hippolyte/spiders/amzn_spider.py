from math import ceil
import urllib2

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy import log
from scrapy.conf import settings

from hippolyte.items import AmznReviewItem,AmznCustomerItem,AmznProductItem
from hippolyte.linkextractors import CustomerLinkExtractor,ItemReviewLinkExtractor

class AmznSpider(CrawlSpider):
    name = "amazon.com"
    allowed_domains = ["amazon.com"]

    start_urls = []

    rules = (
        # Extract the link to the next review page for this product
        # e.g. "http://www.amazon.com/Ride-Bob-Asleep-at-Wheel/product-reviews/B00000JWOJ/ref=cm_cr_pr_link_next_2?ie=UTF8&showViewpoints=0&pageNumber=2"
        Rule(SgmlLinkExtractor(allow=('ref=cm_cr_pr_top_link_next_')),callback='parse_reviews',follow=True),

        # Extract the link to the customer that wrote this item review
        Rule(CustomerLinkExtractor(allow=('ref=cm_cr_pr_auth_rev'),ignore_set=set()),callback='parse_first_customer_page',follow=True),

        # Extract the link to the item in this customer review
        Rule(ItemReviewLinkExtractor(allow=('ref=cm_cr-mr-title'),ignore_set=set()),callback='parse_reviews',follow=True),
    )

    def __init__(self, *a, **kw):
        super(AmznSpider, self).__init__(*a, **kw)
        self._compile_rules()
        #self.uid = kw['SPIDER_UID']
        self.uid = 'a1'

        '''
        try:
            isbns_url = kw['START_ASINS_URL']
            isbns_file = urllib2.urlopen(isbns_url)

            for isbn in isbns_file:
                url = "http://www.amazon.com/product-reviews/"+isbn.rstrip()+"/ref%3Ddp_top_cm_cr_acr_txt?ie=UTF8&showViewpoints=0"
                log.msg('Adding '+url+' to start_urls ...',level=log.DEBUG)
                self.start_urls.append(url)

        except urllib2.HTTPError,e:

            log.msg(start_urls_file_url + ' ' + str(e.code) + ' ' + e.msg,level=log.ERROR)
        '''
            


    def parse_start_url(self, response):
        # if the start_url is a product review url, make sure we parse it 
        if response.url.find('ref=cm_cr_pr_auth_rev') > 0:
            return self.parse_first_customer_page(response)
        elif response.url.find('product-reviews') > 0:
            return self.parse_reviews(response)
        else:
            return []

    def parse_first_customer_page(self,response):

        hxs = HtmlXPathSelector(response)

        # calculate the total number of pages of reviews for this customer
        num_reviews_text = hxs.select("//table/tr/td/table/tr/td/table/tr/td/div[@class='small']/text()").extract()[1]
        num_reviews = int(num_reviews_text[2:].split('\n')[0].replace(",",""))
        num_review_pages = int(ceil(float(num_reviews)/10))

        # get this CustomerId
        customer_id = response.url.split('/')[6]

        log.msg("CustomerId: "+customer_id+", Num reviews: "+str(num_reviews) \
                + ", Num pages: "+str(num_review_pages),level=log.INFO)

        amzn_customer = AmznCustomerItem()
        amzn_customer['CustomerId'] = customer_id
        amzn_customer['TotalReviews'] = int(num_reviews)
        amzn_customer['Depth'] = response.request.meta['amznDepth']
        yield amzn_customer

        for page_num in range(2,num_review_pages+1):
            url = "http://www.amazon.com/gp/cdp/member-reviews/" + customer_id \
                + "?ie=UTF8&display=public&sort_by=MostRecentReview&page=" + str(page_num)
            r = Request(url)
            yield r


    def parse_reviews(self, response):

        hxs = HtmlXPathSelector(response)
        parsed_reviews = []

        # store time retrieved
        date_retrieved = response.headers['Date']

        # get all review <td>s
        reviews = hxs.select("//table[@id='productReviews']/tr/td[1]/div[not(@class='CustomerPopover_load')]")
        _response_uses_more_tables = False

        # amazon provides two different types of HTML responses, one with
        # more tables instead of divs, so detect which response we got and
        # use the appropriate xpath expressions throughout
        if len(reviews) == 0:
            reviews = hxs.select("//table[@id='productReviews']/tr/td/table/tr/td[2]")
            _response_uses_more_tables = True
        
        ASIN = response.url.split('/')[4]
        if ASIN.find('-') > 0:
            ASIN = response.url.split('/')[5] 

        log.msg("Response uses more tables: " + str(_response_uses_more_tables),level=log.ERROR)

        # in each review <td>
        for review in reviews:

            parsed_review = AmznReviewItem()
            parsed_review['DateRetrieved'] = date_retrieved
            parsed_review['ASIN'] = ASIN

            # review ID is in the permalink
            if _response_uses_more_tables:
                permalink_url = review.select('div[last()]/table/tr/td[3]/div/div/span[3]/a/@href').extract()[0]
            else:
                permalink_url = review.select('div[last()]/div/div/div/span[3]/a/@href').extract()[0]

            parsed_review['ReviewId'] = permalink_url.split('/')[4]

            # rating is in the <span>s title, of the form: '1.0 out of 5 stars'
            rating_el = review.select('div/span/span/@title')
            parsed_review['Rating'] = float(rating_el.re('[^ ]+')[0])

            # reviewer ID is in a link to their profile
            if _response_uses_more_tables:
                profile_url = review.select('div[3]/table/tr/td[2]/a[1]/@href')
            else:
                profile_url = review.select('div/div/div/a[1]/@href')

            # some reviews genuinely do not list the reviewer ID
            try:
                parsed_review['CustomerId'] = profile_url.extract()[0].split('/')[6]
            except:
                parsed_review['CustomerId'] = None
            
            # date and summary are in the same <span>
            parsed_review['Date'] = review.select('div/span/nobr/text()').extract()[0]
            parsed_review['Summary'] = review.select('div/span/b/text()').extract()[0]


            parsed_reviews.append(parsed_review)


        num_reviews_parsed = len(parsed_reviews)
        log.msg("Parsed " + str(num_reviews_parsed) + " reviews for " + ASIN,level=log.DEBUG)

        if num_reviews_parsed > 0:

            # if this is an initial review page, yield the product data
            if response.url.find('dp_top_cm_cr_acr_txt') > 0:

                amzn_product = AmznProductItem()
                amzn_product['ASIN'] = ASIN
                amzn_product['Depth'] = response.request.meta['amznDepth']

                # get total reviews
                num_reviews = hxs.select("//span[@class='crAvgStars']/a/text()").extract()[0].split(' ')[0]
                amzn_product['TotalReviews'] = int(num_reviews.replace(",",""))
                amzn_product['MediaType'] = response.request.meta['MediaType']

                yield amzn_product

            # yield reviews
            for parsed_review in parsed_reviews:
                yield parsed_review

