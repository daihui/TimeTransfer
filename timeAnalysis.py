#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import matplotlib.pyplot as plt
from scipy import optimize


def adjacentAnalysis(timeList,filename):
    N = len(timeList) - 1
    detTime = []
    count = 0
    for i in range(1, N):
        dt = (timeList[i][0] - timeList[i - 1][0]) - (timeList[i][1] - timeList[i - 1][1])
        if abs(dt) < 50000:
            detTime.append([timeList[i][0], timeList[i][1], dt])
            count += 1
    fileToList.listToFile(detTime, filename[:-4] + '_adjacent.txt')
    print 'adjacent analysis finished ! ' + str(N) + ' ' + str(count)
    return detTime

def adjacentAnalysisNear(timeList,filename):
    N = len(timeList) - 1
    detTime = []
    count = 0
    for i in range(1, N):
        dt = (timeList[i][0] - timeList[i - 1][0]) - (timeList[i][1] - timeList[i - 1][1])
        if (timeList[i][0] - timeList[i - 1][0])<52000000 and abs(dt) < 50000:
            detTime.append([timeList[i][0], timeList[i][1], dt])
            count += 1
    fileToList.listToFile(detTime, filename[:-4] + '_adjacentNear5.txt')
    print 'adjacent near analysis finished ! ' + str(N) + ' ' + str(count)
    return detTime


def minusAnalysis(timeList,filename):
    N = len(timeList)
    detTime = []
    for i in range(1, N):
        dt = timeList[i][0] - timeList[i][1]
        detTime.append([timeList[i][0], timeList[i][1], dt])
    fileToList.listToFile(detTime, filename[:-4] + '_minus.txt')
    print 'minus analysis finished !'
    return detTime


def leastsqToSec(timeList,tau):
    X = []
    Y = []
    R = []
    Sec = int(timeList[0][0] / tau)
    count = 0

    def residuals(p):
        k, b = p
        return Y - (k * X + b)

    for item in timeList:
        if int(item[0] / tau) == Sec:
            X.append(item[0] / tau)
            Y.append(item[2] )
            count += 1
        else:
            if count >= 2:
                r = optimize.leastsq(residuals, [1.0, 0.0])
                k, p = r[0]
                s = [Sec, (k * (Sec) + p)/1000000000000]
                #print s,k
                R.append(s)
            else:
                s = [Sec, item[2]/1000000000000]
                R.append(s)
            del X[:]
            del Y[:]
            X.append(item[0] / tau)
            Y.append(item[2] )
            Sec = int(item[0] / tau)
            count = 1
    print 'data reduced by leastsq to second.'
    return R


def interSec(timeList):
    startSec = int(timeList[0][0])
    interTimeList = []
    count = 0
    for item in timeList:
        if int(item[0]) == startSec + count:
            interTimeList.append(item)
            count += 1
        else:
            detTime = int(item[0] - (startSec + count))
            for t in range(detTime):
                interTimeList.append([startSec + count, (interTimeList[count - 1][1] + item[1]) / 2])
                count += 1
    print 'the lost second are makeup'
    return interTimeList


def adjacentAnalysisTest():
    timeFile = unicode('G:\时频传输数据处理\双站数据处理\\3.2\\result\\synCoincidenceEM.txt', 'utf8')
    timeList=fileToList.fileToList(timeFile)
    detTime = adjacentAnalysisNear(timeList,timeFile)
    # print len(detTime)
    # x = [detTime[i][0] / 1000000000000 for i in range(len(detTime))]
    # y = [detTime[i][2] for i in range(len(detTime))]
    # # print y
    # plt.figure("play")
    # ax1 = plt.subplot(111)
    # plt.sca(ax1)
    # plt.plot(x, y, linestyle='--', color='r')
    # plt.show()


def leastsqToSecTest():
    timeFile = unicode('G:\时频传输数据处理\双站数据处理\\3.2\\result\\synCoincidenceEM_adjacentNear5.txt', 'utf8')
    timeList = fileToList.fileToList(timeFile)
    tau=100000000000
    R=leastsqToSec(timeList,tau)
    #R = interSec(R)
    #print R
    fileToList.listToFileLong(R, timeFile[:-4] + '_milliSec0327.txt')
