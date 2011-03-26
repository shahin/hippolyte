# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class AmznReviewItem(Item):

    ReviewId = Field()
    ASIN = Field()
    CustomerId = Field()
    Rating = Field()
    Date = Field()
    Summary = Field()
    DateRetrieved = Field()


class AmznCustomerItem(Item):

    CustomerId = Field()
    TotalReviews = Field()
    Depth = Field()

class AmznProductItem(Item):

    ASIN = Field()
    MediaType = Field()
    TotalReviews = Field()
    Depth = Field()
