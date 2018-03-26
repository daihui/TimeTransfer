#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import clockTimeCalibrate
import fitting
import lagInterpolation
import fileToList
import atmosphericDelayCorrect
import numpy

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

def timeGPSFactor(groGPSList,satGPSList,Num,window):
    groGPSFactorList=clockTimeCalibrate.clockTimeFactorSecGro(groGPSList,Num)
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
    windows=250000
    offset=0
    #satShiftTime=groSatShift*1000000000000.0

    #时间修正方法1
    groGPSFactorList,satGPSFactorList=timeGPSFactor(groGPSList,satGPSList,5,50000)

    #时间修正方法2
    # NG = len(groGPSList)
    # secG = [float(i + 1) for i in range(NG)]
    # timeG = [groGPSList[i][0] for i in range(NG)]
    # matG = numpy.polyfit(secG, timeG, 2)
    # FG = numpy.poly1d(matG)
    # NS = len(satGPSList)
    # secS = [float(i + 1) for i in range(NS)]
    # timeS = [satGPSList[i][0] for i in range(NS)]
    # matS = numpy.polyfit(secS, timeS, 2)
    # FS = numpy.poly1d(matS)

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
            #时间修正方法1
            groPulseTime=i*1000000000000.0+(groPulseList[indexGro][0]-timeBaseG)/(groGPSFactorList[i-1]/1000000000000.0)
            satPulseTime=i*1000000000000.0+(satPulseList[indexSat][0]-timeBaseS)/(satGPSFactorList[i-1-groSatShift]/1000000000000.0)

            #时间修正方法2
            # groPulseTime =FG(groPulseList[indexGro][0]/1000000000000.0)
            # satPulseTime=FS(satPulseList[indexSat][0]/1000000000000.0)
            delay=distanceFun(groPulseTime)*1000*1000000000000.0/ 299792458
            delay=distanceFun(groPulseTime+delay)*1000*1000000000000.0/ 299792458
            # detTime=groPulseTime+delay-satPulseTime-(timeBaseG-timeBaseS)
            detTime = groPulseTime + delay - satPulseTime
            # print detTime,delay,groPulseTime,groPulseList[indexGro][0],satPulseTime,satPulseList[indexSat][0]
            if abs(detTime-offset)>tolerate:
                if detTime>0:
                    indexSat+=1
                else:
                    indexGro+=1
            else:
                # print detTime, offset, detTime - offset
                coinCount+=1
                coinList.append([groPulseList[indexGro][0],satPulseList[indexSat][0],groPulseTime,satPulseTime,detTime])
                tolerate=abs(detTime-offset)+windows
                offset=detTime
                indexGro+=1
                indexSat+=1

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
    windows=250000
    offset=0
    groGPSFactorList,satGPSFactorList=timeGPSFactor(groGPSList,satGPSList,5,50000)
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
    matchList=fitfilter(matchList,50,1,groSatShift,1)
    return matchList

#将地面相邻两个激光脉冲记下时间，与星上收到的时间匹配，得到四个时间符合，计算卫星径向速度v，以及相对时间因子K'/K
def nearMatch(groList,satList,groSatShift,threshold):
    c = 299792458.0
    lengthGro = len(groList)
    lengthSat = len(satList)
    indexGro = 0
    indexSat = 0
    matchList = []
    nearMatchList=[]
    result=[]
    nearMatchCount = 0
    while indexGro < lengthGro:
        detTime = groList[indexGro][1] - satList[indexSat][0]
        if abs(detTime) > threshold:
            if detTime > 0:
                indexSat += 1
            else:
                indexGro += 1
        else:
            matchList.append([groList[indexGro][0],groList[indexGro][1],satList[indexSat][0],satList[indexSat][1]])

            indexSat += 1
            indexGro += 1
        if indexSat > lengthSat - 1:
            break
    nearNum = 80
    pairsNum = len(matchList) / nearNum / 2
    for i in range(pairsNum):
        for j in range(nearNum):
            nearMatchList.append(matchList[2*nearNum*i+j]+matchList[2*nearNum*i+nearNum+j])
            nearMatchCount+=1
    print '%s pairs near match'%nearMatchCount
    # print len(nearMatchList)
    for i in range(len(nearMatchList)):
        tG=(nearMatchList[i][0]+nearMatchList[i][4])/2.0/1000000000000.0
        tG1064=nearMatchList[i][4]-nearMatchList[i][0]
        tG532=nearMatchList[i][7]-nearMatchList[i][3]
        tS1064=nearMatchList[i][5]-nearMatchList[i][1]
        tS532=nearMatchList[i][6]-nearMatchList[i][2]
        beta=tG532*tS1064/(tG1064*tS532)
        v=c*(beta-1)/(beta+1)
        relFactor=(1+v/c)*tS532/tG532
        # relFactor2 = (1 - v / c) * tS1064 / tG1064
        # relFactor=(relFactor1+relFactor2)/2
        result.append([tG,v,relFactor])
        #print tG,beta,v,(1+v/c)*tS532/tG532, (1 - v / c) * tS1064 / tG1064
    return result

