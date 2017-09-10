#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import clockTimeCalibrate
import fitting
import lagInterpolation
import fileToList
import atmosphericDelayCorrect

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

def timeGPSFactor(groGPSList,satGPSList,window):
    groGPSFactorList=clockTimeCalibrate.clockTimeFactorSecGro(groGPSList)
    satGPSFactorList=clockTimeCalibrate.clockTimeFactorSecSat(satGPSList,window)
    return groGPSFactorList,satGPSFactorList

#寻找地面发射脉冲，星上接收到的脉冲的符合对
def groPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec):
    indexGro=0
    indexSat=0
    Num=4
    coinCount=0
    coinList=[]
    tolerate = 20000000
    windows=1500000
    offset=0
    #satShiftTime=groSatShift*1000000000000.0
    groGPSFactorList,satGPSFactorList=timeGPSFactor(groGPSList,satGPSList,50000)
    if startSec-groSatShift-1<0:
        print 'start sec should be later than ',groSatShift+1
    timeBaseG = groGPSList[startSec-1][0]
    timeBaseS = satGPSList[startSec-1-groSatShift][0]
    while groPulseList[indexGro][0] - timeBaseG < 0:
            indexGro += 1
    while satPulseList[indexSat][0] - timeBaseS < 0:
            indexSat += 1
    for i in range(startSec, endSec - 1):
        inSec = True
        x= [float(j*1000000000000.0) for j in range(i-Num,i+Num+1)]
        y=[gpsDisList[j][0] for j in range(i-Num,i+Num+1)]
        distanceFun=lagInterpolation.get_Lxfunc(x,y)
        while inSec:
            groPulseTime=i*1000000000000.0+(groPulseList[indexGro][0]-timeBaseG)/(groGPSFactorList[i-1]/1000000000000.0)
            satPulseTime=i*1000000000000.0+(satPulseList[indexSat][0]-timeBaseS)/(satGPSFactorList[i-1-groSatShift]/1000000000000.0)
            delay=distanceFun(groPulseTime)*1000*1000000000000.0/ 299792458
            delay=distanceFun(groPulseTime+delay)*1000*1000000000000.0/ 299792458
            detTime=groPulseTime+delay-satPulseTime
            #print detTime,delay,groPulseTime,satPulseTime
            if abs(detTime-offset)>tolerate:
                if detTime>0:
                    indexSat+=1
                else:
                    indexGro+=1
            else:
                coinCount+=1
                coinList.append([groPulseList[indexGro][0],satPulseList[indexSat][0],groPulseTime,satPulseTime,detTime])
                tolerate=abs(detTime-offset)+windows
                offset=detTime
                indexGro+=1
                indexSat+=1
                #print coinList[-1],detTime
            if satPulseList[indexSat][0]>satGPSList[i-groSatShift][0] and groPulseList[indexGro][0]>groGPSList[i][0]:
                timeBaseS = satGPSList[i-groSatShift][0]
                timeBaseG=groGPSList[i][0]
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
    tolerate = 20000000
    windows=1500000
    offset=0
    groGPSFactorList,satGPSFactorList=timeGPSFactor(groGPSList,satGPSList,50000)
    if startSec-groSatShift-1<0:
        print 'start sec should be later than ',groSatShift+1
    timeBaseG = groGPSList[startSec-1][0]
    timeBaseS = satGPSList[startSec-1-groSatShift][0]
    while groPulseList[indexGro][0] - timeBaseG < 0:
            indexGro += 1
    while satPulseList[indexSat][0] - timeBaseS < 0:
            indexSat += 1
    for i in range(startSec, endSec - 1):
        inSec = True
        x= [float(j) for j in range(i-Num,i+Num+1)]
        y=[gpsDisList[j][0] for j in range(i-Num,i+Num+1)]
        distanceFun=lagInterpolation.get_Lxfunc(x,y)
        while inSec:
            groPulseTime=i*1000000000000.0+(groPulseList[indexGro][0]-timeBaseG)/(groGPSFactorList[i-1]/1000000000000.0)
            satPulseTime=i*1000000000000.0+(satPulseList[indexSat][0]-timeBaseS)/(satGPSFactorList[i-1-groSatShift]/1000000000000.0)
            delay=distanceFun(satPulseTime/1000000000000.0)*1000*1000000000000.0/299792458
            delay=distanceFun((satPulseTime+delay)/1000000000000.0)*1000*1000000000000.0/299792458
            detTime=satPulseTime+delay-groPulseTime
            # print detTime,delay,groPulseTime,satPulseTime
            if abs(detTime-offset)>tolerate:
                if detTime>0:
                    indexGro+=1
                else:
                    indexSat+=1
            else:
                coinCount+=1
                coinList.append([satPulseList[indexSat][0],groPulseList[indexGro][0],satPulseTime,groPulseTime,detTime])
                tolerate=abs(detTime-offset)+windows
                offset=detTime
                indexGro+=1
                indexSat+=1
                #print coinList[-1],detTime
            if satPulseList[indexSat][0]>satGPSList[i-groSatShift][0] and groPulseList[indexGro][0]>groGPSList[i][0]:
                timeBaseS = satGPSList[i-groSatShift][0]
                timeBaseG=groGPSList[i][0]
                inSec=False
    print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coinList

