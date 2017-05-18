# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from tianya02.items import Tianya02Item,IdItem

class Tianya02Pipeline(object):
    def __init__(self):
        self.fileNum=1
        self.qaNum=0
        self.basic_path='/home/wj/myWork/spiders/tianya/tianya02/results/'
        self.f=open(self.basic_path+str(self.fileNum)+".txt",'w',encoding='utf8')
        self.f_id=open('crawlID.txt','w',encoding='utf8')
    def process_item(self, item, spider):
        if isinstance(item, Tianya02Item):
            try:
                self.f.write("Q:"+item['q']+"\n")
                self.f.write("A:"+item['a']+"\n")
                self.qaNum+=1
                if self.qaNum%100==0:
                    print("===Save: %s QA===" % self.qaNum)
            except:
                print("Can not write",item)
            if self.qaNum!=0 and self.qaNum%10000==0:
                self.fileNum+=1
                self.f.close()
                self.f=open(self.basic_path+str(self.fileNum)+".txt",'w',encoding='utf8')
        if isinstance(item, IdItem):
            try:
                self.f_id.write(item['ID'])
                self.f_id.write("\n")
            except:
                print("Something wrong in writing id.")
        return item