#matchList每行数据的顺序是：
# 第一行地面发射时间TE1/t1、星上接收时间TM2/t3、星上发射时间TM1/t5、地面接收时间TE2/t7
# 第二行地面发射时间TE1/t2、星上接收时间TM2/t4、星上发射时间TM1/t6、地面接收时间TE2/t8
# 计算距离R0,速度V，钟差tau，比例因子K, 计算公式参考 文献：Birnbaum, K. M., Chen, Y., & Hemmati, H. (2010, February). Precision optical ranging by paired one-way time of flight. In Free-Space Laser Communication Technologies
def aysnLaserBKC(matchList,groSatShift,smoothNum,groGPSList,satGPSList):
    length = len(matchList)
    groSatShift=groSatShift*1000000000000.0
    c = 299792458.0
    paraterList = []
    sec=0
    startSec=int(matchList[0][0]/1000000000000.0)
    secG = int(matchList[0][0] / 1000000000000.0)
    secS = int(matchList[0][2] / 1000000000000.0)
    for i in range(length-smoothNum-10):
        t0 = matchList[i][0] - groGPSList[secG - 1][0]
        t3 = matchList[i][1] - satGPSList[secS - 1][0]  - t0
        t5 = matchList[i + 1][2] - satGPSList[secS - 1][0]  - t0
        t7 = matchList[i + 1][3] - groGPSList[secG - 1][0] - t0
        t2 = matchList[i + smoothNum][0] - groGPSList[secG - 1][0] - t0
        t4 = matchList[i + smoothNum][1] - satGPSList[secS - 1][0]  - t0
        t6 = matchList[i + smoothNum + 1][2] - satGPSList[secS - 1][0] - t0
        t8 = matchList[i + smoothNum + 1][3] - groGPSList[secG - 1][0] - t0

        t1=0
        K=((t2-t1)/(t4-t3)+(t8-t7)/(t6-t5))/2
        V=c*(((t4-t3)*(t8-t7)-(t6-t5)*(t2-t1))/((t4-t3)*(t8-t7)+(t6-t5)*(t2-t1)))
        # tau=((t2*t3-t1*t4)/(t4-t3)+(t8*t5-t7*t6)/(t6-t5))/2
        tau=(c*(t1+t2+t7+t8)-K*(c-V)*(t3+t4)-K*(c+V)*(t5+t6))/(-4*c)
        # R0=c*(((t2*t3-t1*t4)*(t8-t7)+(t8*t5-t7*t6)*(t2-t1))/((t4-t3)*(t8-t7)+(t6-t5)*(t2-t1)))/1000000000000.0
        R1=((c-V)*(K*(t3+t4)-2*tau)-c*(t1+t2))/(2*1000000000000.0)
        R2=(c*(t7+t8)-(c+V)*(K*(t5+t6)-2*tau))/(2*1000000000000.0)
        R0=(R1+R2)/2
        paraterList.append([t0/1000000000000.0+secG,R0,V,tau,K])
        if i%100==0:
            print t0/1000000000000.0+secG,R0,V,tau,K
    print 'Parameters: R0,V,tau,K calculated! '
    return paraterList

