# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class Zimu01Pipeline(object):
    def __init__(self):
        self.num=1
    def process_item(self, item, spider):
        filename=str(self.num)
        filename='results/'+filename
        print("Save file: %s" % self.num)
        with open(filename,"wb") as f:
            f.write(item['body'])
        self.num+=1
        return item
