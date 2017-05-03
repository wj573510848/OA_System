# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 16:18:17 2017

@author: Administrator
"""
#1.将zipfiles中的压缩文件，全部解压缩至unzipfiles
#2.将unzipfiles中的文件，进行筛选，将srt、ass、ssa三种类型的文件移动至特定文件夹。
#3.其余文件删除。

import glob
import os
import shutil
import zipfile
from unrar import rarfile

#解压缩
def pZipFile(file_path,save_path):
    
    z=zipfile.ZipFile(file_path,'r')
    z.extractall(save_path)
    z.close()
#解压缩
def pRarFile(file_path,save_path):
    
    rar=rarfile.RarFile(file_path,'r')
    rar.extractall(save_path)    

#将文件中的压缩文件，解压缩至目标文件夹。并且删除原文件中的文件
def unZipFiles(oldpos,despos):
    totalFiles=glob.glob(oldpos+"*")
    for f in totalFiles:
        i=1
        save_path=despos+str(i)
        while(os.path.exists(save_path)):
            i+=1
            save_path=despos+str(i)
        try:
            pZipFile(f,save_path)
            os.remove(f)
        except:
            try:
                pRarFile(f,save_path)
                os.remove(f)
            except:
                print("Can't unrar or unzip:",f)

              
#oldpos="G:\\myTest\\zimu\\zipFiles\\"
#despos="G:\\myTest\\zimu\\unzipFiles\\"
#unZipFiles(oldpos,despos)


#将解压缩的文件清理。
#srt、ass、ssa文件移动至zimuFiles
#zip，rar文件移动至zipFiles
#其他文件删除
def processFiles(unZipFiles="C:\\myWork\\zimuSpider\\unzipFiles\\",\
                 zimuFiles="C:\\myWork\\zimuSpider\\zimuFiles\\",\
                 zipFiles="C:\\myWork\\zimuSpider\\zipFiles\\"):
    for root, dirs, files in os.walk(unZipFiles):
        if files:
            for f in files:
                endName=os.path.splitext(f)[-1]
                if endName in (".srt",".ass",'.ssa'):
                    i=1
                    newpos=zimuFiles+str(i)+endName
                    while(os.path.exists(newpos)):
                        i+=1
                        newpos=zimuFiles+str(i)+endName
                    oldpos=os.path.join(root,f)
                    shutil.move(oldpos,newpos)
                elif endName in (".rar",".zip"):
                    i=1
                    newpos=zipFiles+str(i)+endName
                    while(os.path.exists(newpos)):
                        i+=1
                        newpos=zipFiles+str(i)+endName
                    oldpos=os.path.join(root,f)
                    shutil.move(oldpos,newpos)
                else:
                    try:
                        os.remove(os.path.join(root,f))
                    except:
                        print("Can't remove:",f)
    for f in glob.glob(unZipFiles+"*"):
        try:
            shutil.rmtree(f)
        except:
            print("Can't rmtree:",f)

#oldpos="G:\\myTest\\zimu\\zipFiles\\"
#despos="G:\\myTest\\zimu\\unzipFiles\\"
#unZipFiles(oldpos,despos)
#processFiles(unZipFiles="G:\\myTest\\zimu\\unzipFiles\\",zimuFiles="G:\\myTest\\zimu\\zimuFiles\\")            

oldpos="C:\\myWork\\zimuSpider\\zipFiles\\"
despos="C:\\myWork\\zimuSpider\\unzipFiles\\"        
aa=glob.glob(oldpos+"*")
i=0
while(1):
    i+=1
    print(i)
    unZipFiles(oldpos,despos)
    processFiles()
    aa_new=glob.glob(oldpos+"*")
    if aa_new==aa:
        break
    aa=aa_new
    

        
    
        
