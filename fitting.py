#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import matplotlib.pyplot as plt
import math
import numpy
import random
import fileToList
import filter
import clockTimeCalibrate
import gpsOrbit

def polyLeastFit(x,y,order):
    matA = []
    for i in range(0, order + 1):
        matA1 = []
        for j in range(0, order + 1):
            tx = 0.0
            for k in range(0, len(x)):
                dx = 1.0
                for l in range(0, j + i):
                    dx = dx * x[k]
                tx += dx
            matA1.append(tx)
        matA.append(matA1)
    matA = numpy.array(matA)

    matB = []
    for i in range(0, order + 1):
        ty = 0.0
        for k in range(0, len(x)):
            dy = 1.0
            for l in range(0, i):
                dy = dy * x[k]
            ty += y[k] * dy
        matB.append(ty)
    matB = numpy.array(matB)
    matAA = numpy.linalg.solve(matA, matB)
    #print 'fit finished !'

    return matAA

def polyLeastFitCal(x,mat):
    y = []
    for i in range(0, len(x)):
        yy = 0.0
        for j in range(0, len(mat)):
            dy = 1.0
            for k in range(0, j):
                dy *= x[i]
            dy *= mat[j]
            yy += dy
        y.append(yy)
    #print 'fit calculation finished !'
    return y

def polyLeastFitSegment(x,y,order,segmentTime):
    count=0
    s=0
    fitList=[]
    residual=[]
    xa=[]
    ya=[]
    xTmp=[]
    yTmp=[]
    lastTime=x[0]
    lastTimeIndex=0
    for i,time in enumerate(x):
        if time<lastTime+segmentTime:
            xTmp.append(time)
            yTmp.append(y[i])
            #lastTime=time
            count += 1
        else:
            if len(xTmp)>order:
                mat=polyLeastFit(xTmp,yTmp,order)
                y_fit=polyLeastFitCal(xTmp,mat)
                #print mat
                for j,yy in enumerate(y_fit):
                    fitList.append([yy])
                    residual.append([(yTmp[j] - yy)])
                    xa.append(xTmp[j])
                    ya.append(yTmp[j])
                count=0
                s+=1
                del xTmp[:]
                del yTmp[:]
                xTmp.append(time)
                yTmp.append(y[i])
                lastTime=time
                lastTimeIndex=i
                count += 1
            else:
                xTmp.append(time)
                yTmp.append(y[i])
                lastTime = time
                lastTimeIndex = i
                count += 1
    if len(xTmp)>order:
        mat = polyLeastFit(xTmp, yTmp, order)
        y_fit = polyLeastFitCal(xTmp, mat)
        for j, yy in enumerate(y_fit):
            fitList.append([yy])
            residual.append([(yTmp[j] - yy)])
            xa.append(xTmp[j])
            ya.append(yTmp[j])
            count += 1
        s+=1
    else:
        print 'no data or few data in this time segment'
        print len(xTmp)
    print 'data fitting in %s segment.'%s
    return xa,ya,fitList,residual

def polyFitSegment(x,y,order,segmentTime):
    timeUnit=1000000000000.0
    count=0
    s=0
    fitList=[]
    residual=[]
    xa = []
    ya = []
    xTmp=[]
    yTmp=[]
    lastTime=x[0]
    lastTimeIndex=0
    for i,time in enumerate(x):
        if time/timeUnit<lastTime/timeUnit+segmentTime:
            xTmp.append(time/timeUnit)
            yTmp.append(y[i]/timeUnit)
            #lastTime=time
            count += 1
        else:
            if len(xTmp)>2*order:
                mat=numpy.polyfit(xTmp,yTmp,order)
                Fx=numpy.poly1d(mat)
                y_fit=Fx(xTmp)
                #print mat
                for j,yy in enumerate(y_fit):
                    fitList.append([yy])
                    residual.append([(yTmp[j] - yy)])
                    xa.append(xTmp[j]*timeUnit)
                    ya.append(yTmp[j]*timeUnit)
                count=0
                s+=1
                del xTmp[:]
                del yTmp[:]
                xTmp.append(time/timeUnit)
                yTmp.append(y[i]/timeUnit)
                lastTime=time
                lastTimeIndex=i
                count += 1
            else:
                xTmp.append(time/timeUnit)
                yTmp.append(y[i]/timeUnit)
                lastTime = time
                lastTimeIndex = i
                count += 1
    if len(xTmp)>order:
        mat = numpy.polyfit(xTmp, yTmp, order)
        Fx = numpy.poly1d(mat)
        y_fit = Fx(xTmp)
        for j, yy in enumerate(y_fit):
            fitList.append([yy])
            residual.append([(yTmp[j] - yy)])
            xa.append(xTmp[j]*timeUnit)
            ya.append(yTmp[j]*timeUnit)
            count += 1
        s+=1
    else:
        print 'no data or few data in this time segment'
        print len(xTmp)
    print 'data fitting in %s segment.'%s
    return xa,ya,fitList,residual

