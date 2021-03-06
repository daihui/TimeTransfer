#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import clockTimeCalibrate
import Hydraharp400DataConvert
import fitting
import gpsOrbit
import filter
import matplotlib.pyplot as plt
import TDCTest
import numpy
# import statistics


# 合符函数，寻找两list的时间符合。
def timeCoincidence(timeList1, timeList2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, shift, coinfile):
    SYSD1_LJ=171628
    SYSD2_DLH=99901
    coincidenceList = []
    detList=[]
    tolerate = 2000000
    timeCount1 = 0
    timeCount2 = 0
    coinCount = 0
    Num = 5
    sec = 1000000000000.0
    timeFactor1,offset1 = clockTimeCalibrate.clockTimeFactorFit(gpsTimeList1)
    timeFactor2,offset2 = clockTimeCalibrate.clockTimeFactorFit(gpsTimeList2)
    List1 = clockTimeCalibrate.timeCalibrate(timeList1, timeFactor1,offset1)
    List2 = clockTimeCalibrate.timeCalibrate(timeList2, timeFactor2,offset2)
    gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1,offset1)
    gpsTimeList2 = clockTimeCalibrate.timeCalibrate(gpsTimeList2, timeFactor2,offset2)
    # List1=timeList1
    # List2=timeList2
    for i in range(startSec, endSec ):
        inSec = True
        timeBase1 = gpsTimeList1[i-1][0]
        # timeBase2 = gpsTimeList2[i][0]
        timeBase2 = gpsTimeList2[i-1][0]
        while List2[timeCount2][0] - timeBase2 < 0:
            timeCount2 += 1
        while List1[timeCount1][0] - timeBase1 < 0:
            timeCount1 += 1
        startNo = i
        delayFun1 = gpsOrbit.gpsLagInterFun( List2Delay, startNo, Num, shift, 0)
        delayFun2= gpsOrbit.gpsLagInterFun( List2Delay, startNo, Num, shift, 1)
        # atmDelayFun1= gpsOrbit.gpsLagInterFun( List2Delay, startNo, Num, shift, 2)
        # atmDelayFun2= gpsOrbit.gpsLagInterFun( List2Delay, startNo, Num, shift, 3)
        # print i,delayFun1(i),delayFun2(i)
        while inSec:
            delay1 = delayFun1(List1[timeCount1][0]/sec)
            delay2 = delayFun2(List2[timeCount2][0]/sec)
            # atmDelay1=atmDelayFun1(List1[timeCount1][0]/sec)
            # atmDelay2 = atmDelayFun2(List2[timeCount2][0] / sec)
            # print List1[timeCount1][0]/sec,delay1,List2[timeCount2][0]/sec,delay2
            delay1 = delayFun1((List1[timeCount1][0] - delay1)/sec)
            delay2 = delayFun2((List2[timeCount2][0] - delay2)/sec)
            delay1 = delayFun1((List1[timeCount1][0] - delay1)/sec)
            delay2 = delayFun2((List2[timeCount2][0] - delay2)/sec)
            time1 = List1[timeCount1][0] - timeBase1 - delay1-SYSD1_LJ
            time2 = List2[timeCount2][0] - timeBase2 - delay2-SYSD2_DLH
            detTime = time1 - time2
            det = (List1[timeCount1][0] - delay1-SYSD1_LJ) - (List2[timeCount2][0] - delay2-SYSD2_DLH)
            # print List1[timeCount1][0],delay1,List2[timeCount2][0],delay2,detTime,timeBase1,timeBase2
            if abs(detTime) > tolerate:
                if detTime > 0:
                    timeCount2 += 1
                else:
                    timeCount1 += 1
            else:
                coinCount += 1
                # coincidenceList.append(
                #     [timeList1[timeCount1][0], timeList2[timeCount2][0], det, detTime, delay1, delay2])
                # 正常符合
                coincidenceList.append(
                    [List1[timeCount1][0]-SYSD1_LJ, List2[timeCount2][0]-SYSD2_DLH, det, detTime, delay1, delay2])
                #激光修正计算
                # coincidenceList.append(
                #     [List1[timeCount1][0]-SYSD1_LJ-delay1,List2[timeCount2][0]-SYSD2_DLH-delay2,List1[timeCount1][0]-SYSD1_LJ-atmDelay1- (List2[timeCount2][0]-SYSD2_DLH-atmDelay2),  delay1, delay2])
                detList.append(det)
                timeCount1 += 1
                timeCount2 += 1
            if List2[timeCount2][0] > gpsTimeList2[i][0]:
                inSec = False
    fileToList.listToFile(coincidenceList, coinfile)
    # print numpy.std(detList, ddof=1)
    std=numpy.std(detList, ddof=1)
    # print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coincidenceList, std


