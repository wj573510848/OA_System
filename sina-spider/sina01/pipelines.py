# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3

class Sina01Pipeline(object):
    def __init__(self):
        self.num=0
        self.con=sqlite3.connect('data.sqlite')
        self.cur=self.con.cursor()
        self.cur.execute('DROP TABLE IF EXISTS test')
        self.cur.execute("create table 'test'('url' text, 'content' text,'names' text,'comments' text,'relationship' text)")
    def process_item(self, item, spider):
        u=item['url']
        n=item['names']
        c=item['comments']
        r=item['relationship']
        c1=item['content']
        self.cur.execute("insert into test(url,content,names,comments,relationship) values (?,?,?,?,?)" , (u,c1,n,c,r))
        self.con.commit()
        self.num+=1
        if self.num%10==0:
            print("Save weibo number: %s" % self.num)
        return item