def clockDiffByDistance(timeList1,timeList2,gpsTimeList1,gpsTimeList2,delayList,shift):
    factor1=clockTimeCalibrate.clockTimeFactor(gpsTimeList1)
    factor2=clockTimeCalibrate.clockTimeFactor(gpsTimeList2)
    list1=clockTimeCalibrate.timeCalibrate(timeList1,factor1)
    list2=clockTimeCalibrate.timeCalibrate(timeList2,factor2)
    gpsTimeList1=clockTimeCalibrate.timeCalibrate(gpsTimeList1,factor1)
    gpsTimeList2=clockTimeCalibrate.timeCalibrate(gpsTimeList2,factor2)

    lenght=len(list1)
    Num=4
    result=[]

    for index in range(lenght):
        startNo=int(list1[index][0]/1000000000000)-1
        delayFun1,delayFun2=gpsOrbit.gpsLagInterFun(gpsTimeList1,gpsTimeList2,delayList,startNo,Num,shift)
        delay1=delayFun1(list1[index][0])
        delay2=delayFun2(list2[index][0])
        delay1=delayFun1(list1[index][0]-delay1)
        delay2=delayFun2(list2[index][0]-delay2)
        delay1 = delayFun1(list1[index][0] - delay1)
        delay2 = delayFun2(list2[index][0] - delay2)
        coinDelay=list1[index][0]-delay1-(list2[index][0]-delay2)
        result.append([timeList1[index][0],list1[index][0],coinDelay,delay1,delay2])
    print 'clock difference calculated by satellite distance'
    return result

def clockDiffByDistanceTest(date):
    shift=-19
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0530-85-235_filtered.txt' % date,
                       'utf8')
    gpsFile1=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_GPSTime.txt' % date,
                       'utf8')
    gpsFile2 = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_GPSTime.txt' % date,
                       'utf8')
    delayFile=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_Recv_Precise_disDelay.txt' % date,
                       'utf8')
    saveFile=timeFile[:-4]+'_diffByDistance.txt'
    timeList = fileToList.fileToList(timeFile)
    gpsTimeList1=fileToList.fileToList(gpsFile1)
    gpsTimeList2=fileToList.fileToList(gpsFile2)
    delayList=fileToList.fileToList(delayFile)
    timeList1 = []
    timeList2 = []

    for i in range(len(timeList)):
        timeList1.append([timeList[i][0]])
        timeList2.append([timeList[i][1]])

    result=clockDiffByDistance(timeList1,timeList2,gpsTimeList1,gpsTimeList2,delayList,shift)
    fileToList.listToFile(result,saveFile)



def polyLeastFitTest(date):

    order = 9
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0329.txt'%date, 'utf8')
    timeList = fileToList.fileToList(timeFile)
    xa = []
    ya = []
    y=[]

    for i in range(len(timeList)):
        xa.append(timeList[i][1] )
        ya.append(timeList[i][0] - timeList[i][1])

    xa=xa[80000:120000]
    ya=ya[80000:120000]


    matAA = polyLeastFit(xa, ya, order)
    yya = polyLeastFitCal(xa, matAA)
    for i in range(len(yya)):
        y.append([yya[i]-ya[i]])
        # print yya[i]
    filter.dotFilter(y,0,10000,3)
    fileToList.listToFile(y,timeFile[:-4]+'_%s_residual_dotfilt.txt'%date)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(xa, y, color='g', linestyle='-', marker='')
    # ax.plot(xa,ya,color='m',linestyle='',marker='.')
    ax.legend()
    plt.show()