# 每秒寻找第一个符合，然后后面依次按与前面符合对的时间差来找符合
def timeCoincidenceEasyMode(List1, List2, gpsTimeList1, gpsTimeList2, List2Delay, startSec, endSec, coinfile, gpsShift):
    coincidenceList = []
    tolFirst = 2000000
    tol = 200000
    step = 1
    timeCount1 = 0
    timeCount2 = 0
    coinCount = 0
    checkCount = 100
    evaluateLength = 1000
    evaluateThreshold = 100000
    order = 3
    # List1 = filter.freqFilter(List1, 10000000, 10, 200000)
    # List2 = filter.freqFilter(List2, 10000000, 10, 200000)
    while List1[timeCount1][0] - gpsTimeList1[startSec][0] < 0:
        timeCount1 += 1
    while List2[timeCount2][0] - gpsTimeList2[startSec][0] < 0:
        timeCount2 += 1

    # timeFactor1 = clockTimeCalibrate.clockTimeFactor(gpsTimeList1)
    # timeFactor2 = clockTimeCalibrate.clockTimeFactor(gpsTimeList2)
    # List1 = clockTimeCalibrate.timeCalibrate(List1, timeFactor1)
    # List2 = clockTimeCalibrate.timeCalibrate(List2, timeFactor2)
    # gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1)
    # gpsTimeList2 = clockTimeCalibrate.timeCalibrate(gpsTimeList2, timeFactor2)
    for i in range(startSec, endSec, step):
        inSec = True
        firstCoin = False
        delayFunc1, delayFunc2 = gpsOrbit.gpsLagInterFun(gpsTimeList1, gpsTimeList2, List2Delay, i, 5, gpsShift)
        timeBase1 = gpsTimeList1[i][0]
        timeBase2 = gpsTimeList2[i][0]
        disDelay1 = List2Delay[i + gpsShift][0]
        disDelay2 = List2Delay[i + gpsShift][1]
        priorTime1 = 0.0
        priorTime2 = 0.0
        while inSec:
            if firstCoin == False:
                timeCount1, timeCount2, find = searchFirst(List1, List2, timeCount1, timeCount2, timeBase1,
                                                           timeBase2, tolFirst, coincidenceList, delayFunc1,
                                                           delayFunc2, disDelay1, disDelay2)
                if find:
                    coinCount += 1
                    priorTime1 = List1[timeCount1][0]
                    priorTime2 = List2[timeCount2][0]
                    firstCoin = True
                    coincidenceList.append(
                        [List1[timeCount1][0], List2[timeCount2][0], List1[timeCount1][0] - List2[timeCount2][0]])
                    timeCount1 += 1
                    timeCount2 += 1
                else:
                    break
            else:
                timeCount1, moveNext2, findCoin = searchCoin(List1, List2, timeCount1, timeCount2, 200,
                                                             priorTime1, priorTime2, tol)
                if findCoin:
                    checkCount -= 1
                    if checkCount < 0:
                        if len(coincidenceList) > evaluateLength:
                            evaluateFeedback = fitEvaluate(coincidenceList[-evaluateLength:], List1[timeCount1][0],
                                                           List2[timeCount2][0], evaluateThreshold, order)
                            if evaluateFeedback == False:
                                firstCoin = False
                            else:
                                priorTime1 = List1[timeCount1][0]
                                priorTime2 = List2[timeCount2][0]
                                coinCount += 1
                                coincidenceList.append(
                                    [List1[timeCount1][0], List2[timeCount2][0],
                                     List1[timeCount1][0] - List2[timeCount2][0]])
                                timeCount1 += 1
                                timeCount2 += 1
                        checkCount = 100
                    else:
                        priorTime1 = List1[timeCount1][0]
                        priorTime2 = List2[timeCount2][0]
                        coinCount += 1
                        coincidenceList.append(
                            [List1[timeCount1][0], List2[timeCount2][0], List1[timeCount1][0] - List2[timeCount2][0]])
                        timeCount1 += 1
                        timeCount2 += 1
                elif moveNext2:
                    timeCount2 += 1
            if List2[timeCount2][0] - gpsTimeList2[i + 1][0] > 0:
                print coinCount
                inSec = False
    fileToList.listToFile(coincidenceList, coinfile)
    print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coincidenceList


