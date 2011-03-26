"""
AmznDepth Spider Middleware

"""

from scrapy import log
from scrapy.http import Request

class AmznDepthMiddleware(object):

    def __init__(self, max_amzn_depth, stats=None):
        self.max_amzn_depth = max_amzn_depth
        self.stats = stats
        if self.stats and self.max_amzn_depth:
            stats.set_value('envinfo/request_amzndepth_limit', max_amzn_depth)

    @classmethod
    def from_settings(cls, settings):
        max_amzn_depth = settings.getint('AMZN_DEPTH_LIMIT')
        usestats = settings.getbool('AMZN_DEPTH_STATS')
        if usestats:
            from scrapy.stats import stats
        else:
            stats = None
        return cls(max_amzn_depth, stats)


    def process_spider_output(self, response, result, spider):

        def _filter(request):
            if isinstance(request, Request):

                # set page descriptors 
                if request.url.find('ref=cm_cr_pr_link_next_') > 0:
                    request.meta['AmznPageType'] = 'ItemReviewPage'

                # increment our depth only when we reach a customer's first review page
                if request.url.find('cm_cr_pr_auth_rev') > 0:
                    amzn_depth = response.request.meta['amznDepth'] + 1
                else:
                    amzn_depth = response.request.meta['amznDepth']

                request.meta['amznDepth'] = amzn_depth

                # ignore any requests with depth greater than or equal to the max
                if self.max_amzn_depth and amzn_depth >= self.max_amzn_depth:
                    log.msg("Ignoring link (depth > %d): %s " % (self.max_amzn_depth, request.url), \
                        level=log.DEBUG, spider=spider)
                    return False

                elif self.stats:
                    self.stats.inc_value('request_amzndepth_count/%s' % amzn_depth, spider=spider)
                    if amzn_depth > self.stats.get_value('request_amzndepth_max', 0, spider=spider):
                        self.stats.set_value('request_amzndepth_max', amzn_depth, spider=spider)

            return True

        # base case (depth=0)
        if self.stats and 'amznDepth' not in response.request.meta: 
            response.request.meta['amznDepth'] = 0
            self.stats.inc_value('request_amzndepth_count/0', spider=spider)

        return (r for r in result or () if _filter(r))
