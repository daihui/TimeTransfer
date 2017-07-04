#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

#TDC 时间数据转换


import fileToList

def TDCDataConvert(bufferData):
    global coarseTime
    global lastCoarseTime
    global carry
    global lastTime
    global fineTimeList

    channel=int(bufferData[12:14],16)&0x0F
    fineTime=int(bufferData[6:8],16)&0x10<<4 | int(bufferData[14:16],16)
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

    if fineTime<len(fineTimeList[0]):
        exactTime=fineTimeList[0][fineTime]
    else:
        exactTime=6250.0
        print fineTime

    time = -exactTime+(coarseTime[channel]+(carry[channel]<<28))*6250
    if channel>=0 & channel<8:
        if time<lastTime[channel]:
            print 'error in parse data channel %s time%s is small than %s'%(channel,time,lastTime[channel])
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
    coarseTime=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    lastCoarseTime=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    carry=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    lastTime=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    fineTimeList=loadFimeTimeFile(fineTimeFile)

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
                dataList.append([channel,time])
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
    dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\7.1TDC\\7.1-tdc2-3252-160Mhz-500s-3.dat',encoding='utf-8')
    fineTimeFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\FineTimeCali\\tdcB2-52.txt',encoding='utf-8')
    saveFile=dataFile[:-4]+'_fineParse.txt'
    dataList=TDCDataParse(dataFile,fineTimeFile,8,2)
    fileToList.listToFile(dataList,saveFile)

if __name__=='__main__':
    TDCDataParseTest()
    # dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\6.13\\6.13-1000-tdc-coin-128.txt',encoding='utf-8')
    # fileToList.fileLong(dataFile)