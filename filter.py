#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'
import fileToList


def freqFilter(timeList, freq, window, threshold):
    N = len(timeList)
    count = 0
    for i in xrange(N - window - 1):
        averTime = 0.0
        for j in range(window):
            averTime+=timeList[i + j][0]%freq
        averTime = averTime / window
        if abs(timeList[i][0] % freq - averTime) < threshold:
            timeList[i - count][0] = timeList[i][0]
        else:
            count += 1
    del timeList[-count:]
    print 'time list filtered , %s data are moved out' % count
    return timeList


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

def thresholdFilter(x,timeList,listCount,threshold):
    listFiltered=[]
    xa=[]
    lenght = len(timeList)
    count=0
    for i in range(lenght):
        if abs(timeList[i][listCount])>threshold:
            count+=1
        else:
            listFiltered.append(timeList[i])
            xa.append(x[i])
    print '%s data moved !'%count
    return xa,listFiltered

def preFilter(timeList,listCount,threshold):
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
    file = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\send_fixed_850Time.txt', 'utf8')
    # file = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time.txt', 'utf8')
    #dataFilter(file, 10000000, 100, 200000)
    dataFilter(file, 10000000, 100, 1000000)
