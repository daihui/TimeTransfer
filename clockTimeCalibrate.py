#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import fitting
import matplotlib.pyplot as plt

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

def clockTimeFactorSecSat(timeList,window):
    N=len(timeList)
    print N
    sec=[float(i+1) for i in range(N)]
    time=[]
    filteredSec=[]
    filteredTime=[]
    time.append(timeList[0][0])
    for i in range(1,N):
        time.append(timeList[i][0]-timeList[i-1][0])
    mat = fitting.polyLeastFit(sec,time,2)

    for i in range(N):
        det=abs(fitting.polyLeastFitCal([sec[i]],mat)[0]-time[i])
        if det<window:
            filteredSec.append(sec[i])
            filteredTime.append(time[i])
    matFilter=fitting.polyLeastFit(filteredSec,filteredTime,2)
    factorList=fitting.polyLeastFitCal(sec,matFilter)
    # newGPS=0
    # for i in range(N):
    #     newGPS+=factorList[i]
    #     print timeList[i][0]-newGPS
    print factorList
    return factorList
    # fig = plt.figure()
    # ax1 = fig.add_subplot(111)
    # ax1.scatter(sec,time, color='g', marker='o')
    # ax1.scatter(filteredSec,filteredTime, color='b',  marker='*')
    # ax1.scatter(sec,factorList, color='r',  marker='+')
    # plt.show()

def clockTimeFactorSecGro(timeList):
    N=len(timeList)
    print N
    sec=[float(i+1) for i in range(N)]
    time=[]
    filteredSec=[]
    filteredTime=[]
    time.append(timeList[0][0])
    for i in range(1,N):
        time.append(timeList[i][0]-timeList[i-1][0])
    mat = fitting.polyLeastFit(sec,time,2)

    for i in range(N):
        det=time[i]-fitting.polyLeastFitCal([sec[i]],mat)[0]
        if det>0:
            filteredSec.append(sec[i])
            filteredTime.append(time[i])
    matFilter=fitting.polyLeastFit(filteredSec,filteredTime,2)
    factorList=fitting.polyLeastFitCal(sec,matFilter)
    # newGPS=0
    # for i in range(N):
    #     newGPS+=factorList[i]
    #     print timeList[i][0]-newGPS
    print factorList
    return factorList
    # fig = plt.figure()
    # ax1 = fig.add_subplot(111)
    # ax1.scatter(sec,time, color='g', marker='o')
    # ax1.scatter(filteredSec,filteredTime, color='b',  marker='*')
    # ax1.scatter(sec,factorList, color='r',  marker='+')
    # plt.show()

def timeCalibrate(timeList,factor):
    timeListCal=[]
    for item in timeList:
        timeListCal.append([item[0]/factor])
    print 'time calibrate finished !'
    return timeListCal

if __name__=='__main__':
    GPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_GPS.txt',encoding='utf-8')
    timeList=fileToList.fileToList(GPSFile)
    factor=clockTimeFactorSecGro(timeList,50000)
    # for item in timeList:
    #     print item[0]/factor/1000000000000.0

