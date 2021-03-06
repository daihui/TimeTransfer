#!/usr/bin/env python
#-*- coding: utf-8 -*-

#  数据预处理
#  将TDC采集的GPS秒脉冲和850同步光时间事件分别按格式存在GPSTime.txt和850Time.txt

__author__ = 'levitan'

import fileToList

def getFileNime(s):
    filename=s
    gpsfilename=s[:-4]+'_GPSTime.txt'
    synfilename=s[:-4]+'_850Time.txt'
    return filename,gpsfilename,synfilename

def classifyData(filename, gpsfilename, synfilename):
    gps=open(gpsfilename,'w')
    light=open(synfilename, 'w')
    try:
        with open(filename) as f:
            for line in f:
                dataline=line.split()
                if dataline[0]=='5':
                   gps.write(dataline[1]+'\n')
                elif dataline[0]=='4':
                   light.write(dataline[1]+'\n')
            gps.flush()
            gps.close()
            light.flush()
            light.close()
    finally:print 'data classify successfully !'

def dataSelectBySec(startSec,endSec):
    dataFile=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\send_fixed_850Time.txt' , 'utf8')
    dataList=fileToList.fileToList(dataFile)
    saveFile=dataFile[:-4]+'_%s-%s.txt'%(startSec+1,endSec)
    selectList=[]
    for item in dataList:
        sec=int(item[0]/1000000000000)
        if sec>startSec and sec<endSec+1:
            selectList.append(item)
    print 'data selected by secend'
    fileToList.listToFile(selectList,saveFile)