def searchFirst(timeList1, timeList2, index1, index2, timeBase1, timeBase2, tolTime, coincidenceList,
                delayFunc1, delayFunc2, disDelay1, disDelay2):
    evaluateLength = 1000
    evaluateFeedback = True
    evaluateThreshold = 200000
    order = 3
    find = False
    shift = 0
    id2 = index2
    while not find:
        delay1 = timeBase1 + delayFunc1(timeList1[index1 + shift][0] - disDelay1)
        delay2 = timeBase2 + delayFunc2(timeList2[index2][0] - disDelay2)
        det = (timeList2[index2][0] - delay2) - (timeList1[index1 + shift][0] - delay1)
        if len(coincidenceList) < evaluateLength or (timeList2[index2][0] - coincidenceList[-1][1] > 10000000000):
            if abs(det) < tolTime:
                find = True
                print 'first Sec, find the first !', index2 - id2, shift, det, delay1 - delay2, \
                    timeList1[index1 + shift][0], timeList2[index2][0]
            elif det > 0:
                shift += 1
            else:
                index2 += 1
        else:
            if abs(det) < tolTime:
                if len(coincidenceList) > evaluateLength:
                    evaluateFeedback = fitEvaluate(coincidenceList[-evaluateLength:], timeList1[index1 + shift][0],
                                                   timeList2[index2][0], evaluateThreshold, order)
                else:
                    print 'coincidenceList is less than need'
                if evaluateFeedback:
                    find = True
                    print 'find the first !', index2 - id2, shift, det, delay1 - delay2, timeList1[index1 + shift][0], \
                        timeList2[index2][0], coincidenceList[-1][1]
                else:
                    shift += 1
                    index2 += 1
            elif det > 0:
                shift += 1
            else:
                index2 += 1
    return index1 + shift, index2, find


def searchCoin(timeList1, timeList2, index1, index2, searchNum, priorTime1, priorTime2, tol):
    findCoin = False
    moveNext = False
    for i in range(searchNum):
        time1 = timeList1[index1 + i][0] - priorTime1
        time2 = timeList2[index2][0] - priorTime2
        det = time1 - time2
        if abs(det) > tol:
            if det > 0:
                moveNext = True
                break
            elif i == searchNum - 1:
                index1 += searchNum
        else:
            findCoin = True
            index1 = index1 + i
            break
    return index1, moveNext, findCoin


# 根据之前符合序列的拟合来评估下一个拟合是否在阈值内
def fitEvaluate(fitList, timeCoin1, timeCoin2, threshold, order):
    feedBack = False
    timeList = []
    delayList = []
    for item in fitList:
        timeList.append(item[1])
        delayList.append(item[2])
    mat = fitting.polyLeastFit(timeList, delayList, order)
    timeFit = fitting.polyLeastFitCal([timeCoin2], mat)
    det = timeCoin1 - timeCoin2 - timeFit[0]
    if abs(det) < threshold:
        feedBack = True
        # print 'this coincidence is ok,',det
    # else:
    #     print 'this coincidence out of threshold'
    return feedBack


