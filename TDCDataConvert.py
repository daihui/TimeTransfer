#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

#TDC 时间数据转换


import fileToList
import filter
import TDCTest

def TDCDataConvert(bufferData):
    global coarseTime
    global lastCoarseTime
    global carry
    global lastTime
    global fineTimeList
    global fineTimeLen

    channel=int(bufferData[12:14],16)&0x0F
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
            return channel,time
    else:
        print 'channel is out of range'
        return 0,0

def TDCDataParse(dataFile,fineTimeFile,start,channelNo):
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
            channel,time=TDCDataConvert(bufferData)
            if channel==channelNo:
            # if True:
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

def TDCDataParseTest():
    # dataFile=unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171125\\20171125164702-tdc2-2-4-2k-2.dat',encoding='utf-8')
    dataFile=unicode('C:\Users\Levit\Experiment Data\德令哈测试\\20171216\零基线实验\\20171217022617-tdc13-0baseline-2.dat',encoding='utf-8')
    channel=5
    tdc=13
    fineTimeFile=unicode('C:\Users\Levit\Experiment Data\FineTimeCali\\tdc%s\\1216_tdc%s_5C_channel_%s_4%s.txt',encoding='utf-8')%(tdc,tdc,channel,channel-1)
    saveFile=dataFile[:-4]+'_channel_%s.txt'%channel
    dataList=TDCDataParse(dataFile,fineTimeFile,8,channel-1)
    TDCTest.countBySec(dataList)
    fileToList.listToFile(dataList,saveFile)

if __name__=='__main__':
    TDCDataParseTest()
    # dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\6.13\\6.13-1000-tdc-coin-128.txt',encoding='utf-8')
    # fileToList.fileLong(dataFile)