#将地面发射星上接收的符合对与星上发射地面接收的符合对经行配对，配对原则是两个发射时间小于设定阈值即可配对
#配对后四个时间存到matchList，每行数据的顺序是：地面发射时间TE1、星上接收时间TM2、星上发射时间TM1、地面接收时间TE2
def groSatPulseMatch(groList,satList,groSatShift,threshold):
    nosieThd=300000
    lengthGro=len(groList)
    lengthSat=len(satList)
    indexGro=0
    indexSat=0
    matchList=[]
    matchCount=0
    while indexGro<lengthGro:
        # detTime=groList[indexGro][0]-(satList[indexSat][0]+groSatShift*1000000000000.0)
        detTime=groList[indexGro][2]-satList[indexSat][2]
        if abs(detTime)>threshold:
            if detTime>0:
                indexSat+=1
            else:
                indexGro+=1
        else:
            matchCount+=1
            # matchList.append([groList[indexGro][0],groList[indexGro][1],satList[indexSat][0],satList[indexSat][1]])
            matchList.append([groList[indexGro][0],groList[indexGro][1],satList[indexSat][0],satList[indexSat][1],
                              groList[indexGro][2],groList[indexGro][3],satList[indexSat][2],satList[indexSat][3]])

            indexSat+=1
            indexGro+=1
        if indexSat>lengthSat-1:
            break
    print '%s matched! '%matchCount
    matchList=fitfilter(matchList,50,1,1,groSatShift)
    return matchList

#根据星地互打脉冲时间结果计算距离，输出时间、距离，计算模型参考：提高深空异步激光测距精度方法研究
def asynLaserRanging(matchList,groSatShift):
    length=len(matchList)
    rangingList=[]
    tempR=[]
    iterNum=3
    c=299792458.0
    smoothNum=8
    for i in range(length):
        # t=(matchList[i][1]+matchList[i][2])/(2*1000000000000.0)+groSatShift
        # R=(matchList[i][1]+matchList[i][3]-matchList[i][0]-matchList[i][2])*c/(2*1000000000000.0)
        # tau=(matchList[i][3]-matchList[i][0]-(matchList[i][1]-matchList[i][2]))
        # T=matchList[i][3]-matchList[i][0]
        t=(matchList[i][4]+matchList[i][7])/(2*1000000000000.0)
        R=(matchList[i][5]+matchList[i][7]-matchList[i][4]-matchList[i][6])*c/(2*1000000000000.0)
        tau=(matchList[i][7]-matchList[i][4]-(matchList[i][5]-matchList[i][6]))
        T=matchList[i][7]-matchList[i][4]
        rangingList.append([t,R,tau,T,R])
    #TODO  数点合成一个点，平滑滤波，但是需注意数据不能缺失大段，否则会引入误差，待改善
    rangingList=fitSmooth(rangingList,50,1)
    length=len(rangingList)
    tx=[]
    ry=[]
    for j in range(iterNum):
        for i in range(length):
            #TODO 平滑速度
            if i<=smoothNum:
                detR=(rangingList[i+1][1]-rangingList[i][1])/(rangingList[i+1][0]-rangingList[i][0])
            elif i<length-smoothNum :
                for index in range(i-smoothNum,i+smoothNum):
                    tx.append(rangingList[index][0])
                    ry.append(rangingList[index][1])
                mat=fitting.polyLeastFit(tx,ry,1)
                detR=(fitting.polyLeastFitCal([rangingList[i+1][0]],mat)[0]-fitting.polyLeastFitCal([rangingList[i-1][0]],mat)[0])/(rangingList[i+1][0]-rangingList[i-1][0])
                del tx[:]
                del ry[:]
            else:
                detR=(rangingList[i][1]-rangingList[i-1][1])/(rangingList[i][0]-rangingList[i-1][0])
            Tau=rangingList[i][2]/(2+detR/(c-detR))/1000000000000.0
            tempR.append(rangingList[i][4]+detR*(rangingList[i][3]/1000000000000.0-Tau)/2.0)
            # print j,detR
        for i in range(length):
            rangingList[i][1]=tempR[i]
        del tempR[:]
        #newList=fitSmooth(rangingList,80,1)
    print 'iterate %s times, asyn laser ranging is finished!'%iterNum
    return rangingList

