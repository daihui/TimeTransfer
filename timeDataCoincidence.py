#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import clockTimeCalibrate
import Hydraharp400DataConvert
import fitting
import gpsOrbit


# 合符函数，寻找两list的时间符合。
def timeCoincidence(List1, List2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, coinfile):
    coincidenceList = []
    tolerate = 500000
    timeCount1 = 0
    timeCount2 = 0
    coinCount = 0
    timeFactor1 = clockTimeCalibrate.clockTimeFactor(gpsTimeList1)
    timeFactor2 = clockTimeCalibrate.clockTimeFactor(gpsTimeList2)
    List1 = clockTimeCalibrate.timeCalibrate(List1, timeFactor1)
    List2 = clockTimeCalibrate.timeCalibrate(List2, timeFactor2)
    gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1)
    gpsTimeList2 = clockTimeCalibrate.timeCalibrate(gpsTimeList2, timeFactor2)
    for i in range(startSec, endSec - 1):
        inSec = True
        delay1 = 0.0
        delay2 = 0.0
        timeBase1 = gpsTimeList1[i][0]
        timeBase2 = gpsTimeList2[i][0]
        while List2[timeCount2][0] - timeBase2 < 0:
            timeCount2 += 1
        while List1[timeCount1][0] - timeBase1 < 0:
            timeCount1 += 1
        # for i in range(20):
        #     delay1 += (List1[timeCount1 + i][0] - timeBase1) % 10000000
        #     delay2 += (List2[timeCount2 + i][0] - timeBase2) % 10000000
        #     print delay1
        # delay1 = (delay1 / 20)
        # delay2 = (delay2 / 20)
        # print delay1
        while inSec:
            time2 = List2[timeCount2][0] - List2Delay[timeCount2][0] - timeBase2
            time1 = List1[timeCount1][0] - timeBase1
            detTime = time1 - time2
            if abs(detTime) > tolerate:
                if detTime > 0:
                    timeCount2 += 1
                else:
                    timeCount1 += 1
            else:
                coinCount += 1
                coincidenceList.append(
                    [List1[timeCount1][0], List2[timeCount2][0], detTime, delay1 - delay2,
                     List2Delay[timeCount2][0]])
                if coinCount > 1:
                    det1 = (coincidenceList[coinCount - 1][0] - coincidenceList[coinCount - 2][0]) % 10000000
                    det2 = (coincidenceList[coinCount - 1][1] - coincidenceList[coinCount - 2][1]) % 10000000
                    print 'det 1: ' + str(det1) + ' det 2: ' + str(det2)
                timeCount1 += 1
                timeCount2 += 1
            if List2[timeCount2][0] - timeBase2 > 1000000000000:
                inSec = False
    fileToList.listToFile(coincidenceList, coinfile)
    print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coincidenceList


# 每秒寻找第一个符合，然后后面依次按与前面符合对的时间差来找符合
def timeCoincidenceEasyMode(List1, List2, gpsTimeList1, gpsTimeList2, List2Delay, startSec, endSec, coinfile, gpsShift):
    coincidenceList = []
    tolFirst = 4000000
    tol = 200000
    step = 1
    timeCount1 = 0
    timeCount2 = 0
    coinCount = 0
    checkCount = 100
    evaluateLength = 1000
    evaluateThreshold = 100000
    order = 3
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
                timeCount1, timeCount2, find = searchFirst(List1, List2, timeCount1, timeCount2,  timeBase1,
                                                           timeBase2, tolFirst,  coincidenceList, delayFunc1,
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
                        coincidenceList.append([List1[timeCount1][0], List2[timeCount2][0], List1[timeCount1][0] - List2[timeCount2][0]])
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


def searchFirst(timeList1, timeList2, index1, index2,  timeBase1, timeBase2, tolTime, coincidenceList,
                delayFunc1, delayFunc2, disDelay1, disDelay2):
    evaluateLength = 500
    evaluateFeedback = True
    evaluateThreshold = 50000
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


def timeCoinTest():
    List1 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\LJ\\recv_fixed_850Time.txt', 'utf8'))
    List2 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time.txt', 'utf8'))
    List2Delay = fileToList.fileToList(
        unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time_disDelay.txt', 'utf8'))
    gpsTimeList1 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\LJ\\recv_fixed_GPSTime.txt', 'utf8'))
    gpsTimeList2 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_GPSTime.txt', 'utf8'))
    coinfile = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\850coincidence.txt', 'utf8')
    startSec = 50
    endSec = 250
    timeCoincidence(List1, List2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, coinfile)


def timeCoinEasyModeTest(startSec, endSec, gpsShift, date, efficent):
    List1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_850Time.txt' % date, 'utf8'))
    List2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_850Time.txt' % date, 'utf8'))
    List2Delay = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\GPS_Recv_Precise_disDelay.txt' % date, 'utf8'))
    gpsTimeList1 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\send_fixed_GPSTime.txt' % date, 'utf8'))
    gpsTimeList2 = fileToList.fileToList(
        unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\recv_fixed_GPSTime.txt' % date, 'utf8'))
    coinfile = unicode(
        'E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0428EM_%s.txt' % (date, efficent), 'utf8')
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
        'E:\Experiment Data\时频传输数据处理\双站数据处理\\%s\\result\\synCoincidenceEM_0426_eff%s.txt' % (date, efficent), 'utf8')
    # List1Ran=Hydraharp400DataConvert.randomList(List1,0,efficent)
    # List2Ran=Hydraharp400DataConvert.randomList(List2,0,efficent)
    timeCoincidenceFinal(List1, List2, gpsTimeList1, gpsTimeList2, List2Delay, startSec, endSec, coinfile, gpsShift)
