#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import numpy as np
import random


def dataConvert(bufferByte):
    global carryBit
    fourByte = bufferByte[6:] + bufferByte[4:6] + bufferByte[2:4] + bufferByte[:2]
    specialBit = int(fourByte, 16) & 0x80000000
    if specialBit == 0x80000000:
        channel = bin(int(fourByte[:2], 16))[3:-1]
        channelBits = int(channel, 2)
        if channelBits == 63:
            carryBit += (int(fourByte[2:], 16)+int(bin(int(fourByte[1], 16))[-1]))
            preTimeBit = int(bin(int(fourByte[1], 16))[-1])
            timeTag = int(fourByte[2:], 16) + preTimeBit * 16777216 + carryBit * 33554432
        elif channelBits == 0:
            print 'sync signal'
            preTimeBit = int(bin(int(fourByte[1], 16))[-1])
            timeTag = int(fourByte[2:], 16) + preTimeBit * 16777216 + carryBit * 33554432
        else:
            print 'channel mark: %s' % channelBits
            preTimeBit = int(bin(int(fourByte[1], 16))[-1])
            timeTag = int(fourByte[2:], 16) + preTimeBit * 16777216 + carryBit * 33554432
    else:
        channel = bin(int(fourByte[:2], 16))[2:-1]
        if channel == '':
            channel = '0'
        channelBits = int(channel, 2)
        preTimeBit = int(bin(int(fourByte[1], 16))[-1])
        timeTag = (int(fourByte[2:], 16) + preTimeBit * 16777216 + carryBit * 33554432)
        # print channelBits,timeTag
    return channelBits, timeTag


def Hydraharp400DataToList(dataFile, start):
    fileData = open(dataFile, 'rb')
    fileData.read(start)
    dataList = []
    count = 0
    bufferByte = fileData.read(4).encode('hex')
    while len(bufferByte) == 8:
        dataList.append(bufferByte)
        bufferByte = fileData.read(4).encode('hex')
        count += 1
    print 'convert data to List, count: %s' % count
    return dataList


def Hydraharp400DataParse(dataList, saveFile, channelList):
    fileSave = open(saveFile, 'w')
    global carryBit
    carryBit = 0
    for data in dataList:
        channel, time = dataConvert(data)
        if channel in channelList:
            fileSave.write(str(channel) + '\t' + str(time) + '\n')
    fileSave.flush()
    fileSave.close()
    print 'data parser finished, saved to %s' % saveFile


def dataCoinLight(dataFile, channelDelay, coinWidth):
    dataList = fileToList.fileToList(dataFile)
    resultList = []
    index = 0
    count = 0
    length = len(dataList)
    process = True
    while process:
        if dataList[index][0] == dataList[index + 1][0]:
            index += 1
            if index > length - 2:
                process = False
        elif abs(dataList[index][1] - dataList[index + 1][1] - channelDelay) < coinWidth:
            resultList.append([dataList[index][1], (dataList[index][1] - dataList[index + 1][1])])
            count += 1
            index += 2
            if index > length - 2:
                process = False
        else:
            index += 1
            if index > length - 2:
                process = False
    print 'data coincidence finished %s coincidences, and difference time are calculated !' % count
    fileToList.listToFile(resultList, dataFile[:-4] + '_coinDiff.txt')
    return resultList