def fitSmooth(rangingList,segment,order):
    t=[]
    R=[]
    newList=[]
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
        newList.append(rangingList[i*segment+int(segment/2)])
    reamin=length-int(length/segment)*segment
    if reamin>0:
        for ii in range(int(length/segment)*segment,length):
            t.append(rangingList[ii][0])
            R.append(rangingList[ii][1])
        mat=fitting.polyLeastFit(t,R,order)
        for jj in range(int(length/segment)*segment,length):
            rangingList[jj][1]=fitting.polyLeastFitCal([rangingList[jj][0]],mat)[0]
        newList.append(rangingList[int(length/segment)*segment+int(reamin/2)])
    return newList

def fitfilter(matchList,segment,order,groSatShift,windows):
    t=[]
    R=[]
    filterList=[]
    count=0
    c=299792458.0
    length=len(matchList)
    for i in range(int(length/segment)):
        for j in range(segment):
            index=i*segment+j
            t.append((matchList[index][1]+matchList[index][2])/(2*1000000000000.0)+groSatShift)
            R.append((matchList[index][1]+matchList[index][3]-matchList[index][0]-matchList[index][2])*c/(2*1000000000000.0))
        mat=fitting.polyLeastFit(t,R,order)
        for k in range(segment):
            det=R[k]-fitting.polyLeastFitCal([t[k]],mat)[0]
            if abs(det)<windows:
                filterList.append(matchList[i*segment+k])
            else:count+=1
        del t[:]
        del R[:]
        #newList.append(rangingList[i*segment+int(segment/2)])
    reamin=length-int(length/segment)*segment
    # if reamin>0:
    #     for index in range(int(length/segment)*segment,length):
    #         t.append((matchList[index][1]+matchList[index][2])/(2*1000000000000.0)+groSatShift)
    #         R.append((matchList[index][1]+matchList[index][3]-matchList[index][0]-matchList[index][2])*c/(2*1000000000000.0))
    #
    #     mat=fitting.polyLeastFit(t,R,order)
    #     for jj in range(int(length/segment)*segment,length):
    #         det=R[jj]-fitting.polyLeastFitCal([t[jj]],mat)[0]
    #         if abs(det)<windows:
    #             filterList.append(matchList[jj])
    #         else:
    #             count+=1
        #newList.append(rangingList[int(length/segment)*segment+int(reamin/2)])
    print 'fit filtered! %s points moved out!'%(count+reamin)
    return filterList

def reduceSec(rangingList):
    startSec=int(rangingList[0][0])+1
    endSec=int(rangingList[-1][0])
    reduceList=[]
    t=[]
    r=[]
    fitNum=5
    index=0
    for sec in range(startSec,endSec+1):
        while rangingList[index][0]<sec:
            index+=1
        for i in range(index-fitNum,index+fitNum):
            t.append(rangingList[i][0])
            r.append(rangingList[i][1])
        mat=fitting.polyLeastFit(t,r,1)
        reduceList.append([sec,fitting.polyLeastFitCal([float(sec)],mat)[0]])
        del t[:]
        del r[:]
    return reduceList

