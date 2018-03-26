#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'
import fileToList
import fitting
import numpy

#根据已知脉冲频率进行频率滤波
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

# def slopeFilter(timeList,threshold):
#     resultList=[]
    #for

#给出脉冲数据文件，进行频率滤波
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

def thresholdFilter(x, y, residual,timeList, listCount, threshold):
    #listFiltered=[]
    xa=[]
    ya=[]
    filteredList=[]
    residualFiltered=[]
    lenght = len(residual)
    count=0
    for i in range(lenght):
        if abs(residual[i][listCount])>threshold:
            count+=1
            #print residual[i][listCount],threshold
        else:
            #listFiltered.append(residual[i])
            xa.append(x[i])
            ya.append(y[i])
            filteredList.append(timeList[i])
            residualFiltered.append(residual[i])

    print '%s data moved !'%count
    return xa,ya,filteredList,residualFiltered

def fitFilter(timeList,threshold,times,order):
    xa=[]
    ya=[]
    filteredList=[]
    for i in range(len(timeList)):
        # xa.append(timeList[i][0]-timeList[i][4])
        xa.append(timeList[i][0])
        ya.append(timeList[i][2])
        # ya.append((timeList[i][0] - timeList[i][1]))
    xa,ya,fitList, residual = fitting.polyLeastFitSegment(xa, ya, 2, 10000000000000)
    xa, ya, filteredList,residual= thresholdFilter(xa, ya, residual, timeList, 0, 4*threshold)
    for j in range(times):
        xa,ya,fitList, residual = fitting.polyLeastFitSegment(xa, ya, order, 5000000000000)
        xa, ya, filteredList,residual = thresholdFilter(xa, ya, residual,filteredList, 0, threshold)

    return xa,ya,filteredList,fitList,residual

def fitFineFilter(timeList,threshold,times,order):
    xa=[]
    ya=[]
    filteredList=[]
    for i in range(len(timeList)):
        xa.append(timeList[i][0])
        ya.append(timeList[i][0]-timeList[i][1])
    xa,ya,fitList, residual = fitting.polyLeastFitSegment(xa, ya, 1, 200000000000)
    xa, ya, filteredList,residual= thresholdFilter(xa, ya, residual, timeList, 0, 4*threshold)
    for j in range(times):
        xa,ya,fitList, residual = fitting.polyLeastFitSegment(xa, ya, order, 10000000000)
        xa, ya, filteredList,residual = thresholdFilter(xa, ya, residual,filteredList, 0, threshold)

    return xa,ya,filteredList,fitList,residual

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

#将residualList根据单位时间内多个点平滑成一个点
#TODO 时间需要确认
def normalByTime(timeList,residualList,time):
    count=0
    sum=0
    lastTime=timeList[0][0]
    sumTime=0
    normalList=[]
    xa=[]
    if len(timeList)==len(residualList):
        print 'len is ok'
    else:
        print 'lenght is not equal'
    for i,item in enumerate(timeList):
        detTime=item[0]-lastTime
        if detTime<time:
            count+=1
            sum+=residualList[i][0]
            sumTime+=detTime
        else:
            normalList.append([sum/count])
            xa.append((lastTime+sumTime/count))
            #print sum,count
            lastTime=item[0]
            count=1
            sum=residualList[i][0]
            sumTime=0
    print 'normal list finished!'
    return xa,normalList

def normalBySec(timeList,time,order,offset):
    timeSec=1000000000000.0
    startSec=int(timeList[0][0]/time)
    endSec=int(timeList[-1][0]/time)
    length=len(timeList)
    index=0
    xa1=[]
    xa2 = []
    ya=[]
    orbit1=[]
    orbit2 = []
    fitSecList=[]
    for sec in range(startSec,endSec+1):
        while index<length and timeList[index][0]<(sec+0.5)*time:
            xa1.append(timeList[index][0]/timeSec)
            xa2.append(timeList[index][1] / timeSec)
            ya.append(timeList[index][0]-timeList[index][1])
            orbit1.append(timeList[index][4])
            orbit2.append(timeList[index][5])
            index+=1
        if len(xa1)>200:
            mat = numpy.polyfit(xa1, ya, order)
            mat1 = numpy.polyfit(xa1, orbit1, order)
            mat2 = numpy.polyfit(xa2, orbit2, order)
            mat3=numpy.polyfit(xa1, xa2, order)
            Fx = numpy.poly1d(mat)
            Fx1 = numpy.poly1d(mat1)
            Fx2 = numpy.poly1d(mat2)
            Fx3=numpy.poly1d(mat3)
            t=Fx(sec/(timeSec/time))
            t1 = Fx1(sec / (timeSec / time)+offset)
            sec2=Fx3(sec)
            t2=Fx2(sec2+offset)
            fitSecList.append([sec,sec2,t1,t2,t-t1+t2])
            # print sec,sec2,sec-sec2,t,t1,t2,t-t1+t2
            del xa1[:]
            del xa2[:]
            del ya[:]
            del orbit1[:]
            del orbit2[:]
        # else:
        #     fitSecList.append([sec, 0,0,0])
        #     print fitSecList[-1][0], fitSecList[-1][1],fitSecList[-1][2],fitSecList[-1][3]
            # print 'len(xa) is < order !!!'
    return fitSecList