def dataCoinLightSegment(dataFile, channelDelay, coinWidth, segmentLength, start, channelList):
    global carryBit
    carryBit = 0
    saveFile = open(dataFile[:-4] + '_coinDiff_segment.txt', 'w')
    saveFile.close()
    saveFile = open(dataFile[:-4] + '_coinDiff_segment.txt', 'a')
    finish = False
    data = open(dataFile, 'rb')
    data.read(start)
    totCount = 0

    while not finish:
        segmentList = []
        dataToConvert = []
        coinList = []
        for indexS in range(segmentLength):
            bufferByte = data.read(4).encode('hex')
            if len(bufferByte) == 8:
                dataToConvert.append(bufferByte)
            else:
                finish = True
                print 'read file finished !'
                break
        for item in dataToConvert:
            channel, time = dataConvert(item)
            if channel in channelList:
                segmentList.append([channel, time])
                #print channel,time
        #break
        length = len(segmentList)
        index = 0
        count = 0
        process = True
        if length < 2:
            process = False
        while process:
            # print length,index
            if int(segmentList[index][0]) == int(segmentList[index + 1][0]):
                index += 1
            elif int(segmentList[index][0])<int(segmentList[index+1][0]):
                if abs(segmentList[index][1] - segmentList[index + 1][1] - channelDelay) < coinWidth:
                    coinList.append([segmentList[index],segmentList[index+1], (segmentList[index][1] - segmentList[index + 1][1]-channelDelay)])
                    count += 1
                    index += 2
                else:
                    index += 1
            else:
                if abs(segmentList[index+1][1] - segmentList[index][1] - channelDelay) < coinWidth:
                    coinList.append([segmentList[index+1],segmentList[index], (segmentList[index+1][1] - segmentList[index][1]-channelDelay)])
                    count += 1
                    index += 2
                else:
                    index += 1
            if index > length - 2:
                    process = False
        print 'segment data coincidence finished: %s coincidences' % count
        totCount += count
        Num = len(coinList)
        for i in range(Num):
            J = len(coinList[i])
            for j in range(J):
                saveFile.write('%s\t' % coinList[i][j])
            saveFile.write('\n')
    data.close()
    saveFile.flush()
    saveFile.close()
    print 'data coincidence finished, %s coincidences' % totCount

def dataCoinSegment(dataFile, channelDelay, coinWidth, segmentLength,searchSteps, start, channelList):
    global carryBit
    carryBit = 0
    saveFile = open(dataFile[:-4] + '_coinDiff_segment_search.txt', 'w')
    saveFile.close()
    saveFile = open(dataFile[:-4] + '_coinDiff_segment_search.txt', 'a')
    finish = False
    data = open(dataFile, 'rb')
    data.read(start)
    totCount = 0

    while not finish:
        segmentList = []
        dataToConvert = []
        coinList = []
        for indexS in range(segmentLength):
            bufferByte = data.read(4).encode('hex')
            if len(bufferByte) == 8:
                dataToConvert.append(bufferByte)
            else:
                finish = True
                print 'read file finished !'
                break
        for item in dataToConvert:
            channel, time = dataConvert(item)
            if channel in channelList:
                segmentList.append([channel, time])
                #print channel,time
        #break
        length = len(segmentList)
        count = 0
        for coinIndex in range(length-searchSteps):
            for searchIndex in range(1,searchSteps):
                detTime=segmentList[coinIndex][1]-segmentList[coinIndex+searchIndex][1]
                if abs(detTime)<coinWidth:
                    if segmentList[coinIndex][0]<segmentList[coinIndex+searchIndex][0]:
                        # coinList.append([segmentList[coinIndex],segmentList[coinIndex+searchIndex],detTime-channelDelay])
                        coinList.append([segmentList[coinIndex][1],detTime-channelDelay])
                        count+=1
                        break
                    elif segmentList[coinIndex][0]>segmentList[coinIndex+searchIndex][0]:
                        # coinList.append([segmentList[coinIndex+searchIndex],segmentList[coinIndex],-detTime+channelDelay])
                        coinList.append([segmentList[coinIndex+searchIndex][1],-detTime+channelDelay])
                        count+=1
                        break
                else:
                    break
        print 'segment data coincidence finished: %s coincidences' % count
        totCount += count
        Num = len(coinList)
        for i in range(Num):
            J = len(coinList[i])
            for j in range(J):
                saveFile.write('%s\t' % coinList[i][j])
            saveFile.write('\n')
    data.close()
    saveFile.flush()
    saveFile.close()
    print 'data coincidence finished, %s coincidences' % totCount