# 寻找第一个符合点，后面依次按与前面的点寻找符合
def timeCoincidenceFinal(List1, List2, gpsTimeList1, gpsTimeList2, List2Delay, startSec, endSec, coinfile, gpsShift):
    coincidenceList = []
    tolFirst = 2000000
    tol = 200000
    timeCount1 = 0
    timeCount2 = 0
    coinCount = 0
    ListLength1 = len(List1)
    ListLength2 = len(List2)
    firstCoin = False
    endCoin = False
    priorTime1 = 0.0
    priorTime2 = 0.0

    while not firstCoin:
        timeBase1 = gpsTimeList1[startSec][0] + List2Delay[startSec + gpsShift][0]
        timeBase2 = gpsTimeList2[startSec][0] + List2Delay[startSec + gpsShift][1]
        print timeBase1, timeBase2
        if timeCount2 > ListLength2 or timeCount1 > ListLength1:
            print 'List end.'
            break
        while List2[timeCount2][0] - timeBase2 < 0:
            timeCount2 += 1
        while List1[timeCount1][0] - timeBase1 < 0:
            timeCount1 += 1
        timeCount1, timeCount2, find = searchFirst(List1, List2, timeCount1, timeCount2, 2000, 500, timeBase1,
                                                   timeBase2, tolFirst,
                                                   50, coincidenceList)
        if find:
            firstCoin = True
            coinCount += 1
            priorTime1 = List1[timeCount1][0]
            priorTime2 = List2[timeCount2][0]
            coincidenceList.append(
                [List1[timeCount1][0], List2[timeCount2][0], List1[timeCount1][0] - List2[timeCount2][0]])
            timeCount1 += 1
            timeCount2 += 1
            print 'find the first coincidence'
        else:
            startSec += 1
            print 'not find the first coincidence, move to next second'

    while not endCoin:
        timeCount1, timeCount2, findCoin, end = searchCoin(List1, List2, timeCount1, timeCount2, 200, priorTime1,
                                                           priorTime2, tol)
        if end:
            timeCount1 += 1
        else:
            if findCoin:
                coinCount += 1
                priorTime1 = List1[timeCount1][0]
                priorTime2 = List2[timeCount2][0]
                coincidenceList.append(
                    [List1[timeCount1][0], List2[timeCount2][0], List1[timeCount1][0] - List2[timeCount2][0]])
                timeCount1 += 1
                timeCount2 += 1
            else:
                timeCount2 += 1
        # time1 = List1[timeCount1][0] - priorTime1
        # time2 = List2[timeCount2][0] - priorTime2
        # det = time1 - time2
        # if abs(det) > tol:
        #     if det > 0:
        #         timeCount2 += 1
        #     else:
        #         timeCount1 += 1
        # else:
        #     coinCount += 1
        #     priorTime1 = List1[timeCount1][0]
        #     priorTime2 = List2[timeCount2][0]
        #     coincidenceList.append([List1[timeCount1][0], List2[timeCount2][0], List1[timeCount1][0]-List2[timeCount2][0]])
        #     timeCount1 += 1
        #     timeCount2 += 1
        if List2[timeCount2][0] - (gpsTimeList2[endSec][0] + List2Delay[endSec + gpsShift][1]) > 1000000000000:
            endCoin = True
    fileToList.listToFile(coincidenceList, coinfile)
    print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coincidenceList