#平滑parameterList,多点拟合
def BKCSmooth(parameterList,fitNum,order,smoothNum):
    length=len(parameterList)
    smoothList=[]
    t=[]
    R=[]
    V=[]
    tau=[]
    K=[]
    for i in range(int((length-2*fitNum)/smoothNum)):
        for j in range(2*fitNum+1):
            t.append(parameterList[i*smoothNum+j][0])
            R.append(parameterList[i*smoothNum+j][1])
            V.append(parameterList[i*smoothNum+j][2])
            tau.append(parameterList[i*smoothNum+j][3])
            K.append(parameterList[i*smoothNum+j][4])
        matR = fitting.polyLeastFit(t, R, order)
        matV = fitting.polyLeastFit(t, V, order)
        mattau = fitting.polyLeastFit(t, tau, order)
        matK = fitting.polyLeastFit(t, K, order)
        del t[:]
        del R[:]
        del V[:]
        del tau[:]
        del K[:]
        smoothT=[parameterList[i*smoothNum+fitNum][0]]
        fitR=fitting.polyLeastFitCal(smoothT,matR)
        fitV = fitting.polyLeastFitCal(smoothT, matV)
        fitTau = fitting.polyLeastFitCal(smoothT, mattau)
        fitK = fitting.polyLeastFitCal(smoothT, matK)
        smoothList.append([smoothT[0],fitR[0],fitV[0],fitTau[0],fitK[0]])
        # print smoothT[0],fitR[0],fitV[0],fitTau[0],fitK[0]
    print "parameterList have be smoothed!"
    return smoothList