def normalBySecLaser(timeList,time,order,offset):
    timeSec=1000000000000.0
    startSec=int(timeList[0][0]/time+1)
    endSec=int(timeList[-1][0]/time)
    length=len(timeList)
    index=0
    xa1=[]
    xa2 = []
    ya=[]
    orbit1=[]
    orbit2 = []
    fitSecList=[]
    for sec in range(startSec,endSec+1):
        while index<length and timeList[index][0]<(sec+0.5)*time:
            xa1.append(timeList[index][0]/timeSec)
            xa2.append(timeList[index][1] / timeSec)
            ya.append(timeList[index][2]+offset)
            orbit1.append(timeList[index][3])
            orbit2.append(timeList[index][4])
            index+=1
        if len(xa1)>200:
            mat = numpy.polyfit(xa1, ya, order)
            mat1 = numpy.polyfit(xa1, orbit1, order)
            mat2 = numpy.polyfit(xa2, orbit2, order)
            mat3=numpy.polyfit(xa1, xa2, order)
            Fx = numpy.poly1d(mat)
            Fx1 = numpy.poly1d(mat1)
            Fx2 = numpy.poly1d(mat2)
            Fx3=numpy.poly1d(mat3)
            t=Fx(sec/(timeSec/time))
            t1 = Fx1(sec / (timeSec / time))
            sec2=Fx3(sec)
            t2=Fx2(sec2)
            fitSecList.append([sec,sec2,t,t1,t2])
        else:
            del xa1[:]
            del xa2[:]
            del ya[:]
            del orbit1[:]
            del orbit2[:]
            num=len(fitSecList)

            for i in range(order+1):
                xa1.append(fitSecList[num-1-i][0])
                xa2.append(fitSecList[num-1-i][1])
                ya.append(fitSecList[num-1-i][2])
                orbit1.append(fitSecList[num-1-i][3])
                orbit2.append(fitSecList[num-1-i][4])
            mat = numpy.polyfit(xa1, ya, order)
            mat1 = numpy.polyfit(xa1, orbit1, order)
            mat2 = numpy.polyfit(xa2, orbit2, order)
            mat3 = numpy.polyfit(xa1, xa2, order)
            Fx = numpy.poly1d(mat)
            Fx1 = numpy.poly1d(mat1)
            Fx2 = numpy.poly1d(mat2)
            Fx3 = numpy.poly1d(mat3)
            t = Fx(sec )
            t1 = Fx1(sec )
            sec2 = Fx3(sec)
            t2 = Fx2(sec2)
            fitSecList.append([sec, sec2, t, t1, t2])
            print xa1,ya
            print 'len(xa1) less 200'

        del xa1[:]
        del xa2[:]
        del ya[:]
        del orbit1[:]
        del orbit2[:]
        # else:
        #     fitSecList.append([sec, 0,0,0])
        #     print fitSecList[-1][0], fitSecList[-1][1],fitSecList[-1][2],fitSecList[-1][3]
            # print 'len(xa) is < order !!!'
    return fitSecList

#时间单位转换
def timeUnitConvert(timeList,timeUnit):
    result=[]
    count=0
    N=len(timeList[0])
    for item in timeList:
        result.append([])
        for i in range(N):
            result[count]+=[float(item[i])/timeUnit]
        count+=1
    return result

def reflectNoiseFilter(timeList,thresold,channel):
    length=len(timeList)
    nowTime=timeList[0][channel]
    index=0
    for i in range(1,length):
        if timeList[i][channel]-nowTime>thresold:
            index+=1
            timeList[index]=timeList[i]
            nowTime=timeList[index][channel]
        else:
            print timeList[i][channel]-nowTime
    del timeList[index+1:]
    print '%s reflect pulses moved out'%(length-index)
    return timeList

def reflectNoiseFilterTest():
    dataFile=unicode('C:\Users\Levit\Experiment Data\双站数据\\20180121\共视数据\\20180122014608-tdc13_channel_6.txt',encoding='utf-8')
    saveFile=dataFile[:-4]+'_reflectFiltered.txt'
    dataList=fileToList.fileToList(dataFile)
    dataList=reflectNoiseFilter(dataList,1000000,0)
    fileToList.listToFile(dataList,saveFile)

def freqFilterTest():
    file = unicode('C:\Users\Levit\Experiment Data\丽江测试\\20180104\\20180105014530_channel_6.txt', 'utf8')
    saveFile=file[:-4]+'_filtered.txt'
    timeList=fileToList.fileToList(file)
    length=len(timeList)
    for i in range(length):
        timeList[i]=[timeList[i][0]]
    result=freqFilter(timeList,10000200,6,300000)
    # result=freqFilter(timeList,10000000,6,200000)
    fileToList.listToFile(result,saveFile)

def fitFineFilterTest():
    file = unicode('C:\Users\Levit\Experiment Data\双站数据\\20170302\\result\\synCoincidence-85-250--19-0-Coin-紫台WGS84-atm-factor-haiji.txt', 'utf8')
    saveFile = file[:-4] + '_fitFilter.txt'
    timeList = fileToList.fileToList(file)
    xa, ya, timeList, fitList, residual=fitFineFilter(timeList,3500/1000000000000.0,5,2)
    fileToList.listToFile(timeList,saveFile)

def normalBySecLaserTest():
    file = unicode('C:\Users\Levit\Experiment Data\双站数据\\20180109\\result\\synCoincidence-145-235--22-1-Coin-紫台WGS84-atm-factor-haiji_laser_filtered.txt',
        'utf8')
    saveFile = file[:-4] + '_Sec.txt'
    timeList = fileToList.fileToList(file)
    offset=-156000
    fitList=normalBySecLaser(timeList,1000000000000.0,5,offset)
    fileToList.listToFile(fitList,saveFile)

if __name__=='__main__':
    # freqFilterTest()
    # reflectNoiseFilterTest()
    fitFineFilterTest()
    # normalBySecLaserTest()
