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
    filtered = freqFilter(timeList, freq, window, factor)
    fileToList.listToFile(filtered, timeFile[:-4] + '_filtered.txt')
    return filtered

def detFilter(timeList,listCount,factor):
    for i in range(2,len(timeList)):
        det1=timeList[i-1][listCount]-timeList[i-2][listCount]
        det2=timeList[i][listCount]-timeList[i-1][listCount]
        if abs(det2)>abs(det1)*factor:
            timeList[i][listCount]=timeList[i-1][listCount]+det1
            print 'filter %s '%i

def freqFilterTest():
    file = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\send_fixed_850Time.txt', 'utf8')
    # file = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time.txt', 'utf8')
    #dataFilter(file, 10000000, 100, 200000)
    dataFilter(file, 10000000, 100, 1000000)