#根据星地互打脉冲时间结果计算距离，输出时间、距离，计算模型参考：Degnan
def asynLaserRanging(matchList,groSatShift):
    length=len(matchList)
    rangingList=[]
    tempR=[]
    iterNum=1
    c=299792458.0
    smoothNum=20
    for i in range(length):
        # matchList，每行数据的顺序是：地面发射时间TE1、星上接收时间TM2、星上发射时间TM1、地面接收时间TE2
        # t=(matchList[i][1]+matchList[i][2])/(2*1000000000000.0)+groSatShift
        # R=(matchList[i][1]+matchList[i][3]-matchList[i][0]-matchList[i][2])*c/(2*1000000000000.0)
        # tau=(matchList[i][3]-matchList[i][0]-(matchList[i][1]-matchList[i][2]))
        # T=matchList[i][3]-matchList[i][0]
        # clk=(matchList[i][1]-matchList[i][0]-(matchList[i][3]-matchList[i][2]))/2+groSatShift*1000000000000

        #公式来源：提高深空异步激光测距
        # t = (matchList[i][5] + matchList[i][6]) / (2 * 1000000000000.0)
        # R=(matchList[i][5]+matchList[i][7]-matchList[i][4]-matchList[i][6])*c/(2*1000000000000.0)
        # tau=(matchList[i][7]-matchList[i][4]-(matchList[i][5]-matchList[i][6]))
        # T=matchList[i][7]-matchList[i][4]
        # clk = (matchList[i][5] - matchList[i][4] - (matchList[i][7] - matchList[i][6])) / 2 + groSatShift * 1000000000000

        # 公式来源：Degnan
        #t = (matchList[i][3] + matchList[i][0]) / (2 * 1000000000000.0)
        t = (matchList[i][7] + matchList[i][4]) / (2 * 1000000000000.0)
        R=(matchList[i][5]+matchList[i][7]-matchList[i][4]-matchList[i][6])*c/(2*1000000000000.0)
        # R = (matchList[i][1] + matchList[i][3] - matchList[i][0] - matchList[i][2]) * c / (2 * 1000000000000.0)
        #tau=(matchList[i][3]-matchList[i][0]-(matchList[i][1]-matchList[i][2]))
        tau = (matchList[i][7] - matchList[i][4] - (matchList[i][5] - matchList[i][6]))
        # T=matchList[i][3]-matchList[i][0]
        clk = (matchList[i][1] + matchList[i][2] - (matchList[i][0] + matchList[i][3])) / 2 + groSatShift * 1000000000000
        # detSat=matchList[i][5]-matchList[i][6]
        detSat = matchList[i][1] - matchList[i][2]#被动式
        rangingList.append([t, R, tau, clk,detSat])
        # rangingList.append([t,R,tau,T,R,clk])
        #print (matchList[i][4]+matchList[i][7])-(matchList[i][5]+matchList[i][6])
    #TODO  数点合成一个点，平滑滤波，但是需注意数据不能缺失大段，否则会引入误差，待改善

    rangingList = fitSmooth(rangingList, 100, 2)
    # rangingList=reducebyfactor(rangingList,10)
    rangingList, residualList = rangefilter(rangingList, 30, 4, 0.2)

    length=len(rangingList)
    tx=[]
    ry=[]
    for j in range(iterNum):
        for i in range(length):
            #TODO 平滑速度
            if i<=smoothNum:
                detR=(rangingList[i][1]-rangingList[i+1][1])/(rangingList[i+1][0]-rangingList[i][0])
            elif i<length-smoothNum :
                for index in range(i-smoothNum,i+smoothNum):
                    tx.append(rangingList[index][0])
                    ry.append(rangingList[index][1])
                mat=fitting.polyLeastFit(tx,ry,5)
                tR=[]
                detRList=[]
                # for k in range(i-smoothNum/2,i+smoothNum):
                #     tR.append(rangingList[k][0])
                #     detRList.append((fitting.polyLeastFitCal([rangingList[k-1][0]],mat)[0]-fitting.polyLeastFitCal([rangingList[k+1][0]],mat)[0])/(rangingList[k+1][0]-rangingList[k-1][0]))
                # matV=fitting.polyLeastFit(tR,detRList,2)
                detR=(fitting.polyLeastFitCal([rangingList[i-1][0]],mat)[0]-fitting.polyLeastFitCal([rangingList[i+1][0]],mat)[0])/(rangingList[i+1][0]-rangingList[i-1][0])
                # detRV=fitting.polyLeastFitCal([rangingList[i][0]],matV)[0]
                # print detR,detRV,detR-detRV
                del tx[:]
                del ry[:]
                del tR[:]
                del detRList[:]
            else:
                detR=(rangingList[i-1][1]-rangingList[i][1])/(rangingList[i][0]-rangingList[i-1][0])
            #提高
            # Tau=rangingList[i][2]/(2+detR/(c-detR))/1000000000000.0
            # tempR.append(rangingList[i][4]-detR*(rangingList[i][3]/1000000000000.0-Tau)/2.0)
            #Degnan
            Tau = rangingList[i][2] / (2 + 2*detR / c )
            # Tba=rangingList[i][3]-Tau*detR/c
            # Tba = rangingList[i][3] - rangingList[i][4] * detR / (2*c)
            # print detR,Tau*detR/c,rangingList[i][4] * detR / (2*c)
            if j==iterNum-1:
                rangingList[i][2]=Tau
                # rangingList[i][3]=Tba
                rangingList[i]=(rangingList[i]+[detR,Tau*detR/c,rangingList[i][4] * detR / (2*c)])
            # print '%s\t%s\t%s'%(j,rangingList[i][0],detR)
        # for i in range(length):
        #     rangingList[i][1]=tempR[i]
        # del tempR[:]
    print 'iterate %s times, asyn laser ranging is finished!'%iterNum
    rangingList, residualList = rangefilter(rangingList, 30, 4, 0.15)
    # rangingList = fitSmooth(rangingList, 10, 3)
    # rangingList = rangefilter(rangingList, 30, 5, 0.08)

    return rangingList,residualList

