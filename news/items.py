# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    url = scrapy.Field()
    brief =scrapy.Field()
    title = scrapy.Field()
    reading_count = scrapy.Field()
    publication_time =scrapy.Field()
    category =scrapy.Field()
    article_content = scrapy.Field()
    publication_press =scrapy.Field()
    cover =scrapy.Field()
    reading_num =scrapy.Field()
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
