#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import matplotlib.pyplot as plt
from scipy import optimize
import fitting
import filter
import numpy as np
import clockTimeCalibrate


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
        if (timeList[i][0] - timeList[i - 1][0])<32000000 and abs(dt) < 50000:
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


def leastsqToSec(timeList,tau,order):
    X = []
    Y = []
    R = []
    Sec = int(timeList[0][0] / tau)
    count = 0

    # def residuals(p):
    #     k, b = p
    #     return Y - (k * X + b)

    for item in timeList:
        if int(item[0] / tau) == Sec:
            X.append(item[0] / tau)
            Y.append(item[1] )
            count += 1
        else:
            if count >= 2:
                # r = optimize.leastsq(residuals, [1.0, 0.0])
                # k, p = r[0]
                # s = [Sec, (k * (Sec) + p)/1000000000000]
                print count
                mat=fitting.polyLeastFit(X,Y,order)
                y=fitting.polyLeastFitCal([Sec+0.5],mat)
                averY=sum(Y)/len(Y)
                if y[0]>3*averY:
                    s=[Sec+0.5,averY/1000000000000]
                    print averY/1000000000000,'0'
                else:
                    s=[Sec+0.5,y[0]/1000000000000]
                    print y[0]/1000000000000,'1'
                #print s,k
                R.append(s)
            else:
                s = [Sec+0.5, item[1]/1000000000000]
                print item[1]/1000000000000,'2'
                R.append(s)
            del X[:]
            del Y[:]
            X.append(item[0] / tau)
            Y.append(item[1] )
            Sec = int(item[0] / tau)
            count = 1
    print 'data reduced by leastsq to second/%s.'%tau
    filter.dotFilter(R,1,0.000000005,3)
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


def adjacentAnalysisTest(date):
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0329_170-190.txt'%date, 'utf8')
    timeList=fileToList.fileToList(timeFile)
    detTime = adjacentAnalysisNear(timeList,timeFile)
    # print len(detTime)
    x = [detTime[i][0] / 1000000000000 for i in range(len(detTime))]
    y = [detTime[i][2] for i in range(len(detTime))]
    # print y
    plt.figure("play")
    ax1 = plt.subplot(111)
    plt.sca(ax1)
    plt.plot(x, y, linestyle='--', color='r')
    plt.show()


def leastsqToSecTest():
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\result\\synCoincidenceEM_0422_eff5_3.2_residual_segment_dotfilter0422.txt', 'utf8')
    timeList = fileToList.fileToList(timeFile)
    tau=10000000000
    R=leastsqToSec(timeList,tau,1)
    #R = interSec(R)
    #print R
    fileToList.listToFileLong(R, timeFile[:-4] + '_%smilliSec0422.txt'%(tau/1000000000))

def GPS_Compare(gpsList1,gpsList2,shift):
    timeFactor1, offset1 = clockTimeCalibrate.clockTimeFactorFit(gpsList1)
    timeFactor2, offset2 = clockTimeCalibrate.clockTimeFactorFit(gpsList2)
    gpsFitList1 = clockTimeCalibrate.timeCalibrate(gpsList1, timeFactor1, -offset1)
    gpsFitList2 = clockTimeCalibrate.timeCalibrate(gpsList2, timeFactor2, -offset2)
    N1=len(gpsFitList1)
    N2=len(gpsFitList2)
    Sec = []
    coinList = []
    residual = []
    if shift>=0:
        if N1-shift >= N2:
            N = N2
        else:
            N = N1-shift

        for i in range(N):
            residual.append(gpsFitList1[i+shift][0]-(gpsFitList2[i][0]+shift*1000000000000))
            Sec.append(i+1)
            coinList.append([gpsFitList1[i+shift][0],gpsFitList2[i][0],residual[-1]])
    else:
        if N1+shift >= N2:
            N = N2
        else:
            N = N1+shift
        for i in range(N):
            residual.append(gpsFitList1[i - shift][0] - (gpsFitList2[i][0] - shift * 1000000000000))
            Sec.append(i + 1)
            coinList.append([gpsFitList1[i - shift][0], gpsFitList2[i][0], residual[-1]])
    rms=np.std(residual,ddof=1)
    m=np.mean(residual)
    print 'GPS Compare RMS:%s Mean:%s'%(rms,m)
    return coinList,rms,m

def GPS_CompareTest(date, dataLJ,dataDLH,shift):
    gpsList1 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc2_channel_1.txt' % (date, dataLJ), 'utf8'))
    gpsList2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_channel_1.txt' % (date, dataDLH), 'utf8'))
    coinList,rms,m=GPS_Compare(gpsList1,gpsList2,shift)
    X=[i+1 for i in range(len(coinList))]
    residual=[coinList[i][2] for i in range(len(coinList))]
    residualH = [[coinList[i][2]] for i in range(len(coinList))]
    histList = dataHistogram(residualH, 0, 5000, 60000, 0)
    xa = [histList[i][0] for i in range(len(histList))]
    ya = [histList[i][1] for i in range(len(histList))]
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax1.plot(X, residual, color='g', linestyle='-', marker='*')
    ax1.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
    ax1.yaxis.grid(True, which='major')  # y坐标轴的网格使用次刻度show()
    ax1.set_ylabel('Difference (ps)' , fontsize=20)
    ax1.set_xlabel('Time (s)', fontsize=20)
    ax1.set_title('GPS Compare RMS:%d ps Mean:%d ps'%(rms,m), fontsize=24)
    ax2 = fig.add_subplot(122)
    ax2.plot(xa, ya, color='r', linestyle='-', marker='*')
    ax2.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
    ax2.yaxis.grid(True, which='major')  # y坐标轴的网格使用次刻度show()
    ax2.set_ylabel('Count', fontsize=20)
    ax2.set_xlabel('Time Difference (ps)', fontsize=20)
    ax2.set_title('Histgram' , fontsize=24)
    plt.show()



def dataHistogram(timeList,channel,bin,binRange,offset):
    binCount=int(2*binRange/bin)
    print binCount
    countList=np.zeros([1,binCount])
    histList=[]
    for data in timeList:
        t=data[channel]-offset
        if t>=0:
            index=int(t/bin)+binCount/2
        else:
            index=int(t/bin)-1+binCount/2
        if index<binCount and index>=0:
            countList[0][index]+=1
    # print countList
    for i in range(binCount):
        histList.append([offset+bin*(i-binCount/2),countList[0][i]])
        print histList[-1]
    return histList

def dataHistogramTest():
    file = unicode(
        'C:\Users\Levit\Experiment Data\双站数据\\20180109\\result\\GPS 比对.txt',
        'utf8')
    offset=0
    saveFile = file[:-4] + '_%s_hist.txt'%offset
    timeList = fileToList.fileToList(file)
    histList = dataHistogram(timeList,0,5000,60000,offset)
    fileToList.listToFile(histList, saveFile)

if __name__=='__main__':
    # dataHistogramTest()
    GPS_CompareTest('20180108', '20180109015114', '20180109015114', 0)