#平滑 rangingList ([t,R,tau,T,R,clk])
def fitSmooth(rangingList,segment,order):
    t=[]
    R=[]
    tau=[]
    T=[]
    clk=[]
    detSat=[]
    newList=[]
    length=len(rangingList)
    for i in range(int(length/segment)):
        for j in range(segment):
            t.append(rangingList[i*segment+j][0])
            R.append(rangingList[i*segment+j][1])
            # clk.append(rangingList[i * segment + j][2])
            clk.append(rangingList[i * segment + j][3])
            detSat.append(rangingList[i * segment + j][4])
        matR=fitting.polyLeastFit(t,R,order)
        # matTau = fitting.polyLeastFit(t, tau, order)
        matclk = fitting.polyLeastFit(t, clk, order)
        matD = fitting.polyLeastFit(t, detSat, order)
        # for k in range(segment):
        rangingList[i*segment+int(segment/2)][1]=fitting.polyLeastFitCal([rangingList[i*segment+int(segment/2)][0]],matR)[0]
        # rangingList[i * segment + int(segment / 2)][2] = fitting.polyLeastFitCal([rangingList[i * segment + int(segment / 2)][0]], matTau)[0]
        rangingList[i * segment + int(segment / 2)][3] = fitting.polyLeastFitCal([rangingList[i * segment + int(segment / 2)][0]], matclk)[0]
        rangingList[i * segment + int(segment / 2)][4] = fitting.polyLeastFitCal([rangingList[i * segment + int(segment / 2)][0]], matD)[0]

        # rangingList[i * segment + int(segment / 2)][4] =rangingList[i*segment+int(segment/2)][1]
        del t[:]
        del R[:]
        del clk[:]
        del detSat[:]
        newList.append(rangingList[i*segment+int(segment/2)])
    reamin=length-int(length/segment)*segment
    # if reamin>0:
    #     for ii in range(int(length/segment)*segment,length):
    #         t.append(rangingList[ii][0])
    #         R.append(rangingList[ii][1])
    #         clk.append(rangingList[i * segment + j][3])
    #     matR=fitting.polyLeastFit(t,R,order)
    #     matclk = fitting.polyLeastFit(t, clk, order)
    #     rangingList[jj][1]=fitting.polyLeastFitCal([rangingList[jj][0]],matR)[0]
    #     rangingList[i * segment + int(segment / 2)][3] = \
    #     fitting.polyLeastFitCal([rangingList[i * segment + int(segment / 2)][0]], matclk)[0]
    #     newList.append(rangingList[int(length/segment)*segment+int(reamin/2)])
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
    print 'fit filtered! %s points moved out!'%(count+reamin)
    return filterList

def rangefilter(rangingList,segment,order,windows,channel):
    t=[]
    R=[]
    filterList=[]
    residualList=[]
    count=0
    length=len(rangingList)
    for i in range(length):
        if i <segment:
            for j in range(segment):
                index=i+j
                t.append(rangingList[index][0])
                R.append(rangingList[index][channel])
            mat=fitting.polyLeastFit(t,R,order)
            del t[:]
            del R[:]
            det = rangingList[i][channel] - fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
            if abs(det) < windows:
                filterList.append(rangingList[i])
                residualList.append([rangingList[i][0],det])
                # print rangingList[i][0], det
            else:
                # rangingList[i ][1] = fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
                # filterList.append(rangingList[i])
                # residualList.append([rangingList[i][0], 0])
                count += 1
        elif i<length-segment:
            for j in range(segment):
                index=i+j-segment/2
                t.append(rangingList[index][0])
                R.append(rangingList[index][channel])

            mat=fitting.polyLeastFit(t,R,order)
            del t[:]
            del R[:]
            det = rangingList[i][channel] - fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
            if abs(det) < windows:
                filterList.append(rangingList[i])
                residualList.append([rangingList[i][0], det])
                # print rangingList[i][0], det
            else:
                # rangingList[i ][channel] = fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
                # filterList.append(rangingList[i])
                # residualList.append([rangingList[i][0], 0])
                count += 1
        else:
            for j in range(segment):
                index=i+j-segment
                t.append(rangingList[index][0])
                R.append(rangingList[index][channel])

            mat=fitting.polyLeastFit(t,R,order)
            del t[:]
            del R[:]
            det = rangingList[i][channel] - fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
            if abs(det) < windows:
                filterList.append(rangingList[i])
                residualList.append([rangingList[i][0], det])
                # print rangingList[i][0], det
            else:
                # rangingList[i][channel] = fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
                # filterList.append(rangingList[i])
                # residualList.append([rangingList[i][0], 0])
                count += 1
    print 'fit filtered! %s points moved !'%(count)
    return filterList,residualList

def fitsegment(list,index,segment,channel,order):
    t = []
    R = []
    for i in range(index-segment,index+segment):
        t.append(list[i][0])
        R.append(list[i][channel])
    mat = fitting.polyLeastFit(t, R, order)
    del t[:]
    del R[:]
    return mat

