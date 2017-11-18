#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'
import fileToList
import fitting

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
        xa.append(timeList[i][0])
        ya.append(timeList[i][2])
    xa,ya,fitList, residual = fitting.polyLeastFitSegment(xa, ya, 1, 100000000000)
    xa, ya, filteredList,residual= thresholdFilter(xa, ya, residual, timeList, 0, threshold)
    for j in range(times):
        xa,ya,fitList, residual = fitting.polyLeastFitSegment(xa, ya, order, 50000000000)
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
def normalByTime(timeList,residualList,time):
    count=0
    sum=0
    lastTime=timeList[0][0]
    normalList=[]
    xa=[]
    if len(timeList)==len(residualList):
        print 'len is ok'
    else:
        print 'lenght is not equal'
    for i,item in enumerate(timeList):
        if item[0]-lastTime<time:
            count+=1
            sum+=residualList[i][0]
        else:
            normalList.append([sum/count])
            xa.append(lastTime)
            #print sum,count
            lastTime=item[0]
            count=1
            sum=residualList[i][0]
    print 'normal list finished!'
    return xa,normalList

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
    del timeList[index+1:]
    print '%s reflect pulses moved out'%(length-index)
    return timeList

def reflectNoiseFilterTest():
    dataFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\170919\\20170920032416_fineParse_2_532_filtered.txt',encoding='utf-8')
    saveFile=dataFile[:-4]+'_reflectFiltered.txt'
    dataList=fileToList.fileToList(dataFile)
    dataList=reflectNoiseFilter(dataList,2000000,0)
    fileToList.listToFile(dataList,saveFile)

def freqFilterTest():
    file = unicode('C:\Users\Levit\Experiment Data\阿里数据\\170919\\20170920032416_fineParse_2_532.txt', 'utf8')
    saveFile=file[:-4]+'_filtered.txt'
    timeList=fileToList.fileToList(file)
    length=len(timeList)
    for i in range(length):
        timeList[i]=[timeList[i][0]]
    result=freqFilter(timeList,90000000,6,5000000)
    # result=freqFilter(timeList,10000000,6,200000)
    fileToList.listToFile(result,saveFile)

if __name__=='__main__':
    # freqFilterTest()
    reflectNoiseFilterTest()
