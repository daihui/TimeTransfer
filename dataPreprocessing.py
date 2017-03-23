#!/usr/bin/env python
#-*- coding: utf-8 -*-

#  数据预处理
#  将TDC采集的GPS秒脉冲和850同步光时间事件分别按格式存在GPSTime.txt和850Time.txt

__author__ = 'levitan'

def getFileNime(s):
    filename=str(s)
    gpsfilename=str(s)[:-4]+'_GPSTime.txt'
    lightfilename=str(s)[:-4]+'_850Time.txt'
    return filename,gpsfilename,lightfilename

def classifyData(filename,gpsfilename,lightfilename):
    gps=open(gpsfilename,'w')
    light=open(lightfilename,'w')
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