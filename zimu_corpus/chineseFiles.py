# -*- coding: utf-8 -*-
"""
Created on Mon May  1 17:27:46 2017

@author: Administrator
"""
#将中文文件筛选出，并且处理为UTF8格式。
import chardet
import re
import glob
import traceback

path1='C:\\myWork\\zimuSpider\\zimuFiles'                 
path2="C:\\myWork\\zimuSpider\\ChineseFiles" 
cn=r"([\u4e00-\u9fa5]+)"
j=0
k=0
pattern_cn = re.compile(cn)
for i in glob.glob(path1+"\\*"):
    k+=1
    try:
        with open(i,'rb') as f:
            s=f.read()
            e=chardet.detect(s)['encoding']
            if(not e):
                e='gb18030'
            s=s.decode(e,'ignore').encode("utf8",'ignore').decode()
            ch_txt=re.findall(pattern_cn,s)
            if len(ch_txt)>100:
                j+=1
                with open(path2+"\\"+str(j)+".txt" ,'w',encoding= 'utf8') as f1:
                    f1.write(s)
                print("j:",j)
    except:
        traceback.print_exc()
        print(i)
        break
    print("K:",k)


        
    
    