def filterbyfit(rangingList,segment,order,windows,channel):
    t=[]
    R=[]
    filterList=[]
    count=0
    fitCount=int(segment/2)
    length=len(rangingList)
    for i in range(length):
        if i <segment:
            for j in range(segment):
                index=i+j
                t.append(rangingList[index][0])
                R.append(rangingList[index][channel])
            mat=fitting.polyLeastFit(t,R,order)
            del t[:]
            del R[:]
            det = rangingList[i][channel] - fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
            if abs(det) < windows:
                filterList.append(rangingList[i])
            else:
                count += 1
        elif i<length-segment:
            if fitCount==int(segment/2):
                mat=fitsegment(rangingList,i,segment,channel,order)
            fitCount-=1
            if fitCount==0:
                fitCount=int(segment/2)
            det = rangingList[i][channel] - fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
            if abs(det) < windows:
                filterList.append(rangingList[i])
            else:
                count += 1
        else:
            for j in range(segment):
                index=i+j-segment
                t.append(rangingList[index][0])
                R.append(rangingList[index][channel])
            mat=fitting.polyLeastFit(t,R,order)
            del t[:]
            del R[:]
            det = rangingList[i][channel] - fitting.polyLeastFitCal([rangingList[i][0]], mat)[0]
            if abs(det) < windows:
                filterList.append(rangingList[i])
                # residualList.append([rangingList[i][0], det])
            else:
                count += 1
    print 'fit filtered! %s points moved !'%(count)
    return filterList

def reduceSec(rangingList,fitNum,timeShift,channelR,channelC,order):
    startSec=int(rangingList[0][0])+1
    endSec=int(rangingList[-1][0])
    reduceList=[]
    t=[]
    r=[]
    c=[]
    # fitNum=5
    index=0
    length=len(rangingList)
    for sec in range(startSec,endSec+1):
        while rangingList[index][0]<sec:
            index+=1
        for i in range(index-fitNum,index+fitNum):
            if i>=length-1:
                break
            t.append(rangingList[i][0]+timeShift)
            r.append(rangingList[i][channelR])
            c.append(rangingList[i][channelC])
        matR=fitting.polyLeastFit(t,r,order)
        matC = fitting.polyLeastFit(t, c, order)
        reduceList.append([sec,fitting.polyLeastFitCal([float(sec)],matR)[0],fitting.polyLeastFitCal([float(sec)],matC)[0]])
        del t[:]
        del r[:]
        del c[:]
    return reduceList

def reducebyfactor(List,factor):
    newList=[]
    count=0
    for item in List:
        count+=1
        if count==factor:
            count=0
            newList.append(item)
    return newList

def atmCorrect(rangingList,atmList):
    length=len(rangingList)
    sec=int(rangingList[0][0])
    index=0
    while int(atmList[index][0])<sec:
        index+=1
    for i in range(length):
        delay1=atmosphericDelayCorrect.MPAtmDelayModelCal(1.064,32.333,5031,45270,5,30,float(atmList[index][1]))
        delay2=atmosphericDelayCorrect.MPAtmDelayModelCal(0.532,32.333,5031,45270,5,30,float(atmList[index][1]))
        rangingList[i][1]=rangingList[i][1]-(delay1+delay2)/2
        index+=1


def groPulseCoincidenceTest():
    startSec=245
    endSec=445
    groSatShift=240
    date='170829'
    groFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\%s\\20170830031232_fineParse_1064.txt',encoding='utf-8')%date
    satFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\%s\\0829AliSatellite_channel_27_1064.txt',encoding='utf-8')%date
    groGPSFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\%s\\20170830031232_fineParse_GPS.txt',encoding='utf-8')%date
    satGPSFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\%s\\0829AliSatellite_channel_5_GPS.txt',encoding='utf-8')%date
    gpsDisFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\%s\\GPS_Dis.txt',encoding='utf-8')%date
    saveFile=groFile[:-4]+'_%s-%s_coincidence_0320.txt'%(startSec,endSec)
    groPulseList=fileToList.fileToList(groFile)
    satPulseList=fileToList.fileToList(satFile)
    groGPSList=fileToList.fileToList(groGPSFile)
    satGPSList=fileToList.fileToList(satGPSFile)
    gpsDisList=fileToList.fileToList(gpsDisFile)

    # groPulseList,satPulseList,groGPSList,satGPSList=timeCalibrate(groList,satList,groGPSList,satGPSList)
    coinList=groPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec)
    fileToList.listToFile(coinList,saveFile)
    # for groSatShift in range(22,23
    #                          ):
    #     print 'shift',groSatShift
    #     groPulseCoincidence(groPulseList, satPulseList, groGPSList, satGPSList, gpsDisList, groSatShift, startSec,
    #                         endSec)


