#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList

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
        #print channelBits,timeTag
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

def Hydraharp400DataParse(dataList,saveFile,channelList):
    fileSave=open(saveFile,'w')
    global carryBit
    carryBit=0
    for data in dataList:
        channel,time=dataConvert(data)
        if channel in channelList:
            fileSave.write(str(channel)+'\t'+str(time)+'\n')
    fileSave.flush()
    fileSave.close()
    print 'data parser finished, saved to %s'%saveFile

def dataCoinLight(dataFile,channelDelay,coinWidth):
    dataList=fileToList.fileToList(dataFile)
    resultList=[]
    index=0
    count=0
    length=len(dataList)
    process=True
    while process:
        if dataList[index][0]==dataList[index+1][0]:
            index+=1
            if index>length-2:
                process=False
        elif abs(dataList[index][1]-dataList[index+1][1]-channelDelay)<coinWidth:
            resultList.append([dataList[index][1],(dataList[index][1]-dataList[index+1][1])])
            count+=1
            index+=2
            if index>length-2:
                process=False
        else:
            index+=1
            if index>length-2:
                process=False
    print 'data coincidence finished %s coincidences, and difference time are calculated !'%count
    fileToList.listToFile(resultList,dataFile[:-4]+'_coinDiff.txt')
    return resultList

def dataCoinLightSegment(dataFile,channelDelay,coinWidth,segmentLength,start,channelList):
    global carryBit
    carryBit=0
    saveFile=open(dataFile[:-4]+'_coinDiff_segment.txt','w')
    saveFile.close()
    saveFile=open(dataFile[:-4]+'_coinDiff_segment.txt','a')
    finish=False
    data=open(dataFile,'rb')
    data.read(start)
    totCount=0

    while not finish:
        segmentList=[]
        dataToConvert=[]
        coinList=[]
        for indexS in range(segmentLength):
            bufferByte=data.read(4).encode('hex')
            if len(bufferByte)==8:
                dataToConvert.append(bufferByte)
            else:
                finish=True
                print 'read file finished !'
                break
        for item in dataToConvert:
            channel,time=dataConvert(item)
            if channel in channelList:
                segmentList.append([channel,time])
        length= len(segmentList)
        index=0
        count=0
        process=True
        if length<2:
            process=False
        while process:
            #print length,index
            if segmentList[index][0]==segmentList[index+1][0]:
                index+=1
                if index>length-2:
                    process=False
            elif abs(segmentList[index][1]-segmentList[index+1][1]-channelDelay)<coinWidth:
                coinList.append([segmentList[index][1],(segmentList[index][1]-segmentList[index+1][1])])
                count+=1
                index+=2
                if index>length-2:
                    process=False
            else:
                index+=1
                if index>length-2:
                    process=False
        print 'segment data coincidence finished: %s coincidences'%count
        totCount+=count
        Num=len(coinList)
        for i in range(Num):
            J=len(coinList[i])
            for j in range(J):
                saveFile.write('%.1f\t'%coinList[i][j])
            saveFile.write('\n')
    data.close()
    saveFile.flush()
    saveFile.close()
    print 'data coincidence finished, %s coincidences'%totCount

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

def dataReduce(timeList,factor):
    listReduce=[]
    lenght=len(timeList)
    sum=0.0
    for i in range(lenght/factor):
        for j in range(factor):
            sum+=timeList[i*factor+j][0]
        listReduce.append([sum/factor])
        sum=0.0
    print 'data reduce finished ! '
    return listReduce

if __name__=='__main__':
    dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\4.10\\2-80k-50M-100s-1.ptu','utf8')
    # saveFile=dataFile[:-4]+'_parse.txt'
    # dataList=Hydraharp400DataToList(dataFile,8000)
    # Hydraharp400DataParse(dataList,saveFile,[0,1])
    # dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地TDC测试\\4.1\解析\\recv_time-10k-400s_classified_diff_4.5_residual_segment.txt','utf8')
    #dataCoincidence(dataFile)
    #dataCoinLight(dataFile,0,500)
    dataCoinLightSegment(dataFile,0,500,1000000,8000,[0,2])
    #timeAnalysis(dataFile)
    # timeList=fileToList.fileToList(dataFile)
    # reduceList=dataReduce(timeList,5)
    # fileToList.listToFileLong(reduceList,dataFile[:-4]+'_reduce5.txt')
