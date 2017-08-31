#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import fitting

def clockTimeFactor(timeList):
    N=len(timeList)
    print N
    sec=[float(i+1) for i in range(N)]
    time=[timeList[i][0] for i in range(N)]
    mat = fitting.polyLeastFit(sec,time,1)
    detTime=fitting.polyLeastFitCal([N],mat)[0]-fitting.polyLeastFitCal([1],mat)[0]
    factor=detTime/((N-1)*1000000000000.0000)
    print 'time factor is '+str(factor)
    return factor

def timeCalibrate(timeList,factor):
    timeListCal=[]
    for item in timeList:
        timeListCal.append([item[0]/factor])
    print 'time calibrate finished !'
    return timeListCal

if __name__=='__main__':
    GPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170828\\20170829033442_fineParse_GPS.txt',encoding='utf-8')
    timeList=fileToList.fileToList(GPSFile)
    factor=clockTimeFactor(timeList)
    for item in timeList:
        print item[0]/factor/1000000000000.0

