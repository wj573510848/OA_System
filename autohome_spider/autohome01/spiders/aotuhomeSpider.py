#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 10:30:37 2017

@author: wj
"""

import scrapy
import scrapy
from scrapy.http import Request
from autohome01.items import Autohome01Item

class aotuhomeSpider(scrapy.Spider):
    name = 'autohome01'
    start_urls = ["http://club.autohome.com.cn/bbs/forum-a-100024-1.html"]
    allowed_domains = []
    
    def parse(self,response): 
        a_s=response.xpath\
        ('//div[@id="subcontent"]/dl[@class="list_dl"]/dt/a[@class="a_topic"]/text()').extract()
        a_s_href=response.xpath\
        ('//div[@id="subcontent"]/dl[@class="list_dl"]/dt/a[@class="a_topic"]/@href').extract()
        for sub_href in a_s_href:
            yield Request(url="http://club.autohome.com.cn"+sub_href,callback=self.parse_details)
        next_url=response.xpath("//a[@class='afpage']/@href").extract()
        if next_url:
            yield Request(url="http://club.autohome.com.cn"+next_url[0],callback=self.parse)
    def parse_details(self,response):
        print(response.url)
        divs=response.xpath("//div[@class='w740']")
        for div in divs:
            q=div.xpath("div[1]/div[2]/p[2]/text()").extract()
            a=div.xpath("div[2]/text()").extract()
            if q and a:
                item=Autohome01Item()
                item['q']=q[0]
                item['a']=a[0]
                yield item
        next_url=response.xpath("//a[@class='afpage']/@href").extract()
        if next_url:
            yield Request(url="http://club.autohome.com.cn/bbs/"+next_url[0],callback=self.parse_details)
        
            
       