#Hydraharp400采数文件计算每秒通道计数
def dataSecCountSegment(dataFile, segmentLength, start, channelList):
    global carryBit
    carryBit = 0
    saveFile = open(dataFile[:-4] + '_SecCount_segment.txt', 'w')
    saveFile.close()
    saveFile = open(dataFile[:-4] + '_SecCount_segment.txt', 'a')
    finish = False
    data = open(dataFile, 'rb')
    data.read(start)
    second=0
    count1=0
    count2=0
    totCount=0
    carryCount=0

    while not finish:
        dataToConvert = []
        secCountList = []
        for indexS in range(segmentLength):
            bufferByte = data.read(4).encode('hex')
            if len(bufferByte) == 8:
                dataToConvert.append(bufferByte)
            else:
                finish = True
                print 'read file finished !'
                break
        for item in dataToConvert:
            channel, time = dataConvert(item)
            if channel in channelList:
                if time/1000000000000<second:
                    if int(channel)==int(channelList[0]):
                        count1+=1
                        totCount+=1
                    elif int(channel)==int(channelList[1]):
                        count2+=1
                        totCount+=1
                else:
                    secCountList.append([second,count1,count2])
                    second+=1
                    count1=0
                    count2=0
            else:
                carryCount+=1

        Num = len(secCountList)
        for i in range(1,Num):
            J = len(secCountList[i])
            for j in range(J):
                saveFile.write('%s\t' % secCountList[i][j])
            saveFile.write('\n')
    data.close()
    saveFile.flush()
    saveFile.close()
    print 'data second count finished ! total count: , carry count:  '
    print totCount
    print carryCount


def dataCoincidence(dataFile):
    dataList = fileToList.fileToList(dataFile)
    resultList = []
    count = 0
    if abs(dataList[1][1] - dataList[0][1]) < 10000:
        start = 0
    else:
        start = 1
    for i in range(start, len(dataList) / 2):
        resultList.append([i, (dataList[i + count][1] - dataList[i + 1 + count][1])])
        count += 1
    print 'difference time are calculated !'
    fileToList.listToFile(resultList, dataFile[:-4] + '_diff.txt')
    return resultList

def dataCountHistogram(timeList,bin,range):
    binCount=int(2*range/bin)
    countList=np.zeros([1,binCount])
    index=0
    finish=False
    while not finish:
        for item in timeList:
            if float(item[0])<float(-range+(index+1)*bin) and float(item[0])>float(-range+index*bin):
                countList[0][index]+=1
        print float(-range+index*bin),'\t',countList[0][index]
        index+=1
        if index>=binCount:
            finish=True


def timeAnalysis(datafile):
    timeList = fileToList.fileToList(dataFile)
    length = len(timeList)
    sum = 0.0
    for i in range(length):
        sum += timeList[i][1]
    averTime = sum / length
    for i in range(length):
        timeList[i][1] = (timeList[i][1] - averTime) / 1000000000000.0
    fileToList.listToFileLong(timeList, dataFile[:-4] + '_residual.txt')


def dataReduce(timeList, factor):
    listReduce = []
    lenght = len(timeList)
    sum = 0.0
    for i in range(lenght / factor):
        for j in range(factor):
            sum += timeList[i * factor + j][0]
        listReduce.append([sum / factor])
        sum = 0.0
    print 'data reduce finished ! '
    return listReduce

def randomList(timeList,channel,factor):
    length=len(timeList)
    print length
    ranList=[]
    for i in range(length/factor):
        ranList.append([timeList[i*factor+random.randint(0,factor-1)][channel]])
    print len(ranList)
    return ranList

if __name__ == '__main__':
    #dataFile = unicode('E:\Experiment Data\时频传输数据处理\丽江测试\\4.14\\4.14-lzx-lj-400s.ptu', 'utf8')
    # saveFile=dataFile[:-4]+'_parse.txt'
    # dataList=Hydraharp400DataToList(dataFile,8000)
    # Hydraharp400DataParse(dataList,saveFile,[0,2])
    # dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\4.11\\2-1200k-50M-100s-1.ptu','utf8')
    # dataCoincidence(dataFile)
    # dataCoinLight(dataFile,0,500)
    # dataCoinLightSegment(dataFile, 0, 2000, 2000000, 8000, [0, 1])
    #dataCoinSegment(dataFile, 0, 2000, 2000000,10, 8000, [0, 2])
    # dataSecCountSegment(dataFile,2000000,6000,[0,2])
    # timeAnalysis(dataFile)
    # timeList=fileToList.fileToList(dataFile)
    # reduceList=dataReduce(timeList,5)
    # fileToList.listToFileLong(reduceList,dataFile[:-4]+'_reduce5.txt')
    dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\4.11\\2-1200k-50M-100s-1_coinDiff_segment-1clo.txt','utf8')
    timeList=fileToList.fileToList(dataFile)
    #ranList=randomList(timeList,0,10)
    dataCountHistogram(timeList,50,2000)