def timeCoinTest(startSec, endSec, gpsShift, date,tdcShift,dataLJ,dataDLH):
    # List1 = fileToList.fileToList(
    #     unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc2_channel_6_filtered.txt', 'utf8') % (
    #     date, dataLJ))
    # List2 = fileToList.fileToList(
    #     unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_merge_filtered.txt' % (date, dataDLH), 'utf8'))
    List1 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\20170302\\send_fixed_850Time_filtered.txt', 'utf8') )
    List2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\20170302\\recv_fixed_850Time_filtered.txt' , 'utf8'))

    groundXYZList= fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\groundStation_haiji.txt' , 'utf8'))
    satelliteXYZList = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\satelliteWGS84_Sec.txt'%date , 'utf8'))
    # List2Delay = fileToList.fileToList( unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_Recv_Precise_紫台_disDelay.txt' % date, 'utf8'))
    atmosphereList=fileToList.fileToList(
            unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\天气参数.txt'%date, 'utf8'))
    # gpsTimeList1 = fileToList.fileToList(
    #     unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc2_channel_1.txt' % (date, dataLJ), 'utf8'))
    # gpsTimeList2 = fileToList.fileToList(
    #     unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_channel_1.txt' % (date, dataDLH), 'utf8'))
    gpsTimeList1 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\send_fixed_GPSTime.txt' % (date), 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\recv_fixed_GPSTime.txt' % (date), 'utf8'))

    newList2 = []
    for item in List2:
        time = item[0] + tdcShift * 1000000000000
        if time > 0:
            newList2.append([time])
    newgpsTimeList2 = []
    if tdcShift >= 0:
        for i in range(tdcShift):
            newgpsTimeList2.append([gpsTimeList2[i][0]])
        for i in range(len(gpsTimeList2)):
            newgpsTimeList2.append([gpsTimeList2[i][0] + tdcShift * 1000000000000])
    else:
        for i in range(len(gpsTimeList2)):
            gpsTime = gpsTimeList2[i][0] + tdcShift * 1000000000000
            if gpsTime > 0:
                newgpsTimeList2.append([gpsTime])
    print gpsTimeList2
    print newgpsTimeList2
    for i in range(1):
        List2Delay = gpsOrbit.delayCalWGS84(groundXYZList,0,1, satelliteXYZList, 0, 5,atmosphereList)
        delayFile=unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\result\\delay-%s-%s.txt' % (
            date, gpsShift+i, tdcShift), 'utf8')
        fileToList.listToFile(List2Delay,delayFile)
        # coinfile = unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\result\\synCoincidence-%s-%s-%s-%s-Coin-紫台WGS84-atm-factor-haiji_SYSdelay.txt' % (
        #     date, startSec, endSec, gpsShift+i, tdcShift), 'utf8')
        coinfile = unicode(
            'C:\Users\Levit\Experiment Data\双站数据\\%s\\result\\synCoincidence-%s-%s-%s-%s-Coin-紫台WGS84-atm-factor-haiji.txt' % (
                date, startSec, endSec, gpsShift + i, tdcShift), 'utf8')
        coindenceList,std=timeCoincidence(List1, newList2, List2Delay, gpsTimeList1, newgpsTimeList2, startSec, endSec, gpsShift+i, coinfile)
        filterFile=coinfile[:-4]+'_filtered.txt'
        xa, ya, filterList, fitList, residual = filter.fitFineFilter(coindenceList, 2500 / 1000000000000.0, 5, 2)
        countFile=filterFile[:-4]+'_count.txt'
        countList=TDCTest.countBySec(filterList)
        fileToList.listToFile(countList,countFile)
        fileToList.listToFile(filterList, filterFile)

def timeCoinCoarseTest(startSec, endSec, gpsShift, date,tdcShift,dataLJ,dataDLH):

    List1 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc2_channel_6_filtered.txt', 'utf8')%(date,dataLJ))
    List2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_merge_filtered.txt'%(date,dataDLH), 'utf8'))
    # groundXYZList= fileToList.fileToList(
    #     unicode('C:\Users\Levit\Experiment Data\双站数据\\20180108\\groundStationWGS84.txt' , 'utf8'))

    DelayList1 = fileToList.fileToList( unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\LJ_Distance.txt'%date , 'utf8'))
    DelayList2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\DLH_Distance.txt'%date, 'utf8'))

    # atmosphereList=fileToList.fileToList(
    #         unicode('C:\Users\Levit\Experiment Data\双站数据\\20180108\\天气参数.txt', 'utf8'))
    gpsTimeList1 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc2_channel_1.txt'%(date,dataLJ) , 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\共视数据\\%s-tdc13_channel_1.txt'%(date,dataDLH) , 'utf8'))
    newList2=[]
    for item in List2:
        time=item[0]+tdcShift*1000000000000
        if time>0:
            newList2.append([time])
    newgpsTimeList2=[]
    if tdcShift>=0:
        for i in range(tdcShift):
            newgpsTimeList2.append([gpsTimeList2[i][0]])
        for i in range(len(gpsTimeList2)):
            newgpsTimeList2.append([gpsTimeList2[i][0]+tdcShift*1000000000000])
    else:
        for i in range(len(gpsTimeList2)):
            gpsTime=gpsTimeList2[i][0]+tdcShift*1000000000000
            if gpsTime>0:
                newgpsTimeList2.append([gpsTime])
    print gpsTimeList2
    print newgpsTimeList2
    for i in range(1):
        List2Delay = gpsOrbit.delayCoarseCal(DelayList1,DelayList2)
        print List2Delay
        coinfile = unicode('C:\Users\Levit\Experiment Data\双站数据\\%s\\result\\synCoincidence-%s-%s-%s-%s-Coarse_Coin_factor.txt' % (
            date, startSec, endSec, gpsShift+i, tdcShift), 'utf8')
        coindenceList = timeCoincidence(List1, newList2, List2Delay, gpsTimeList1, newgpsTimeList2, startSec, endSec,
                                        gpsShift + i, coinfile)
        filterFile = coinfile[-4:] + '_filtered.txt'
        xa, ya, filterList, fitList, residual = filter.fitFineFilter(coindenceList, 2500 / 1000000000000.0, 5, 2)
        fileToList.listToFile(filterList, filterFile)
        countFile = filterFile[:-4] + '_count.txt'
        countList = TDCTest.countBySec(filterList)
        fileToList.listToFile(countList, countFile)
        # timeCoincidence(List1, List2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, gpsShift + i,
        #                 coinfile)


