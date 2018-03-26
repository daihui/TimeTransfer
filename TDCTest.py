#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList


def classifyData(dataFile):
    filename=dataFile[:-4] + '_classified.txt'
    dataClassify = open(filename, 'w')
    try:
        with open(dataFile) as f:
            for line in f:
                dataline = line.split()
                if dataline[0] == '0':
                    dataClassify.write(dataline[1] + '\t')
                elif dataline[0] == '1':
                    dataClassify.write(dataline[1] + '\n')
            dataClassify.flush()
            dataClassify.close()
    finally:
        print 'data classify successfully !'
    return filename

def classifyData850(dataFile,channelList):
    fileNames=[]
    dataClassify=[]
    for item in channelList:
        fileNames.append(dataFile[:-4] + '_channel_%s_classified.txt'%item)
        dataClassify.append(open(fileNames[-1],'w'))
    try:
        with open(dataFile) as f:
            for line in f:
                dataline=line.split()
                for index,item in enumerate(channelList):
                    if dataline[0]==str(item):
                        dataClassify[index].write(dataline[1] + '\n')
                        break
            for item in dataClassify:
                item.flush()
                item.close()
    finally:
        print 'data classify successfully !'
    return fileNames

def coincidence850(list1,list2,channelDelay, coinWidth):
    resultList=[]
    index1=0
    index2=0
    count=0
    finish=False
    len1=len(list1)
    len2=len(list2)
    print len1,len2
    while not finish:
        if index1 > len1-1 or index2 > len2-1:
            break
        detTime=list1[index1][0]-list2[index2][0]-channelDelay
        if abs(detTime)<coinWidth:
            resultList.append([list1[index1][0],list2[index2][0],detTime])
            count+=1
            index1+=1
            index2+=1
        elif detTime>0:
            index2+=1
        else:
            index1+=1
    print 'coincidence finished! %s pairs'%count
    return resultList

def coindenceTest(dataList1,dataList2,channelDelay,coinWidth,saveFile):
    resultList=coincidence850(dataList1,dataList2,channelDelay,coinWidth)
    averSecCount=countBySec(resultList)
    fileToList.listToFile(resultList,saveFile)
    return resultList,averSecCount

def timeAnalysis(timeList):
    diffList = []
    for i, item in enumerate(timeList):
        diffList.append([float(i), float(item[0]) - float(item[1])])
    print 'get the diffList.'
    return diffList

def coindenceListMerge(dataList1,dataList2):
    listMerge=[]
    index1=0
    index2=0

def mergeFilter(dataList,timeWindow):
    length=len(dataList)
    filteredList=[]
    filteredList.append(dataList[0])
    count=0
    for index in range(1,length):
        if abs(dataList[index][0]-dataList[index-1][0])>timeWindow:
            filteredList.append(dataList[index])
        else:
            count+=1
    print 'dataList have been filtered! %s data repeat in %s ps have been moved '%(count,timeWindow)
    return filteredList

def mergeFilterTest():
    timeWindow=100000
    dataFile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.27NS\\6.27NS_coindence-2pulse-merge-1900-2080.txt', 'utf8')
    dataList=fileToList.fileToList(dataFile)
    filteredList=mergeFilter(dataList,timeWindow)
    saveFile=dataFile[:-4]+'_mergeFiltered.txt'
    fileToList.listToFile(filteredList,saveFile)

def countBySec(dataList):
    length=len(dataList)
    sec=int(dataList[0][0]/1000000000000)
    # sec = int(dataList[0][0] )
    count=0
    sumSec=0
    sumCount=0
    countList=[]
    for index in range(length):
        if int(dataList[index][0]/1000000000000)==sec:
        # if int(dataList[index][0] ) == sec:
            count+=1
        else:
            print '%s\t%s'%(sec,count)
            countList.append([sec,count])
            sumSec+=1
            sumCount+=count
            count=0
            # sec=int(dataList[index][0]/1000000000000)
            sec+=1
    return countList

def countBySecTest():
    dataFile = unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_1064_245-445_coincidence_0320_match.txt', 'utf8')
    dataList=fileToList.fileToList(dataFile)
    countList=countBySec(dataList)

    # return averSecCount

if __name__ == '__main__':
    # dataFile1 = unicode('C:\Users\Levit\Experiment Data\德令哈测试\系统延时测试\\20180302\\20180302211447-15mPMD-信号线-1_channel_2.txt', 'utf8')
    # dataFile2 = unicode('C:\Users\Levit\Experiment Data\德令哈测试\系统延时测试\\20180302\\20180302211447-15mPMD-信号线-1_channel_3.txt', 'utf8')
    # saveFile = dataFile1[:-4] + '_coindence.txt'
    # datalist1 = fileToList.fileToList(dataFile1)
    # datalist2 = fileToList.fileToList(dataFile2)
    # coindenceTest(datalist1,datalist2,-999999849928,200000,saveFile)
    # coindenceTest(datalist1, datalist2, -35297770-105000 , 10000, saveFile)
    #mergeFilterTest()
    countBySecTest()
    # dataFile= unicode('C:\Users\Levit\Experiment Data\阿里数据\\170919\\20170919AliSat.txt', 'utf8')
    # dataClassify = classifyData850(dataFile,[5,10,27])
    # timeList = fileToList.fileToList(dataClassify)
    # diffList = timeAnalysis(timeList)
    # fileToList.listToFile(diffList, dataClassify[:-4] + '_diff.txt')
    # dataFile1 = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\dat2txt\\recv_fixed.txt', 'utf8')
    # f=open(dataFile1)
    # for i in range(10000):
    #     print f.readlines()

