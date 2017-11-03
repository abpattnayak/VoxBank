# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VoxillobankingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    CountryCode = scrapy.Field()
    ProviderName = scrapy.Field()
    ProductName = scrapy.Field()
    LoanType = scrapy.Field()
    Period = scrapy.Field()
    Rate = scrapy.Field()
    CoverageStart = scrapy.Field()
    CoverageEnd = scrapy.Field()
    CheckDate = scrapy.Field()
    ValidSince = scrapy.Field()
    NHG = scrapy.Field()