def timeCoinEasyModeTest(startSec, endSec, gpsShift, date):
    List1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\send_fixed_850Time_filtered.txt', 'utf8'))
    List2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\recv_fixed_850Time_filtered.txt', 'utf8'))
    List2Delay = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_Recv_Precise_disDelay.txt' % date, 'utf8'))
    gpsTimeList1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_GPSTime.txt' % date, 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_GPSTime.txt' % date, 'utf8'))
    coinfile = unicode(
        'E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0530-%s-%s-EM-%s.txt' % (
        date, startSec, endSec, gpsShift), 'utf8')
    # List1Ran = Hydraharp400DataConvert.randomList(List1, 0, efficent)
    # List2Ran = Hydraharp400DataConvert.randomList(List2, 0, efficent)
    timeCoincidenceEasyMode(List1, List2, gpsTimeList1, gpsTimeList2, List2Delay, startSec, endSec, coinfile, gpsShift)


def timeCoinFinalEfficent(startSec, endSec, gpsShift, date, efficent):
    List1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_850Time.txt' % date, 'utf8'))
    List2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_850Time.txt' % date, 'utf8'))
    List2Delay = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_disDelay.txt' % date, 'utf8'))
    gpsTimeList1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_GPSTime.txt' % date, 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_GPSTime.txt' % date, 'utf8'))
    coinfile = unicode(
        'E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0502_eff%s.txt' % (date, efficent), 'utf8')
    # List1Ran=Hydraharp400DataConvert.randomList(List1,0,efficent)
    # List2Ran=Hydraharp400DataConvert.randomList(List2,0,efficent)
    timeCoincidenceFinal(List1, List2, gpsTimeList1, gpsTimeList2, List2Delay, startSec, endSec, coinfile, gpsShift)


