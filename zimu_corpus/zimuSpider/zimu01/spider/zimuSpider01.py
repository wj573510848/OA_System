# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 11:40:24 2017

@author: Aoshuo-wj
"""

import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from zimu01.items import Zimu01Item

class zimuSpider(scrapy.Spider):
    name = "zimu"
    allowed_domains = ["zimuku.net"]
    start_urls = ["http://www.zimuku.net/search?q=&t=onlyst&ad=1&p=1"]
    
    #start_urls = ["http://www.zimuku.net/shooter/57265.html"]
    
    #得到能够搜索的总页数，并且生成这些网址。
    def parse(self,response):
        selector=Selector(response)
        nextUrl=selector.xpath("//a[@class='end']/text()").extract()[0]
        print(nextUrl)
        for i in range(1,int(nextUrl)+1):
            yield Request(url="http://www.zimuku.net/search?q=&t=onlyst&ad=1&p=%s" % i,callback=self.parse_info)
    #进入每一页，得到每一项的url。
    def parse_info(self,response):
        #print(response.url)
        selector=Selector(response)
        divs=selector.xpath("//div[@class='box clearfix']/div[@class='persub clearfix']")
        for div in divs:
            url=div.xpath("h1/a/@href").extract()
            geshi=div.xpath("p[1]/span[2]/text()").extract()
            if(url and geshi):
                geshi=geshi[0]
                if(("Subrip" in geshi) or ('SSA' in geshi) or ("ASS" in geshi) or ("SRT" in geshi)):
                    yield Request(url="http://www.zimuku.net%s" % url[0],callback=self.parse_fileUrl)
    #进入每一项，得到下载页的url。
    def parse_fileUrl(self,response):
        #print(response.url)
        selector=Selector(response)
        downloadUrl=selector.xpath("//li[@class='li dlsub']/div/a[1]/@href").extract()
        if downloadUrl:
            yield Request(url=downloadUrl[0],callback=self.parse_file)
    #得到下载数据。
    def parse_file(self,response):
        body=response.body
        items=Zimu01Item()
        items['body']=body
        return items
            
            
                
    '''
    #http://www.zimuku.net/shooter/57265.html test
    def parse(self,response):
        print("******%s******" % response.url)
        selector=Selector(response)
        downloadUrl=selector.xpath("//li[@class='li dlsub']/div/a[1]/@href").extract()[0]
        yield Request(url=downloadUrl,callback=self.parse_download,dont_filter=True)
    
    def parse_download(self,response):
        body=response.body
        with open("results/test1",'wb') as f:
            f.write(body)
    '''