def atmCorrect(rangingList,atmList):
    length=len(rangingList)
    sec=int(rangingList[0][0])
    index=0
    while int(atmList[index][0])<sec:
        index+=1
    for i in range(length):
        delay=atmosphericDelayCorrect.MPAtmDelayModelCal(1.064,32.333,5045,45270,5,30,float(atmList[index][1]))
        rangingList[i][1]=rangingList[i][1]-delay
        index+=1


def groPulseCoincidenceTest():
    startSec=245
    endSec=500
    groSatShift=240
    groFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_1064.txt',encoding='utf-8')
    satFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\0829AliSatellite_channel_27_1064.txt',encoding='utf-8')
    groGPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_GPS.txt',encoding='utf-8')
    satGPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\0829AliSatellite_channel_5_GPS.txt',encoding='utf-8')
    gpsDisFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\GPS_Dis.txt',encoding='utf-8')
    saveFile=groFile[:-4]+'_%s-%s_coincidence_new.txt'%(startSec,endSec)
    groPulseList=fileToList.fileToList(groFile)
    satPulseList=fileToList.fileToList(satFile)
    groGPSList=fileToList.fileToList(groGPSFile)
    satGPSList=fileToList.fileToList(satGPSFile)
    gpsDisList=fileToList.fileToList(gpsDisFile)

    # groPulseList,satPulseList,groGPSList,satGPSList=timeCalibrate(groList,satList,groGPSList,satGPSList)
    coinList=groPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec)
    fileToList.listToFile(coinList,saveFile)

def satPulseCoincidenceTest():
    startSec=245
    endSec=500
    groSatShift=240
    groFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_532_filtered_reflectFiltered.txt',encoding='utf-8')
    satFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\0829AliSatellite_channel_10_532.txt',encoding='utf-8')
    groGPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_GPS.txt',encoding='utf-8')
    satGPSFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\0829AliSatellite_channel_5_GPS.txt',encoding='utf-8')
    gpsDisFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\GPS_Dis.txt',encoding='utf-8')
    saveFile=groFile[:-4]+'_%s-%s_coincidence_new.txt'%(startSec,endSec)
    groPulseList=fileToList.fileToList(groFile)
    satPulseList=fileToList.fileToList(satFile)
    groGPSList=fileToList.fileToList(groGPSFile)
    satGPSList=fileToList.fileToList(satGPSFile)
    gpsDisList=fileToList.fileToList(gpsDisFile)
    # groPulseList,satPulseList,groGPSList,satGPSList=timeCalibrate(groList,satList,groGPSList,satGPSList)
    coinList=satPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec)
    fileToList.listToFile(coinList,saveFile)

def groSatPulseMatchTest():
    groCoinFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_1064_245-500_coincidence_new.txt',encoding='utf-8')
    satCoinFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_532_filtered_reflectFiltered_245-500_coincidence_new.txt',encoding='utf-8')
    groList=fileToList.fileToList(groCoinFile)
    satList=fileToList.fileToList(satCoinFile)
    saveFile=groCoinFile[:-4]+'_match.txt'
    matchList=groSatPulseMatch(groList,satList,240,90000000)
    fileToList.listToFile(matchList,saveFile)

def asynLaserRangingTest():
    matchFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\20170830031232_fineParse_1064_245-500_coincidence_new_match.txt',encoding='utf-8')
    atmFile=unicode('E:\Experiment Data\时频传输数据处理\阿里测试\\170829\\俯仰角.txt',encoding='utf-8')
    saveFile=matchFile[:-4]+'_ranging.txt'
    saveRedFile=matchFile[:-4]+'_rangingSec.txt'
    matchList=fileToList.fileToList(matchFile)
    atmList=fileToList.fileToList(atmFile)
    rangingList=asynLaserRanging(matchList,240)
    reduceList=reduceSec(rangingList)
    # atmCorrect(reduceList,atmList)
    fileToList.listToFileLong(rangingList,saveFile)
    fileToList.listToFileLong(reduceList,saveRedFile)

if __name__=='__main__':
    # groPulseCoincidenceTest()
    # satPulseCoincidenceTest()
    # groSatPulseMatchTest()
    asynLaserRangingTest()