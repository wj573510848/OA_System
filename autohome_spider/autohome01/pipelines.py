# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class Autohome01Pipeline(object):
    def __init__(self):
        self.fileNum=1
        self.qaNum=0
        self.basic_path='/home/wj/myWork/spiders/autohome/autohome01/results/'
        self.f=open(self.basic_path+str(self.fileNum)+".txt",'w',encoding='utf8')
    def process_item(self, item, spider):
        try:
            self.f.write("Q:"+item['q']+"\n")
            self.f.write("A:"+item['a']+"\n")
            self.qaNum+=1
            print("===Save: %s QA===" % self.qaNum)
        except:
            print("Can not write",item)
        if self.qaNum!=0 and self.qaNum%10000==0:
            self.fileNum+=1
            self.f.close()
            self.f=open(self.basic_path+str(self.fileNum)+".txt",'w',encoding='utf8')
        return item
