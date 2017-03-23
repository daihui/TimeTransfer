#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import matplotlib.pyplot as plt


def adjacentAnalysis(timeFile):
    timeList = fileToList.fileToList(timeFile)
    N = len(timeList) - 1
    detTime = []
    count=0
    for i in range(1, N):
        #print timeList[i]
        dt = (timeList[i][0] - timeList[i - 1][0]) - (timeList[i][1] - timeList[i - 1][1])
        if abs(dt) < 50000:
            detTime.append([timeList[i][0],timeList[i][1],dt])
            count+=1
            #print dt
    fileToList.listToFile(detTime,timeFile[:-4]+'_adjacent.txt')
    print 'adjacent analysis finished ! '+str(N)+' '+str(count)
    return detTime

def minusAnalysis(timeFile):
    timeList = fileToList.fileToList(timeFile)
    N = len(timeList)
    detTime = []
    for i in range(1, N):
        #print timeList[i]
        dt = timeList[i][0] - timeList[i][1]
        detTime.append([timeList[i][0],timeList[i][1],dt])
        #print dt
    fileToList.listToFile(detTime,timeFile[:-4]+'_minus.txt')
    print 'minus analysis finished !'
    return detTime

def adjacentAnalysisTest():
    timeFile = unicode('G:\时频传输数据处理\双站数据处理\\3.2\\850coincidenceEM.txt', 'utf8')
    detTime = adjacentAnalysis(timeFile)
    print len(detTime)
    x=[detTime[i][0]/1000000000000 for i in range(len(detTime))]
    y=[detTime[i][2] for i in range(len(detTime))]
    #print y
    plt.figure("play")
    ax1 = plt.subplot(111)
    plt.sca(ax1)
    plt.plot(x,y,linestyle='--', color='r')
    plt.show()
