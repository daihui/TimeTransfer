#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import clockTimeCalibrate
import fitting
import lagInterpolation
import fileToList

#根据各自TDC记录GPS秒脉冲，对TDC采集数据的时间经行修正，对齐到GPS时间尺度
def timeCalibrate(groPulseList,satPulseList,groGPSList,satGPSList):
    groFactor=clockTimeCalibrate.clockTimeFactor(groGPSList)
    satFactor=clockTimeCalibrate.clockTimeFactor(satGPSList)
    groGPSList=clockTimeCalibrate.timeCalibrate(groGPSList,groFactor)
    satGPSList=clockTimeCalibrate.timeCalibrate(satGPSList,satFactor)
    groPulseList=clockTimeCalibrate.timeCalibrate(groPulseList,groFactor)
    satPulseList=clockTimeCalibrate.timeCalibrate(satPulseList,satFactor)
    print 'time calibrated!'
    return groPulseList,satPulseList,groGPSList,satGPSList

#寻找地面发射脉冲，星上接收到的脉冲的符合对
def groPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec):
    indexGro=0
    indexSat=0
    Num=4
    coinCount=0
    coinList=[]
    tolerate = 10000000
    #satShiftTime=groSatShift*1000000000000.0
    if startSec-groSatShift-1<0:
        print 'start sec should be later than ',groSatShift+1
    for i in range(startSec, endSec - 1):
        inSec = True
        timeBaseG = groGPSList[i-1][0]
        timeBaseS = satGPSList[i-1-groSatShift][0]
        #print 'GPS',i,timeBaseG-timeBaseS
        while groPulseList[indexGro][0] - timeBaseG < 0:
            indexGro += 1
        while satPulseList[indexSat][0] - timeBaseS < 0:
            indexSat += 1
        x= [float(j*1000000000000.0) for j in range(i-Num,i+Num+1)]
        y=[gpsDisList[j][0] for j in range(i-Num,i+Num+1)]
        distanceFun=lagInterpolation.get_Lxfunc(x,y)
        while inSec:
            groPulseTime=groPulseList[indexGro][0]
            satPulseTime=satPulseList[indexSat][0]
            delay=distanceFun(groPulseTime)*1000*1000000000000.0/ 299792458
            delay=distanceFun(groPulseTime+delay)*1000*1000000000000.0/ 299792458
            detTime=(groPulseTime+delay-timeBaseG)-(satPulseTime-timeBaseS)
            #print detTime,delay,groPulseTime,satPulseTime
            if abs(detTime)>tolerate:
                if detTime>0:
                    indexSat+=1
                else:
                    indexGro+=1
            else:
                coinCount+=1
                coinList.append([groPulseTime,satPulseTime,detTime])
                indexGro+=1
                indexSat+=1
                #print coinList[-1],detTime
            if groPulseList[indexGro][0]>groGPSList[i][0]:
                inSec=False
    print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coinList

#寻找星上发射脉冲，地面接收脉冲的符合对
def satPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec):
    indexGro=0
    indexSat=0
    Num=4
    coinCount=0
    coinList=[]
    tolerate = 10000000
    #satShiftTime=groSatShift*1000000000000.0
    if startSec-groSatShift-1<0:
        print 'start sec should be later than ',groSatShift+1
    for i in range(startSec, endSec - 1):
        inSec = True
        timeBaseG = groGPSList[i-1][0]
        timeBaseS = satGPSList[i-1-groSatShift][0]
        while groPulseList[indexGro][0] - timeBaseG < 0:
            indexGro += 1
        while satPulseList[indexSat][0] - timeBaseS < 0:
            indexSat += 1
        x= [float(j) for j in range(i-Num-groSatShift,i+Num+1-groSatShift)]
        y=[gpsDisList[j][0] for j in range(i-Num,i+Num+1)]
        distanceFun=lagInterpolation.get_Lxfunc(x,y)
        #print x,y,distanceFun(i)
        while inSec:
            groPulseTime=groPulseList[indexGro][0]
            satPulseTime=satPulseList[indexSat][0]
            delay=distanceFun(satPulseTime/1000000000000.0)*1000*1000000000000.0/299792458
            #delay=distanceFun((satPulseTime+delay)/1000000000000.0)*1000*1000000000000.0/299792458
            detTime=(satPulseTime+delay-timeBaseS)-(groPulseTime-timeBaseG)
            # print detTime,delay,groPulseTime,satPulseTime
            if abs(detTime)>tolerate:
                if detTime>0:
                    indexGro+=1
                else:
                    indexSat+=1
            else:
                coinCount+=1
                coinList.append([satPulseTime,groPulseTime,detTime])
                indexGro+=1
                indexSat+=1
                #print coinList[-1],detTime
            if satPulseList[indexSat][0]>satGPSList[i-groSatShift][0]:
                inSec=False
    print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coinList

