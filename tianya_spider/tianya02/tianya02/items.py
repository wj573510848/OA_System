# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Tianya02Item(scrapy.Item):
    # define the fields for your item here like:
    q = scrapy.Field()
    a = scrapy.Field()
    
class IdItem(scrapy.Item):
    # define the fields for your item here like:
    ID= scrapy.Field()

