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

def coindenceTest(dataFile1,dataFile2,channelDelay,coinWidth):
    list1=fileToList.fileToList(dataFile1)
    list2=fileToList.fileToList(dataFile2)
    saveFile=dataFile1[:-4]+'_coindence.txt'
    resultList=coincidence850(list1,list2,channelDelay,coinWidth)
    fileToList.listToFile(resultList,saveFile)

def timeAnalysis(timeList):
    diffList = []
    for i, item in enumerate(timeList):
        diffList.append([float(i), float(item[0]) - float(item[1])])
    print 'get the diffList.'
    return diffList


if __name__ == '__main__':
    dataFile1 = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.14\\6.14Nanshan_channel_0_classified.txt', 'utf8')
    dataFile2= unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.14\\6.14Nanshan_channel_1_classified.txt', 'utf8')
    coindenceTest(dataFile1,dataFile2,-4000,3000)
    # dataFile= unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.14\\6.14Nanshan.txt', 'utf8')
    # dataClassify = classifyData850(dataFile,[0,1,2,3,5])
    # timeList = fileToList.fileToList(dataClassify)
    # diffList = timeAnalysis(timeList)
    # fileToList.listToFile(diffList, dataClassify[:-4] + '_diff.txt')
    # dataFile1 = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\dat2txt\\recv_fixed.txt', 'utf8')
    # f=open(dataFile1)
    # for i in range(10000):
    #     print f.readlines()

