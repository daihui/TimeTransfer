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


def timeCoincidenceEasyMode(List1, List2, List2Delay, startSec, endSec, coinfile, gpsShift):
    tau=10
    coincidenceList = []
    tolFirst = 4000000
    tol = 100000
    timeCount1 = 0
    timeCount2 = 0
    coinCount = 0

    # timeFactor1 = clockTimeCalibrate.clockTimeFactor(gpsTimeList1)
    # timeFactor2 = clockTimeCalibrate.clockTimeFactor(gpsTimeList2)
    # List1 = clockTimeCalibrate.timeCalibrate(List1, timeFactor1)
    # List2 = clockTimeCalibrate.timeCalibrate(List2, timeFactor2)
    # gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1)
    # gpsTimeList2 = clockTimeCalibrate.timeCalibrate(gpsTimeList2, timeFactor2)
    for i in range(startSec*tau, endSec*tau):
        inSec = True
        firstCoin = False
        timeBase1 = List2Delay[i][0]
        timeBase2 = List2Delay[i][1]
        priorTime1 = 0.0
        priorTimp2 = 0.0
        # seachCount=0
        # del1=0.0
        # del2=0.0
        while List2[timeCount2][0] - timeBase2 < 0:
            timeCount2 += 1
        while List1[timeCount1][0] - timeBase1 < 0:
            timeCount1 += 1
        # for j in range(30):
        #     del1 += (List1[timeCount1 + j][0] - timeBase1- List2Delay[i + gpsShift][0]) % 10000000
        #     del2 += (List2[timeCount2 + j][0] - timeBase2- List2Delay[i + gpsShift][1]) % 10000000
        #     #print delay1 % 10000000
        # del1 = (del1 / 30)
        # del2 = (del2 / 30)
        # print 'sec ',i,delay1,delay2
        while inSec:
            if firstCoin == False:
                # firstime1 = List1[timeCount1][0] - List2Delay[i + gpsShift][0] - timeBase1-delay1
                # firstime2 = List2[timeCount2][0] - List2Delay[i + gpsShift][1] - timeBase2-delay2
                # detTime = firstime1 - firstime2
                # print detTime
                delay1=List2Delay[i + gpsShift*tau][2]+ timeBase1
                delay2=  timeBase2
                timeCount1,timeCount2,find=search(List1,List2,timeCount1,timeCount2,2000,100,delay1,delay2,tolFirst)
                if find:
                    coinCount += 1
                    print coinCount
                    priorTime1 = List1[timeCount1][0]
                    priorTimp2 = List2[timeCount2][0]
                    firstCoin = True
                    coincidenceList.append(
                            [List1[timeCount1][0], List2[timeCount2][0],  List2Delay[i + gpsShift][0]])
                    if coinCount>1:
                        dt = (priorTime1 - coincidenceList[coinCount - 2][0]) - (priorTimp2 - coincidenceList[coinCount - 2][1])
                        print dt
                    timeCount1 += 1
                    timeCount2 += 1
                else:
                    break
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
                    priorTime1 = List1[timeCount1][0]
                    priorTimp2 = List2[timeCount2][0]
                    coincidenceList.append([List1[timeCount1][0], List2[timeCount2][0], det, 0])
                    timeCount1 += 1
                    timeCount2 += 1
            if List2[timeCount2][0] - timeBase2 > 1000000000000/tau:
                inSec = False
    fileToList.listToFile(coincidenceList, coinfile)
    print 'time coincidence finished ! there are ' + str(coinCount) + ' pairs.'
    return coincidenceList

def search(timeList1, timeList2, index1, index2, gate1, gate2, delay1, delay2, tolTime):
    if index1-gate1/2<0:
        print 'index1 is smaller than gate/2 !'
    else:
        find=False
        shift=-gate1/2
        id2=index2
        while not find:
            det=(timeList2[index2][0]-delay2)-(timeList1[index1+shift][0]-delay1)
            if abs(det)<tolTime:
                find=True
                print 'find the sec first !',index2-id2,shift,det
            else:
                if shift<gate1/2:
                    shift+=1
                else:
                    index2+=1
                    shift=-gate1/2
                    if index2-id2==gate2:
                        print 'not find sec first, move to next sec.'
                        shift=0
                        break
    return index1+shift,index2,find



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
    List1 = fileToList.fileToList(unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\send_fixed_850Time_filtered.txt', 'utf8'))
    List2 = fileToList.fileToList(unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\recv_fixed_850Time_filtered.txt', 'utf8'))
    List2Delay = fileToList.fileToList(unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\result\GPS_disDelay_inter10.txt', 'utf8'))
    # gpsTimeList1 = fileToList.fileToList(unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\send_fixed_GPSTime.txt', 'utf8'))
    # gpsTimeList2 = fileToList.fileToList(unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\recv_fixed_GPSTime.txt', 'utf8'))
    coinfile = unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\12.12\\result\\synCoincidenceEM_0328.txt', 'utf8')
    timeCoincidenceEasyMode(List1, List2, List2Delay, startSec, endSec, coinfile, gpsShift)
