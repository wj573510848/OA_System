#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 09:44:17 2017

@author: wj
"""

import gensim

path1='wiki_jieba.txt'

class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        #i=0
        for line in open(self.dirname):
            #i+=1
            #print(i)
            #if i==100:
                #break
            if line[0]!='=':
                yield line.split()
sentences=MySentences(path1)
model = gensim.models.Word2Vec(sentences)
model.save("wiki_word2vec")