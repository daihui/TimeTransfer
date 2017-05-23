#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'
import fileToList


def freqFilter(timeList, freq, window, threshold):
    N = len(timeList)
    resultList=[]
    count = 0
    for i in xrange(N - window - 1):
        okCount=0.0
        for j in range(1,window):
            residual=((timeList[i + j][0]-timeList[i][0])%freq)
            if residual<threshold or (freq-residual)<threshold:
                okCount+=1
        if okCount > (window-1)/2:
            resultList.append([timeList[i][0]])
        else:
            count += 1
            #print okCount
    print 'time list filtered , %s data are moved out' % count
    return resultList

def slopeFilter(timeList,threshold):
    resultList=[]
    #for

def dataFilter(timeFile, freq, window, threshold):
    timeList = fileToList.fileToList(timeFile)
    filtered = freqFilter(timeList, freq, window, threshold)
    fileToList.listToFile(filtered, timeFile[:-4] + '_filtered.txt')
    return filtered

def dotFilter(timeList,listCount,threshold,times):
    lenght=len(timeList)
    for loop in range(times):
        count=0
        for i in range(lenght-1):
            if abs(timeList[i][listCount])>threshold:
                timeList[i][listCount]=timeList[i+1][listCount]
                count+=1
        print '%s\'th filter have finished, %s data are replace by the next data'%(loop,count)
    for i in range(lenght-1):
        if abs(timeList[i][listCount]) > threshold:
            timeList[i][listCount] =threshold/2

def thresholdFilter(x,y,timeList,listCount,threshold):
    listFiltered=[]
    xa=[]
    ya=[]
    lenght = len(timeList)
    count=0
    for i in range(lenght):
        if abs(timeList[i][listCount])>threshold:
            count+=1
        else:
            listFiltered.append(timeList[i])
            xa.append(x[i])
            ya.append(y[i])
    print '%s data moved !'%count
    return xa,ya,listFiltered

def  preFilter(timeList,listCount,threshold):
    listFiltered=[]
    xa=[]
    lenght = len(timeList)
    count=0
    listFiltered.append(timeList[0][0]-timeList[0][1])
    xa.append(timeList[0][1])
    for i in range(1,lenght):
        if abs(timeList[i][listCount]-timeList[i-1][listCount])>threshold:
            count+=1
        else:
            listFiltered.append(timeList[i][0]-timeList[i][1])
            xa.append(timeList[i][1])
    print '%s data moved !'%count
    return xa,listFiltered

def freqFilterTest():
    file = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\recv_fixed_850Time.txt', 'utf8')
    # file = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time.txt', 'utf8')
    #dataFilter(file, 10000000, 100, 200000)
    timeList=fileToList.fileToList(file)
    freqFilter(timeList,10000000,10,100000)
