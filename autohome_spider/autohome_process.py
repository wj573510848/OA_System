# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#[]可能是表情符号，所以删掉包含这个符号的句子。
##有可能是转发等消息，所以删掉这些句子。
#最后输出，包含中文且长度小于20的句子。
import re
import glob
path1='/home/wj/myWork/spiders/autohome/autohome01/results/'
path2='/home/wj/myWork/语料库/问答对/总结/luntan01.txt'
def process_raw(path1):
    qa=[]
    with open(path1,'r',encoding='utf8') as f:
        for line in f:
            if line[:2]=="Q:":
                qa.append(line)
            if line[:2]=="A:":
                qa.append(line)
                yield qa
                qa=[]               
def process_lines(path1):
    pa_s='(\[[^\[\]]+\])'#delete:[]
    pa_s=re.compile(pa_s)
    pa_ch='[\u4e00-\u9fa5]'
    pa_ch=re.compile(pa_ch)
    qa=[]
    for q,a in process_raw(path1):
        if len(q)<20 and len(a)<20:
            q=re.sub(pa_s,"",q)
            a=re.sub(pa_s,"",a)
            if re.search(pa_ch,q) and re.search(pa_ch,a):
                if not("#" in q) and not ('#' in a):
                    qa.append(q)
                    qa.append(a)
                    yield qa
                    qa=[]
files_path=[]
for i in range(1,21):
    files_path.append(path1+str(i)+".txt")
    
f1=open(path2,'w',encoding='utf8')
for file_path in glob.glob(path1+"*.txt"):
    for q,a in process_lines(file_path):
        f1.write("conversation:\n")
        f1.write(q[2:])
        f1.write(a[2:])
f1.close()
