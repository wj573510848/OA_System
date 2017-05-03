# -*- coding: utf-8 -*-
"""
Created on Wed May  3 14:44:54 2017

@author: Aoshuo-wj
"""
#筛选出srt的文件处理。
#用时间来确定是否是属于同一段对话。
#时间间隔可调整。得出不同的对话。
import re

def is_srt(path1):
    with open(path1,'r',encoding='utf8') as f:
        s=f.read()
        d=re.findall(u"Dialogue",s)
    if len(d)>100:
        return False
    return True



def srttime(time):
    '''00:03:27,061  这种结构 返回毫秒单位的时间'''
    t = time.strip()
    ts = t.split(',')
    r = 0
    r = r + int(ts[1])
    ts = ts[0].split(':')
    r = r + 1000 * (int(ts[0]) * 3600 + int(ts[1]) * 60 + int(ts[2]))
    return r
        
#srt格式的时间分割。
def timeSpilt(file_path):
    with open(file_path,'r',encoding='utf8') as f:
        s=f.readlines()
    s=[i for i in s]
    tmp=[]
    items=[]
    for i in s:
        i=i.strip()
        if len(i)>1 and not("-->" in i):
            tmp.append(i)
        if("-->" in i):
            items.append(tmp[:-1])
            tmp=[]
            tmp.append(i)
    return items

def contentSplit(file_path):
    if not is_srt(file_path):
        print("This is not srt txt:",file_path)
        return None
    content_items=timeSpilt(file_path)
    currt=-10000
    cnt=0
    ret=[]
    for item in content_items:
        if not item:
            continue
        item_time=item[0]
        startt=srttime(item_time.split("-->")[0])
        endt=srttime(item_time.split("-->")[1])
        SPLIT_INTERVAL = 1000
        if cnt < 2:
                SPLIT_INTERVAL = 5000
        elif cnt < 3:
            SPLIT_INTERVAL = 2000
        if startt - currt > SPLIT_INTERVAL:
            ret.append(u'E')
            cnt = 0
        for i in item[1:]:
            cn=r"([\u4e00-\u9fa5]+)"
            pattern_cn = re.compile(cn)
            i=re.findall(pattern_cn,i)
            i="".join(i)
            ret.append(i)
        cnt = cnt + 1
        currt = endt
    return ret

if __name__ == "__main__":
    basic_path1="C:\\myWork\\zimuSpider\\ChineseFiles\\"
    basic_path2="C:\\myWork\\zimuSpider\\duihuaFiles\\"
    for i in range(998,999):
        file_path=basic_path1+str(i)+".txt"
        try:
            r=contentSplit(file_path)
        except:
            with open("C:\\myWork\\zimuSpider\\duihuaFiles\\error.txt",'a') as error_f:
                error_f.write("Process error:")
                error_f.write(file_path)
                error_f.write("\n")
        if r:
            file_path02=basic_path2+str(i)+".txt"
            with open(file_path02,'w',encoding='utf8') as f1:
                for r0 in r:
                    f1.write(r0)
                    f1.write("\n")