def satPulseCoincidenceTest():
    file=unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\',encoding='utf-8')
    startSec=245
    endSec=445
    groSatShift=240
    groFile=unicode('%s20170830031232_fineParse_532_filtered_reflectFiltered.txt',encoding='utf-8')%file
    satFile=unicode('%s0829AliSatellite_channel_10_532.txt',encoding='utf-8')%file
    groGPSFile=unicode('%s20170830031232_fineParse_GPS.txt',encoding='utf-8')%file
    satGPSFile=unicode('%s0829AliSatellite_channel_5_GPS.txt',encoding='utf-8')%file
    gpsDisFile=unicode('%sGPS_Dis.txt',encoding='utf-8')%file
    saveFile=groFile[:-4]+'_%s-%s_coincidence_0320.txt'%(startSec,endSec)
    groPulseList=fileToList.fileToList(groFile)
    satPulseList=fileToList.fileToList(satFile)
    groGPSList=fileToList.fileToList(groGPSFile)
    satGPSList=fileToList.fileToList(satGPSFile)
    gpsDisList=fileToList.fileToList(gpsDisFile)
    # groPulseList,satPulseList,groGPSList,satGPSList=timeCalibrate(groList,satList,groGPSList,satGPSList)
    coinList=satPulseCoincidence(groPulseList,satPulseList,groGPSList,satGPSList,gpsDisList,groSatShift,startSec,endSec)
    fileToList.listToFile(coinList,saveFile)

def groSatPulseMatchTest():
    groCoinFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_1064_245-445_coincidence_0320.txt',encoding='utf-8')
    satCoinFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_532_filtered_reflectFiltered_245-445_coincidence_0320.txt',encoding='utf-8')
    groList=fileToList.fileToList(groCoinFile)
    satList=fileToList.fileToList(satCoinFile)
    saveFile=groCoinFile[:-4]+'_match.txt'
    matchList=groSatPulseMatch(groList,satList,240,105000000)
    fileToList.listToFile(matchList,saveFile)

def nearMatchTest():
    groCoinFile = unicode(
        'C:\Users\Levit\Experiment Data\阿里数据\\170919\\20170920032416_fineParse_1_1064_10-220_coincidence_new.txt',
        encoding='utf-8')
    satCoinFile = unicode(
        'C:\Users\Levit\Experiment Data\阿里数据\\170919\\20170920032416_fineParse_2_532_filtered_reflectFiltered_10-220_coincidence_new.txt',
        encoding='utf-8')
    groList = fileToList.fileToList(groCoinFile)
    satList = fileToList.fileToList(satCoinFile)
    saveFile = groCoinFile[:-4] + '_nearMatch.txt'
    result = nearMatch(groList, satList, 5, 90000000)
    reduceVList=reduceSec(result,30,0,1)
    reduceKList = reduceSec(result, 30, 0, 2)
    fileToList.listToFileLong(result, saveFile)
    fileToList.listToFileLong(reduceVList, saveFile[:-4]+'_VSec.txt')
    fileToList.listToFileLong(reduceKList, saveFile[:-4] + '_KSec.txt')

def asynLaserRangingTest():
    matchFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_1064_245-445_coincidence_0320_match.txt',encoding='utf-8')
    atmFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\俯仰角.txt',encoding='utf-8')
    saveFile=matchFile[:-4]+'_ranging_Degnan_K_detSat_S100-1.txt'
    saveResiFile = saveFile[:-4] + '_residual.txt'
    saveRedFile=saveFile[:-4]+'_Sec.txt'
    matchList=fileToList.fileToList(matchFile)
    atmList=fileToList.fileToList(atmFile)
    rangingList,residualList=asynLaserRanging(matchList,240)
    # for timeshift in range(0,1,5):
    #     timeshift=0.001*timeshift
    #     saveRedFile = matchFile[:-4] + '_rangingSec_NoIte-%s.txt'%timeshift
    #     reduceList=reduceSec(rangingList,5,timeshift,4,5)
    #     atmCorrect(reduceList,atmList)
    #     fileToList.listToFile(reduceList, saveRedFile)
    reduceList = reduceSec(rangingList, 20, 0, 1, 3,5)
    atmCorrect(reduceList, atmList)
    fileToList.listToFile(reduceList, saveRedFile)
    # atmCorrect(rangingList, atmList)
    fileToList.listToFileLong(residualList,saveResiFile)
    fileToList.listToFileLong(rangingList,saveFile)

