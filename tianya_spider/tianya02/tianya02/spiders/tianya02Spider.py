#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 09:32:48 2017

@author: wj
"""

import scrapy
from scrapy import Request
import re
from tianya02.items import Tianya02Item
from tianya02.items import IdItem

class tianyaSpider(scrapy.Spider):
    name = 'tianya02'
    start_urls = ["http://bbs.tianya.cn/list-funinfo-1.shtml"]
    allowed_domains = []
    html_ID=[]
    
    def parse(self, response):
        if 'partial' in response.flags:
            print(response.headers)
            
        id_item=IdItem()
        trs=response.xpath("//table/tbody/tr")
        for tr in trs:
            sub_href=tr.xpath("td[1]/a/@href").extract()
            sub_huifu=tr.xpath('td[4]/text()').extract()
            if not (sub_huifu and sub_href):
                continue
            if int(sub_huifu[0])<100:
                continue
            if not("funinfo" in sub_href[0].split("-")):
                continue
            pa="-([0-9]+)-"
            href_id=re.findall(pa,sub_href[0])[0]
            if href_id in self.html_ID:
                continue
            else:
                self.html_ID.append(href_id)
                id_item['ID']=href_id
                yield id_item

            if len(self.html_ID)%1000==0:
                print("Crawl num of ID: %s" % len(self.html_ID))
            yield Request(url="http://bbs.tianya.cn"+sub_href[0],callback=self.parse_details)
            
        next_url=response.xpath("//div[@class='links']/a[@rel='nofollow']/@href").extract()
        if next_url:
            yield Request(url="http://bbs.tianya.cn"+next_url[0],callback=self.parse)

    def parse_details(self,response):
        divs=response.xpath("//div[@class='bbs-content']")
        items=Tianya02Item()
        for div in divs:
            cons=div.xpath('text()').extract()
            if len(cons)<4:
                continue
            if list(set(cons[-2].strip()))==['—'] or list(set(cons[-2].strip()))==['-'] or list(set(cons[-2].strip()))==['=']:
                q=cons[-3].strip()
                a=cons[-1].strip()
                if q and a:
                    items['q']=q
                    items['a']=a
                    yield items
            elif list(set(cons[-3].strip()))==['—'] or list(set(cons[-3].strip()))==['-'] or list(set(cons[-3].strip()))==['=']:
                q=cons[-4].strip()
                a=cons[-2].strip()
                if q and a:
                    items['q']=q
                    items['a']=a
                    yield items            
        next_url=response.xpath("//a[@class='js-keyboard-next']/@href").extract()
        if next_url:
            yield Request(url='http://bbs.tianya.cn'+next_url[0],callback=self.parse_details)
            
                
            

        

        
        
        
        
        