#将地面发射星上接收的符合对与星上发射地面接收的符合对经行配对，配对原则是两个发射时间小于设定阈值即可配对
#配对后四个时间存到matchList，每行数据的顺序是：地面发射时间TE1、星上接收时间TM2、星上发射时间TM1、地面接收时间TE2
def groSatPulseMatch(groList,satList,groSatShift,threshold):
    nosieThd=30000
    lengthGro=len(groList)
    lengthSat=len(satList)
    indexGro=0
    indexSat=0
    matchList=[]
    matchCount=0
    preTimeG=groList[0][0]-(groSatShift*1000000000000+groList[0][1])
    preTimeS=satList[0][0]+groSatShift*1000000000000-satList[0][1]
    while indexGro<lengthGro:
        detTime=groList[indexGro][0]-(satList[indexSat][0]+groSatShift*1000000000000.0)
        if abs(detTime)>threshold:
            if detTime>0:
                indexSat+=1
            else:
                indexGro+=1
        else:
            tempG=groList[indexGro][0]-(groSatShift*1000000000000+groList[indexGro][1])
            tempS=satList[indexSat][0]+groSatShift*1000000000000-satList[indexSat][1]
            if abs(tempG-preTimeG)<nosieThd and abs(tempS-preTimeS)<nosieThd:
                matchCount+=1
                matchList.append([groList[indexGro][0],groList[indexGro][1],satList[indexSat][0],satList[indexSat][1]])
                preTimeG=tempG
                preTimeS=tempS
            indexSat+=1
            indexGro+=1
        if indexSat>lengthSat-1:
            break
    print '%s matched! '%matchCount
    return matchList

#根据星地互打脉冲时间结果计算距离，输出时间、距离，计算模型参考：提高深空异步激光测距精度方法研究
def asynLaserRanging(matchList,groSatShift):
    length=len(matchList)
    rangingList=[]
    tempR=[]
    iterNum=3
    c=299792458.0
    for i in range(length):
        t=(matchList[i][1]+matchList[i][2])/(2*1000000000000.0)+groSatShift
        R=(matchList[i][1]+matchList[i][3]-matchList[i][0]-matchList[i][2])*c/(2*1000000000000.0)
        rangingList.append([t,R])
    fitSmooth(rangingList,80,1)
    for j in range(iterNum):
        for i in range(length):
            if i==0:
                detR=(rangingList[i+1][1]-rangingList[i][1])/(rangingList[i+1][0]-rangingList[i][0])
            elif i<length-1 and i>0:
                detR=(rangingList[i+1][1]-rangingList[i-1][1])/(rangingList[i+1][0]-rangingList[i-1][0])
            elif i == length:
                detR=(rangingList[i][1]-rangingList[i-1][1])/(rangingList[i][0]-rangingList[i-1][0])
            Tau=(matchList[i][3]-matchList[i][0]-(matchList[i][1]-matchList[i][2]))/(2+detR/(c-detR))/1000000000000.0
            R=(matchList[i][1]+matchList[i][3]-matchList[i][0]-matchList[i][2])*c/(2*1000000000000.0)
            tempR.append(R-detR*((matchList[i][3]-matchList[i][0])/1000000000000.0-Tau)/2.0)
        for i in range(length):
            rangingList[i][1]=tempR[i]
        del tempR[:]
        fitSmooth(rangingList,80,1)
    print 'iterate %s times, asyn laser ranging is finished!'%iterNum
    return rangingList

