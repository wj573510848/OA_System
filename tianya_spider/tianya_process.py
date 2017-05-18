#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 14:54:49 2017

@author: wj
"""

#删掉不包含中文的问答对。
#删掉含有"本帖发自""消息来自"的句子。
#得到长度小于20的句子。

import re

path1='/home/wj/myWork/spiders/tianya/tianya02/results/1.txt'
path2='/home/wj/myWork/语料库/问答对/总结/tianya01.txt'

def process_raw(path1):
    
    pa_ch='[\u4e00-\u9fa5]'
    pa_ch=re.compile(pa_ch)
    
    items=[]
    for line in open(path1):
        if line[:2]=="Q:":
            items.append(line[2:])
        if line[:2]=="A:":
            items.append(line[2:])
            if len(items)==2:
                if re.search(pa_ch,items[0]) and re.search(pa_ch,items[1]):
                    if len(items[0].strip())<20 and len(items[1].strip())<20:
                        yield items
            items=[]
#本帖发自

def process_convs(convs):
    cut1="本帖发自"
    cut2="消息来自"
    pa='[\u4e00-\u9fa5|0-9|a-z|A-Z]+'
    pa=re.compile(pa)

    for lines in convs:
        q=lines[0]
        a=lines[1]
        q=" ".join(re.findall(pa,q))
        a=" ".join(re.findall(pa,a))
        if q[:4]==cut1 or a[:4]==cut1 or q[:4]==cut2 or a[:4]==cut2:
            continue
        else:
            yield q,a
a=process_convs(process_raw(path1))
    
    


        
        
            

