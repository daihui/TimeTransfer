#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

#TDC 时间数据转换


import fileToList
import filter
import TDCTest

def TDCDataConvert(bufferData,channelStr):
    global coarseTime
    global lastCoarseTime
    global carry
    global lastTime
    global fineTimeList
    global fineTimeLen

    channel=int(bufferData[12:14],16)&0x0F
    channelNo=int(bufferData[12:14],16)
    if bufferData[12:14]!=channelStr:
        return channelNo,0
    # print channelNo
    else:
        fineTime=(int(bufferData[6:8],16)&0x10)<<4 | int(bufferData[14:16],16)
        #print fineTime
        coarseTime[channel]=int(bufferData[8:10],16) | int(bufferData[10:12],16)<<8 | \
                            int(bufferData[4:6],16)<<16 | (int(bufferData[6:8],16)&0x0F)<<24
        if coarseTime[channel]<lastCoarseTime[channel]:
            carry[channel]+=1
        lastCoarseTime[channel]=coarseTime[channel]

        #如果没有细计数修正文件
        # if fineTime>=273:
        #     print fineTime
        #     exactTime=6250
        # else:
        #     exactTime=int(6250.0/273*fineTime)

        if fineTime<fineTimeLen:
            exactTime=fineTimeList[0][fineTime]
        else:
            exactTime=6250.0
            # print fineTime

        time = -exactTime+(coarseTime[channel]+(carry[channel]<<28))*6250
        # print coarseTime[channel],-exactTime,fineTime
        if channel>=0 & channel<8:
            if time<lastTime[channel]:
                print 'error in parse data channel %s time %s is small than %s'%(channel,time,lastTime[channel])
                lastTime[channel] = time
                return channel, time
            else:
                #print time-lastTime[channel]
                lastTime[channel]=time
                return channelNo,time
        else:
            print 'channel is out of range'
            return 0,0

def TDCDataParse(dataFile,fineTimeFile,start,channelStr):
    global coarseTime
    global lastCoarseTime
    global carry
    global lastTime
    global fineTimeList
    global fineTimeLen
    coarseTime=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    lastCoarseTime=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    carry=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    lastTime=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    fineTimeList=loadFimeTimeFile(fineTimeFile)
    fineTimeLen=len(fineTimeList[0])
    channelNo=int(channelStr,16)
    fileData = open(dataFile, 'rb')
    fileData.read(start)
    dataList = []
    count = 0
    bufferData = fileData.read(8).encode('hex')
    while len(bufferData) == 16:
        if bufferData[0:8]=='a5a5a5a5' or bufferData[8:]=='47474747':
            #print bufferData
            bufferData = fileData.read(8).encode('hex')
        else:
            channel,time=TDCDataConvert(bufferData,channelStr)
            if channel==channelNo:
                dataList.append([time])
                count += 1
            bufferData = fileData.read(8).encode('hex')
            #print bufferData
            #print channel, time
    print 'convert data to List, count: %s' % count
    return dataList

def loadFimeTimeFile(fineTimeFile):
    fileTimeList=fileToList.fileToList(fineTimeFile)
    print fileTimeList
    return fileTimeList


#解析双站共视时丽江站的实验数据，通道1，6，7分别是GPS信号、850信号、532信号
def TDCDataParseLJTest(date,dataLJ):
    # dataFile=unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171125\\20171125164702-tdc2-2-4-2k-2.dat',encoding='utf-8')
    dataFile=unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc2.dat'%(date,dataLJ),encoding='utf-8')
    channelList=[1,6,7]
    tdc=2
    for channel in channelList:
        saveFile=dataFile[:-4]+'_channel_%s.txt'%channel
        channelNo=str(40+channel-1)
        if channel==6:
            print 'channel: %s' % channel
            fineTimeFile = unicode('C:\Users\Levit\Experiment Data\丽江测试\\20180105\细计数\\0105_tdc2_17C_channel_6_45.txt',
                                   encoding='utf-8')
            dataList = TDCDataParse(dataFile, fineTimeFile, 8, channelNo)
            countList = TDCTest.countBySec(dataList)
            countFile = saveFile[:-4] + '_count.txt'
            fileToList.listToFile(countList, countFile)
            fileToList.listToFile(dataList,saveFile)
            filterFile = saveFile[:-4] + '_filtered.txt'
            length = len(dataList)
            for i in range(length):
                dataList[i] = [dataList[i][0]]
            filterList = filter.freqFilter(dataList, 10000200, 6, 300000)
            filterList = filter.reflectNoiseFilter(filterList, 1000000, 0)
            fileToList.listToFile(filterList, filterFile)
        elif channel==1:
            print 'channel: %s' % channel
            fineTimeFile = unicode('C:\Users\Levit\Experiment Data\丽江测试\\20180105\细计数\\0105_tdc2_17C_channel_6_45.txt',
                                   encoding='utf-8')
            dataList = TDCDataParse(dataFile, fineTimeFile, 8, channelNo)
            countList = TDCTest.countBySec(dataList)
            fileToList.listToFile(dataList, saveFile)
        elif channel==7:
            print 'channel: %s, channelNo: %s' % (channel,channelNo)
            fineTimeFile = unicode('C:\Users\Levit\Experiment Data\丽江测试\\20180105\细计数\\0105_tdc2_17C_channel_7_46.txt',
                                   encoding='utf-8')
            dataList = TDCDataParse(dataFile, fineTimeFile, 8, channelNo)
            countList = TDCTest.countBySec(dataList)
            countFile = saveFile[:-4] + '_count.txt'
            fileToList.listToFile(countList, countFile)
            fileToList.listToFile(dataList, saveFile)
            filterFile = saveFile[:-4] + '_filtered.txt'
            length = len(dataList)
            for i in range(length):
                dataList[i] = [dataList[i][0]]
            filterList = filter.freqFilter(dataList, 89985475, 6, 3000000)
            filterList = filter.reflectNoiseFilter(filterList, 1000000, 0)
            fileToList.listToFile(filterList, filterFile)

