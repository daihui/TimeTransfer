#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import struct
import fileToList
#print struct.unpack("b",fileData.read(1))

def dataConvert(bufferByte):
    global carryBit
    fourByte=bufferByte[6:]+bufferByte[4:6]+bufferByte[2:4]+bufferByte[:2]
    specialBit=int(fourByte,16) & 0x80000000
    if specialBit==0x80000000:
        channel=bin(int(fourByte[:2],16))[3:-1]
        channelBits=int(channel,2)
        if channelBits==63:
            carryBit+=int(fourByte[-1],16)
            preTimeBit=int(bin(int(fourByte[1],16))[-1])
            timeTag=int(fourByte[2:],16)+preTimeBit*16777216+carryBit*33554432
        elif channelBits==0:
            print 'sync signal'
            preTimeBit=int(bin(int(fourByte[1],16))[-1])
            timeTag=int(fourByte[2:],16)+preTimeBit*16777216+carryBit*33554432
        else:
            print 'channel mark: %s'%channelBits
            preTimeBit=int(bin(int(fourByte[1],16))[-1])
            timeTag=int(fourByte[2:],16)+preTimeBit*16777216+carryBit*33554432
    else:
        channel=bin(int(fourByte[:2],16))[2:-1]
        if channel=='':
            channel='0'
        channelBits=int(channel,2)
        preTimeBit=int(bin(int(fourByte[1],16))[-1])
        timeTag=(int(fourByte[2:],16)+preTimeBit*16777216+carryBit*33554432)
        # print channelBits,timeTag
    return channelBits,timeTag

def Hydraharp400DataToList(dataFile,start):
    fileData=open(dataFile,'rb')
    fileData.read(start)
    dataList=[]
    count=0
    bufferByte=fileData.read(4).encode('hex')
    while len(bufferByte)==8:
        dataList.append(bufferByte)
        bufferByte=fileData.read(4).encode('hex')
        count+=1
    print 'convert data to List, count: %s'%count
    return dataList

def Hydraharp400DataParse(dataList,saveFile):
    fileSave=open(saveFile,'w')
    global carryBit
    carryBit=0
    for data in dataList:
        channel,time=dataConvert(data)
        if channel==0 or channel==1:
            fileSave.write(str(channel)+'\t'+str(time)+'\n')
    fileSave.flush()
    fileSave.close()
    print 'data parser finished, saved to %s'%saveFile

def dataCoincidence(dataFile):
    dataList=fileToList.fileToList(dataFile)
    resultList=[]
    count=0
    if abs(dataList[1][1]-dataList[0][1])<10000:
        start=0
    else:
        start=1
    for i in range(start,len(dataList)/2):
        resultList.append([i,(dataList[i+count][1]-dataList[i+1+count][1])])
        count+=1
    print 'difference time are calculated !'
    fileToList.listToFile(resultList,dataFile[:-4]+'_diff.txt')
    return resultList

def timeAnalysis(datafile):
    timeList=fileToList.fileToList(dataFile)
    length=len(timeList)
    sum=0.0
    for i in range(length):
        sum+=timeList[i][1]
    averTime=sum/length
    for i in range(length):
        timeList[i][1]=(timeList[i][1]-averTime)/1000000000000.0
    fileToList.listToFileLong(timeList,dataFile[:-4]+'_residual.txt')

if __name__=='__main__':
    # dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地TDC测试\HydraHarp400\\10k-500s-1.ptu','utf8')
    # saveFile=dataFile[:-4]+'_parse.txt'
    # dataList=Hydraharp400DataToList(dataFile,8000)
    # Hydraharp400DataParse(dataList,saveFile)
    dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地TDC测试\HydraHarp400\\10k-500s-mode2-1_parse.txt','utf8')
    dataCoincidence(dataFile)
    #timeAnalysis(dataFile)