def aysnLaserBKCTest():
    matchFile = unicode(
        'C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_1064_245-445_coincidence_0320_match.txt',
        encoding='utf-8')
    groGPSFile = unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_GPS.txt',
                         encoding='utf-8')
    satGPSFile = unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\0829AliSatellite_channel_5_GPS.txt',
                         encoding='utf-8')
    groGPSList=fileToList.fileToList(groGPSFile)
    satGPSList=fileToList.fileToList(satGPSFile)
    smoothNum=30
    saveFile = matchFile[:-4] + '_parameters_%s.txt'%smoothNum
    matchList = fileToList.fileToList(matchFile)
    parameterList=aysnLaserBKC(matchList,240,smoothNum,groGPSList,satGPSList)
    fileToList.listToFileLong(parameterList,saveFile)

def BKCSmoothTest():
    paraFile = unicode(
        'C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_1064_245-445_coincidence_0320_match_parameters_30_filtered.txt',
        encoding='utf-8')
    smoothNum = 30
    saveFile = paraFile[:-4] + '_Smooth%s.txt' % smoothNum
    paraList = fileToList.fileToList(paraFile)
    smoothList = BKCSmooth(paraList,80,2,50)
    fileToList.listToFileLong(smoothList, saveFile)

def reduceSecTest():
    dataFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_1064_245-445_coincidence_0320_match_parameters_30_filtered_Smooth30.txt',encoding='utf-8')
    atmFile=unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\俯仰角.txt',encoding='utf-8')

    saveRedFile=dataFile[:-4]+'_Sec.txt'
    rangingList=fileToList.fileToList(dataFile)
    atmList=fileToList.fileToList(atmFile)
    reduceList = reduceSec(rangingList, 20, 0, 1, 3,5)
    atmCorrect(reduceList, atmList)
    fileToList.listToFile(reduceList, saveRedFile)

def filterbyfitTest():
    segment = 100
    order = 2
    windows = 180
    rangeFile = unicode(
        'C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_1064_245-445_coincidence_0320_match_parameters_30.txt',
        encoding='utf-8')
    rangeList = fileToList.fileToList(rangeFile)

    saveFile = rangeFile[:-4] + '_filtered.txt'
    filteredList =filterbyfit(rangeList, segment, order, windows, 2)
    fileToList.listToFileLong(filteredList, saveFile)

def rangefilterTest():
    segment=400
    order=3
    windows=0.15
    rangeFile = unicode('C:\Users\Levit\Experiment Data\阿里数据\\170829\\20170830031232_fineParse_1064_245-445_coincidence_0320_match_parameters_30_filtered_Smooth30.txt',
        encoding='utf-8')
    rangeList = fileToList.fileToList(rangeFile)
    newList=[]
    count=0
    for item in rangeList:
        count+=1
        if count==1:
            # newList.append([item[1]/1000000000000.0,item[1]-item[0]-240000000000000])
            newList.append([item[0], item[1]])
            count=0
        # print newList[-1]
    print 'newList finished'
    saveFile=rangeFile[:-4]+'_%s_%s_residual_dis_1.txt'%(segment,order)
    # saveFile = rangeFile[:-4] + '_filtered.txt'
    filteredList,residualList=rangefilter(newList,segment,order,windows,1)
    fileToList.listToFileLong(residualList,saveFile)
    # fileToList.listToFileLong(filteredList, saveFile)


if __name__=='__main__':
    # groPulseCoincidenceTest()
    # satPulseCoincidenceTest()
    # groSatPulseMatchTest()
    # asynLaserRangingTest()
    # rangefilterTest()
    # filterbyfitTest()
    reduceSecTest()
    # aysnLaserBKCTest()
    # BKCSmoothTest()