#解析双站共视时德令哈站的实验数据，通道1，4，5，6，7，8分别是GPS信号、532信号、850的H/V/+/-
def TDCDataParseDLHTest(date,dataDLH):
    dataFile = unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13.dat'%(date,dataDLH), encoding='utf-8')
    channelList = [1,4,5,6,7,8]
    # channelList =[4]
    tdc = 13
    for channel in channelList:
        saveFile = dataFile[:-4] + '_channel_%s.txt' % channel
        channelNo = str(40 + channel - 1)
        if channel==4:
            print 'channel: %s' % channel
            fineTimeFile = unicode(
                'C:\Users\Levit\Experiment Data\FineTimeCali\\tdc%s\\1216_tdc%s_5C_channel_%s_4%s.txt',
                encoding='utf-8') % (tdc, tdc, channel, channel - 1)
            dataList = TDCDataParse(dataFile, fineTimeFile, 8, channelNo)
            countList = TDCTest.countBySec(dataList)
            countFile = saveFile[:-4] + '_count.txt'
            fileToList.listToFile(dataList, saveFile)
            fileToList.listToFile(countList, countFile)
            filterFile = saveFile[:-4] + '_filtered.txt'
            length = len(dataList)
            for i in range(length):
                dataList[i] = [dataList[i][0]]
            filterList = filter.freqFilter(dataList,89985475, 6, 3000000)
            filterList = filter.reflectNoiseFilter(filterList, 1000000, 0)
            fileToList.listToFile(filterList, filterFile)
        elif channel==1:
            print 'channel: %s' % channel
            fineTimeFile = unicode(
                'C:\Users\Levit\Experiment Data\FineTimeCali\\tdc%s\\1216_tdc%s_5C_channel_%s_4%s.txt',
                encoding='utf-8') % (tdc, tdc, 5, 4)
            dataList = TDCDataParse(dataFile, fineTimeFile, 8, channelNo)
            countList = TDCTest.countBySec(dataList)
            fileToList.listToFile(dataList, saveFile)
        else:
            print 'channel: %s' % channel
            fineTimeFile = unicode(
                'C:\Users\Levit\Experiment Data\FineTimeCali\\tdc%s\\1216_tdc%s_5C_channel_%s_4%s.txt',
                encoding='utf-8') % (tdc, tdc, channel, channel - 1)
            dataList = TDCDataParse(dataFile, fineTimeFile, 8, channelNo)
            countList = TDCTest.countBySec(dataList)
            countFile = saveFile[:-4] + '_count.txt'
            fileToList.listToFile(dataList, saveFile)
            fileToList.listToFile(countList, countFile)
            filterFile = saveFile[:-4] + '_filtered.txt'
            length = len(dataList)
            for i in range(length):
                dataList[i] = [dataList[i][0]]
            filterList = filter.freqFilter(dataList, 10000200, 6, 300000)
            filterList = filter.reflectNoiseFilter(filterList, 1000000, 0)
            fileToList.listToFile(filterList, filterFile)

def listMerge(list1,list2):
    channelDelay=0
    coinWidth=30000
    det=2000000
    biasSum=0
    coinList=TDCTest.coincidence850(list1,list2,channelDelay,coinWidth)
    xa, ya, filteredList, fitList, residual = filter.fitFilter(coinList, 2000 / 1000000000000.0, 2, 1)
    for item in filteredList:
        biasSum+=item[2]
    bias=biasSum/len(filteredList)
    print 'bias: %s'%bias
    mergeList=[]
    length1=len(list1)
    length2=len(list2)
    print length1+length2
    index1=0
    for i in range(length2):
        detTime=list1[index1][0]-bias-list2[i][0]
        while detTime < -coinWidth:
            if index1==length1-1:
                break
            else:
                mergeList.append([list1[index1][0] - bias])
            if index1 < length1 -1:
                index1 += 1
                detTime = list1[index1][0] - bias - list2[i][0]
            else:
                detTime = list1[index1][0] - bias - list2[i][0]
                print list1[index1][0] - bias
                print '1 end'
                break
        if abs(detTime)<coinWidth:
            mergeList.append(list2[i])
            if index1 < length1 - 1:
                index1 += 1
            else:
                print '2 end'
        else:
            mergeList.append(list2[i])
    return mergeList

def listMergeTest(date,dataDLH):
    saveFile=unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_merge_filtered.txt'%(date,dataDLH), 'utf8')
    list1 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_channel_7_filtered.txt'%(date,dataDLH), 'utf8'))
    list2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_channel_6_filtered.txt'%(date,dataDLH), 'utf8'))
    list3 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_channel_8_filtered.txt'%(date,dataDLH),
                'utf8'))

    mergeList1=listMerge(list1,list2)
    print len(mergeList1)
    mergeList2=listMerge(list3,mergeList1)
    print len(mergeList2)
    listCount=TDCTest.countBySec(mergeList2)
    mergeCountFile=saveFile[:-4]+'_count.txt'
    fileToList.listToFile(mergeList2,saveFile)
    fileToList.listToFile(listCount,mergeCountFile)


if __name__=='__main__':
    date='20180125'
    dataDLH='20180126015156'
    dataLJ='20180126015157'
    TDCDataParseLJTest(date,dataLJ)
    # TDCDataParseDLHTest(date,dataDLH)
    # dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\6.13\\6.13-1000-tdc-coin-128.txt',encoding='utf-8')
    # fileToList.fileLong(dataFile)
    # listMergeTest(date,dataDLH)