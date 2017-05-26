#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 25 13:59:43 2017

@author: wj
"""

#start_requests:初始化爬虫网址。
#parse
#1.检查当前ID，去重，yield Request(url=response.url,callback=self.parse_weibo)去爬取详细的微博信息。
#2.获得当前ID的粉丝及关注网址，在下一个函数中获得粉丝及关注的ID。
#parse_list:获取关注及粉丝的ID。
#parse_weibo:获取一个ID的微博列表，获得回复数量大于2的链接。
#parse_details:爬取微博正文及评论。

import scrapy
from sina01.weiboID import weiboID
import re
from scrapy.http import Request
from sina01.items import Sina01Item
import redis
import random

class sinaSpider(scrapy.Spider):
    name='SinaSpider'
    start_urls = list(set(weiboID))#随机初始化新浪微博ID。爬虫初始网址构成为"https://weibo.cn/"+ID
    #start_urls=["https://weibo.cn/2714101054"]
    allowed_domains = []
    server_redis=redis.Redis()
    key_redis="id"
    key_processed_redis='id_processed'
    
    
    def start_requests(self):
        random.shuffle(self.start_urls)
        for url in self.start_urls:
            yield Request(url="https://weibo.cn/"+str(url),callback=self.parse)
    
    #get fans and follows list.
    def parse(self,response):
        #yield Request(url="https://weibo.cn/comment/F4Cvn1odB?&page=1",callback=self.parse_details)
        #yield Request(url=response.url,callback=self.parse_weibo)
        weibo_ID=re.findall("cn/(\d+)",response.url)[0]
	#去重
        if weibo_ID.isdigit():
            isExist = self.server_redis.getbit(self.key_processed_redis+str(int(int(weibo_ID)/4000000000)), int(weibo_ID)%4000000000)
            if isExist != 1:
                self.server_redis.setbit(self.key_processed_redis+str(int(int(weibo_ID)/4000000000)), int(weibo_ID)%4000000000, 1)
                yield Request(url=response.url,callback=self.parse_weibo)
            else:
                print("weiboID:%s is already processed!" % weibo_ID)
                
	#粉丝及关注者列表        
        fans=response.xpath("//div[@class='tip2']/a[contains(text(),'粉丝')]/text()").extract()
        if fans:
            fans_num=fans[0].split("[")[-1].split("]")[-2]
            if fans_num.isdigit() and int(fans_num)>1:
                href=response.xpath("//div[@class='tip2']/a[contains(text(),'粉丝')]/@href").extract()
                if href:
                    href=href[0]
                    yield Request(url="https://weibo.cn"+href,callback=self.parse_list)
        follows=response.xpath("//div[@class='tip2']/a[contains(text(),'关注')]/text()").extract()
        if follows:
            follows_num=follows[0].split("[")[-1].split("]")[-2]
            if follows_num.isdigit() and int(follows_num)>1:
                href=response.xpath("//div[@class='tip2']/a[contains(text(),'关注')]/@href").extract()
                if href:
                    href=href[0]
                    yield Request(url="https://weibo.cn"+href,callback=self.parse_list)
        
            
    def parse_list(self,response):
        
        href_list=response.xpath('//a[text()="关注他" or text()="关注她"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(href_list), re.S)
        
        #print("UIDS")
        #print(uids[0])
        #去重
        for uid in uids:
            if uid.isdigit():
                isExist = self.server_redis.getbit(self.key_redis+str(int(int(uid)/4000000000)), int(uid)%4000000000)
                if isExist != 1:
                    self.server_redis.setbit(self.key_redis+str(int(int(uid)/4000000000)), int(uid)%4000000000, 1)
                    yield Request(url="https://weibo.cn/"+uid,callback=self.parse)
                else:
                    print("%s already parsed." % uid)
        
        next_url = response.xpath('//a[text()="下页"]/@href').extract()
        if next_url:
            yield Request(url="https://weibo.cn"+next_url[0],callback=self.parse_list)
    
    def parse_weibo(self,response):
        #微博列表
        weibo_ID=re.findall("cn/(\d+)",response.url)[0]
        a_s=response.xpath('//a[contains(text(),"评论")]')
        for a in a_s:
            text=a.xpath("text()").extract()
            if not text:
                continue
            text=text[0].strip()
            if text[:2]!='评论':
                continue
            text_num=text.split("[")[-1].split("]")[-2]
            if text_num.isdigit() and int(text_num)>2:    #设置评论数大于2
                href=a.xpath("@href").extract()
               # print(text)
               # print(text_num)
                #print(href)
                yield Request(url=href[0],callback=self.parse_details)
        
        next_url = response.xpath('//a[text()="下页"]/@href').extract()
        if next_url:
            yield Request(url="https://weibo.cn"+next_url[0],callback=self.parse_weibo)
    
    
    def parse_details(self,response):
        items=Sina01Item()
        content_url=response.url
        content=response.xpath("//div[@id='M_']/div/span[@class='ctt']/text()").extract()
        if content:
            content="".join(content).strip()
        else:
            content=""
        comment_divs=response.xpath("//body/div[contains(@id,'C_')]")
        #for div in comment_divs:
        #comment=response.xpath("//div[contains(@id,'C_')]//text()").extract()
        relations=[]
        names=[]
        coms=[]
        for div in comment_divs:
            comment_relation=div.xpath("span//text()").extract()
            try:
                comment_relation=[i.strip() for i in comment_relation]
                comment_relation="\t".join(comment_relation[:-5]).strip()
            except:
                comment_relation=""
            comment_name=div.xpath("a[1]/text()").extract()
            if comment_name:
                comment_name=comment_name[0].strip()
            else:
                continue
            comment=div.xpath("span[@class='ctt']//text()").extract()
            if comment:
                comment=[i.strip() for i in comment]
                comment="\t".join(comment)
            else:
                continue
            relations.append(comment_relation)
            names.append(comment_name)
            coms.append(comment)
        if len(coms)>0:    
            items['url']=content_url#网址
            items['content']=content#微博正文
            items['comments']="\n".join(coms)#该页的评论
            items['names']="\n".join(names)#评论者昵称
            items['relationship']="\n".join(relations)#评论关系，如@某某，回复某某
            yield items
        next_url = response.xpath('//a[text()="下页"]/@href').extract()
        if next_url:
            yield Request(url="https://weibo.cn"+next_url[0],callback=self.parse_details)
    
        
        
            
        

        
        
            
        
        
        
        
        
        