def polyLeastFitSegmentTest(date):
    order =50
    timeNormal=100000000000
    timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\Result\\synCoincidenceEM_0530-85-250-EM--18.txt' % date, 'utf8')
    #timeFile=unicode('E:\Experiment Data\时频传输数据处理\丽江测试\\4.14\\4.14-lzx-lj-400s_coinDiff_segment_search.txt','utf8')
    timeList = fileToList.fileToList(timeFile)
    xa = []
    ya = []
    x=[]

    for i in range(len(timeList)):
        xa.append(timeList[i][1])
        ya.append(timeList[i][0] - timeList[i][1])
        # xa.append(timeList[i][0])
        # ya.append(timeList[i][1])

    # xa = xa[50000:70000]
    # ya = ya[50000:70000]

    # print len(xa), len(ya)
    # xa,ya =filter.preFilter(timeList,2,100000)
    # print len(xa),len(ya)
    # fitList,residual=polyLeastFitSegment(xa,ya,10,1000)
    # filter.dotFilter(residual, 0, 10000.0, 3)
    # xa,ya,residual=filter.thresholdFilter(xa,ya,residual,0,4000)
    # fitList, residual = polyLeastFitSegment(xa, ya, order, 100)
    # xa, ya, residual = filter.thresholdFilter(xa, ya, residual, 0, 2500)
    xa,ya,timeList,fitList,residual=filter.fitFilter(timeList,3000,2,order)

    print len(xa),len(timeList),len(residual)
    #residualNormal=filter.normalByTime(timeList,residual,timeNormal)
    residualSecUnit=filter.timeUnitConvert(residual,1000000000000)
    fileToList.listToFileLong(residualSecUnit, timeFile[:-4] + '_%s_residual-0531-10-20000-ps.txt' % date)
    #fileToList.listToFile(timeList,timeFile[:-4]+'_filtered.txt')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(xa, residual, color='g', linestyle='-', marker='')
    # ax.plot(xa,ya,color='m',linestyle='',marker='.ux')
    ax.legend()
    plt.show()

def polyFitSegmentTest(date):
    order =1
    timeNormal=500000000000
    #timeFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\Result\\synCoincidenceEM_0530-85-250-EM--18.txt' % date, 'utf8')
    timeFile=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.14\\6.14Nanshan_channel_2-3_60-170-singlepulsecoindence.txt','utf8')
    timeList = fileToList.fileToList(timeFile)
    xa = []
    ya = []
    x=[]

    for i in range(len(timeList)):
        xa.append(timeList[i][1])
        ya.append((timeList[i][0] - timeList[i][1]))

    xa,ya,timeList,fitList,residual=filter.fitFilter(timeList,2000,3,1)
    # xa,ya,fitList, residual = polyFitSegment(xa, ya, 1, 0.1)
    # xa, ya, filteredList, residual=filter.thresholdFilter(xa,ya,residual,timeList,0,0.000000002)
    xa,ya,fitList, residual = polyFitSegment(xa, ya, order,300)
    # xa, ya, filteredList, residual = filter.thresholdFilter(xa, ya, residual, timeList, 0, 0.0000001)

    # print len(xa),len(timeList),len(residual)
    xa,residualNormal=filter.normalByTime(timeList,residual,timeNormal)
    # residualSecUnit=filter.timeUnitConvert(residual,1000000000000)
    fileToList.listToFileLong(residualNormal, timeFile[:-4] + '_residual-1-all-0.5-ps.txt')
    #fileToList.listToFile(filteredList,timeFile[:-4]+'_filtered.txt')
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    #ax2= fig.add_subplot(212)
    ax1.plot(xa,residualNormal, color='g', linestyle='-', marker='')
    #ax2.plot(xa,ya,color='m',linestyle='',marker='.')
    #ax2.plot(xa, fitList, color='g', linestyle='-', marker='')
    #ax.legend()
    plt.show()