def coincidenceDelay(timeList1, timeList2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, shift, fitNum):
    # Num=int((endSec-startSec)/2)+5
    Num = 4
    secCount = 1000000000000
    # print Num
    timeFactor1 = clockTimeCalibrate.clockTimeFactor(gpsTimeList1)
    timeFactor2 = clockTimeCalibrate.clockTimeFactor(gpsTimeList2)
    List1 = clockTimeCalibrate.timeCalibrate(timeList1, timeFactor1)
    List2 = clockTimeCalibrate.timeCalibrate(timeList2, timeFactor2)
    gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1)
    gpsTimeList2 = clockTimeCalibrate.timeCalibrate(gpsTimeList2, timeFactor2)
    # delayFun1, delayFun2,delayfunc = gpsOrbit.gpsLagInterFun(gpsTimeList1, gpsTimeList2, List2Delay, 86, Num, shift,sec)
    # x=[float(i/100.0) for i in range(8600,10500)]
    # fx=[delayFun2(i) for i in x]
    # plt.figure("play")
    # ax1 = plt.subplot(111)
    # plt.sca(ax1)
    # #plt.plot(sr_x, sr_fx, linestyle=' ', marker='o', color='b')
    # plt.plot(x, fx, linestyle='--', color='r')
    # plt.show()
    tol = len(List1)
    gap = int(tol / 1000)
    for i in range(1, fitNum + 1):
        sec = int(List1[i * gap][0] / 1000000000000)
        delayFun1, delayFun2, delayfunc = gpsOrbit.gpsLagInterFun(gpsTimeList1, gpsTimeList2, List2Delay, sec, Num,
                                                                  shift, secCount)
        # print sec
        timeBase1 = gpsTimeList1[sec - 1][0]
        timeBase2 = gpsTimeList2[sec - 1][0]
        delay1 = delayFun1(List1[i * gap][0] / 1000000000000)
        delay2 = delayFun2(List2[i * gap][0] / 1000000000000)
        # print delay1, delay2,List1[i*gap][0]/1000000000000,List2[i*gap][0]/1000000000000,'1'
        delay1 = delayFun1((List1[i * gap][0] - delay1) / 1000000000000)
        delay2 = delayFun2((List2[i * gap][0] - delay2) / 1000000000000)
        delay1 = delayFun1((List1[i * gap][0] - delay1) / 1000000000000)
        delay2 = delayFun2((List2[i * gap][0] - delay2) / 1000000000000)
        delay = delayfunc(List1[i * gap][0] / 1000000000000)
        delay = delayfunc((List1[i * gap][0] - delay) / 1000000000000)
        delay = delayfunc((List1[i * gap][0] - delay) / 1000000000000)
        time2 = List2[i * gap][0] - delay2
        time1 = List1[i * gap][0] - delay1
        detTime = time1 - time2
        det = List1[i * gap][0] - List2[i * gap][0] - delay
        # print delay1,delay2,time1,time2
        # print timeBase2-timeBase1
        print '%s\t%s\t%s\t%s' % (List1[i * gap][0], detTime, det, delay)


def coincidenceDelayTest(startSec, endSec, gpsShift, date):
    List = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\3.2\\Result\\synCoincidenceEM_0530-85-250-EM--18_filtered.txt',
                'utf8'))
    List2Delay = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_Recv_Precise_disDelay.txt' % date, 'utf8'))
    gpsTimeList1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_GPSTime.txt' % date, 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_GPSTime.txt' % date, 'utf8'))
    list1 = []
    list2 = []
    for item in List:
        list1.append([item[0]])
        list2.append([item[1]])
    coincidenceDelay(list1, list2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, gpsShift, 990)


if __name__=='__main__':
    date='3.2'
    dataLJ = '20180109015114'
    dataDLH = '20180109015114'
    # timeCoinTest(61, 200, 1, '3.10', 0)
    # timeCoinCoarseTest(165,265,-11,'20180108',0)
    # timeCoinCoarseTest(50, 120, -14, '20180106', 0)
    # timeCoinCoarseTest(137, 240, -21, '20180109', 1,dataLJ,dataDLH)
    # timeCoinCoarseTest(90, 190, -17, '20180110', 0, dataLJ, dataDLH)
    # timeCoinTest(145, 235, -22, '20180109', 1, '20180110012855', '20180110012854')
    # timeCoinTest(165, 265, -11, date, 0, dataLJ, dataDLH)
    # timeCoinTest(85, 250, -18, date, 0, dataLJ, dataDLH)
    # timeCoinCoarseTest(120, 130, -16, '20180121', 1, '20180122014609', '20180122014608')
    # timeCoinTest(120, 220, -17, '20180121', 1, '20180122014609', '20180122014608')
    # timeCoinTest(90, 190, -18, '20180110', 0, '20180111010707', '20180111010706')
    timeCoinTest(85, 250, -19, '20170302', 0, '20180122014609', '20180122014608')
    # timeCoinCoarseTest(60, 160, -12, '20180125', 0, '20180126015157', '20180126015156')

