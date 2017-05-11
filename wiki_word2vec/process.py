#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 10:46:08 2017

@author: wj
"""
import jieba
import re
from jpype import *
from tqdm import tqdm
path1='/home/wj/myWork/语料库/维基百科-中文词条/zhwiki_2017_03.clean'
path2='/home/wj/myWork/语料库/word_vec_wiki/wiki_jieba.txt'
path3='/home/wj/myWork/语料库/word_vec_wiki/wiki_hanlp.txt'
#startJVM(getDefaultJVMPath(), "-Djava.class.path=/home/wj/HanLP/hanlp-1.3.3.jar:/home/wj/HanLP",\
#         "-Xms1g", "-Xmx1g")
#HanLP = JClass('com.hankcs.hanlp.HanLP')
pun='''`~!@#$%^&*()-=_+[]{}\|;':",./<>?`～！@#￥%……&×（）-=——+【】、{}|；‘：“”’，。/《》？「」'''
f_jieba=open(path2,'w')
#f_hanlp=open(path3,'w')

def total_lines(path1):
    i=0
    for line in open(path1):
        i+=1
    return i
#%%
pbar = tqdm(total=929099)
for line in open(path1):
    pbar.update(1)
    try:
        title=line.split('\t')[0]
        s=line.split('\t')[1]
    except:
        print("error:",line)
        continue
    s=re.split('，|。|；',s.strip())
    f_jieba.write("===")
    f_jieba.write(title)
    f_jieba.write('\n')
    for i1 in s:
        i=jieba.lcut(i1)
        s1=[j for j in i if j not in pun]
        s1=" ".join(s1)
        #print(s1)
        if s1:
            f_jieba.write(s1)
            f_jieba.write("\n")
      #  i_han=HanLP.segment(i1)
     #   i_han=[str(w).split('/')[0] for w in i_han]
    #    i_han=[w for w in i_han if w not in pun]
   #     i_han=" ".join(i_han)
  #      print(i_han)
 #       if i_han:
#            f_jieba.write(i_han)
#            f_jieba.write('\n')
        
f_jieba.close()
pbar.close()
    