def fitSmooth(rangingList,segment,order):
    t=[]
    R=[]
    length=len(rangingList)
    for i in range(int(length/segment)):
        for j in range(segment):
            t.append(rangingList[i*segment+j][0])
            R.append(rangingList[i*segment+j][1])
        mat=fitting.polyLeastFit(t,R,order)
        for k in range(segment):
            rangingList[i*segment+k][1]=fitting.polyLeastFitCal([rangingList[i*segment+k][0]],mat)[0]
        del t[:]
        del R[:]
    reamin=length-int(length/segment)*segment
    if reamin>0:
        for ii in range(int(length/segment)*segment,length):
            t.append(rangingList[ii][0])
            R.append(rangingList[ii][1])
        mat=fitting.polyLeastFit(t,R,order)
        for jj in range(int(length/segment)*segment,length):
            rangingList[jj][1]=fitting.polyLeastFitCal([rangingList[jj][0]],mat)[0]

def groPulseCoincidenceTest():
    startSec=260
    endSec=265
    groSatShift=240
    groFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_1064.txt',encoding='utf-8')
    satFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\0829AliSatellite_channel_27_1064.txt',encoding='utf-8')
    groGPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_GPS.txt',encoding='utf-8')
    satGPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\0829AliSatellite_channel_5_GPS.txt',encoding='utf-8')
    gpsDisFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\GPS_Dis.txt',encoding='utf-8')
    saveFile=groFile[:-4]+'_%s-%s_coincidence.txt'%(startSec,endSec)
    groList=fileToList.fileToList(groFile)
    satList=fileToList.fileToList(satFile)
    groGPSList=fileToList.fileToList(groGPSFile)
    satGPSList=fileToList.fileToList(satGPSFile)
    gpsDisList=fileToList.fileToList(gpsDisFile)
    groPulseList,satPulseList,groGPSList,satGPSList=timeCalibrate(groList,satList,groGPSList,satGPSList)
    coinList=groPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec)
    fileToList.listToFile(coinList,saveFile)

def satPulseCoincidenceTest():
    startSec=260
    endSec=265
    groSatShift=240
    groFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_532_filtered_reflectFiltered.txt',encoding='utf-8')
    satFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\0829AliSatellite_channel_10_532.txt',encoding='utf-8')
    groGPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_GPS.txt',encoding='utf-8')
    satGPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\0829AliSatellite_channel_5_GPS.txt',encoding='utf-8')
    gpsDisFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\GPS_Dis.txt',encoding='utf-8')
    saveFile=groFile[:-4]+'_%s-%s_coincidence.txt'%(startSec,endSec)
    groList=fileToList.fileToList(groFile)
    satList=fileToList.fileToList(satFile)
    groGPSList=fileToList.fileToList(groGPSFile)
    satGPSList=fileToList.fileToList(satGPSFile)
    gpsDisList=fileToList.fileToList(gpsDisFile)
    groPulseList,satPulseList,groGPSList,satGPSList=timeCalibrate(groList,satList,groGPSList,satGPSList)
    coinList=satPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec)
    fileToList.listToFile(coinList,saveFile)

def groSatPulseMatchTest():
    groCoinFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_1064_260-265_coincidence.txt',encoding='utf-8')
    satCoinFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_532_filtered_reflectFiltered_260-265_coincidence.txt',encoding='utf-8')
    groList=fileToList.fileToList(groCoinFile)
    satList=fileToList.fileToList(satCoinFile)
    saveFile=groCoinFile[:-4]+'_match.txt'
    matchList=groSatPulseMatch(groList,satList,240,30000000)
    fileToList.listToFile(matchList,saveFile)

def asynLaserRangingTest():
    matchFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_1064_260-265_coincidence_match.txt',encoding='utf-8')
    saveFile=matchFile[:-4]+'_ranging.txt'
    matchList=fileToList.fileToList(matchFile)
    rangingList=asynLaserRanging(matchList,240)
    fileToList.listToFileLong(rangingList,saveFile)

if __name__=='__main__':
    # groPulseCoincidenceTest()
    # satPulseCoincidenceTest()
    # groSatPulseMatchTest()
    asynLaserRangingTest()