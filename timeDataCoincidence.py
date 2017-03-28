#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'levitan'

import fileToList
import clockTimeCalibrate


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


def timeCoincidenceEasyMode(List1, List2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, coinfile, gpsShift):
    coincidenceList = []
    tolFirst = 1000000
    tol = 100000
    timeCount1 = 0
    timeCount2 = 0
    coinCount = 0

    timeFactor1 = clockTimeCalibrate.clockTimeFactor(gpsTimeList1)
    timeFactor2 = clockTimeCalibrate.clockTimeFactor(gpsTimeList2)
    List1 = clockTimeCalibrate.timeCalibrate(List1, timeFactor1)
    List2 = clockTimeCalibrate.timeCalibrate(List2, timeFactor2)
    gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1)
    gpsTimeList2 = clockTimeCalibrate.timeCalibrate(gpsTimeList2, timeFactor2)
    for i in range(startSec, endSec):
        inSec = True
        firstCoin = False
        timeBase1 = gpsTimeList1[i][0]
        timeBase2 = gpsTimeList2[i][0]
        priorTime1 = 0.0
        priorTimp2 = 0.0
        seachCount=0
        delay1=0.0
        delay2=0.0
        while List2[timeCount2][0] - timeBase2 < 0:
            timeCount2 += 1
        while List1[timeCount1][0] - timeBase1 < 0:
            timeCount1 += 1
        # for i in range(20):
        #     delay1 += (List1[timeCount1 + i][0] - timeBase1) % 10000000
        #     delay2 += (List2[timeCount2 + i][0] - timeBase2) % 10000000
        #     #print delay1 % 10000000
        # delay1 = (delay1 / 20)
        # delay2 = (delay2 / 20)
        print 'sec ',i,timeBase1-timeBase2
        while inSec:
            if firstCoin == False:
                firstime1 = List1[timeCount1][0] - List2Delay[i + gpsShift][0] - timeBase1
                firstime2 = List2[timeCount2][0] - List2Delay[i + gpsShift][1] - timeBase2
                detTime = firstime1 - firstime2
                # print detTime
                if abs(detTime) > tolFirst:
                    if seachCount<40:
                        if detTime > 0:
                            timeCount2 += 1
                            seachCount+=1
                        else:
                            timeCount1 += 1
                            seachCount+=1
                    else:
                        print '0'
                        break
                else:
                    coinCount += 1
                    print coinCount,seachCount
                    priorTime1 = List1[timeCount1][0]
                    priorTimp2 = List2[timeCount2][0]
                    firstCoin = True
                    dt=(priorTime1-List1[timeCount1-1][0])-(priorTimp2-List2[timeCount2-1][0])
                    print dt
                    coincidenceList.append(
                            [List1[timeCount1][0], List2[timeCount2][0], detTime, List2Delay[i + gpsShift][0]])
                    timeCount1 += 1
                    timeCount2 += 1
                if List2[timeCount2][0] - timeBase2 > 1000000000000:
                    inSec = False
                    #     continue
            else:
                time1 = List1[timeCount1][0] - priorTime1
                time2 = List2[timeCount2][0] - priorTimp2
                det = time1 - time2
                if abs(det) > tol:
                    if det > 0:
                        timeCount2 += 1
                    else:
                        timeCount1 += 1
                else:
                    coinCount += 1
                    # print coinCount
                    priorTime1 = List1[timeCount1][0]
                    priorTimp2 = List2[timeCount2][0]
                    coincidenceList.append([List1[timeCount1][0], List2[timeCount2][0], det, 0])
                    timeCount1 += 1
                    timeCount2 += 1
                    # print coincidenceList[coinCount - 1][0]
            if List2[timeCount2][0] - timeBase2 > 1000000000000:
                inSec = False
    fileToList.listToFile(coincidenceList, coinfile)
    print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coincidenceList


def timeCoinTest():
    List1 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\LJ\\recv_fixed_850Time.txt', 'utf8'))
    List2 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time.txt', 'utf8'))
    List2Delay = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time_disDelay.txt', 'utf8'))
    gpsTimeList1 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\LJ\\recv_fixed_GPSTime.txt', 'utf8'))
    gpsTimeList2 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_GPSTime.txt', 'utf8'))
    coinfile = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\850coincidence.txt', 'utf8')
    startSec = 50
    endSec = 250
    timeCoincidence(List1, List2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, coinfile)


def timeCoinEasyModeTest(startSec, endSec, gpsShift):
    List1 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\LJ\\recv_fixed_850Time_filtered.txt', 'utf8'))
    List2 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time_filtered.txt', 'utf8'))
    List2Delay = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\GPS_disDelay.txt', 'utf8'))
    gpsTimeList1 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\LJ\\recv_fixed_GPSTime.txt', 'utf8'))
    gpsTimeList2 = fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_GPSTime.txt', 'utf8'))
    coinfile = unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\850coincidenceEM_0328.txt', 'utf8')
    timeCoincidenceEasyMode(List1, List2, List2Delay, gpsTimeList1, gpsTimeList2, startSec, endSec, coinfile, gpsShift)
