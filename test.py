#!/usr/bin/env python
#-*- coding: utf-8 -*-

#  功能测试文件

__author__ = 'levitan'

import dataPreprocessing
import orbitDelayGps
import timeDataCoincidence
import fileToList
import clockTimeCalibrate
import timeAnalysis
import filter
import satOrbit
import jdutil
import calculate
import gpsOrbit
import fitting
import matplotlib.pyplot as plt

def dataPreprocessingTest(s):
    f,g,l=dataPreprocessing.getFileNime(s)
    dataPreprocessing.classifyData(f,g,l)

def test1():
    dataFile=unicode('E:\Experiment Data\时频传输数据处理\本地光路系统测试\\5.17\\5.17-850-2路-1_coinDiff_segment_search.txt','utf8')
    timeList=fileToList.fileToList(dataFile)
    xa=[]
    ya=[]
    timeNormal=250000000000
    for i in range(len(timeList)):
        if timeList[i][1]>-700 and timeList[i][1]<600:
            xa.append([timeList[i][0]])
            ya.append([timeList[i][1]])
    xa,ya=filter.normalByTime(xa,ya,timeNormal)
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    ax1.yaxis.grid(True, which='major') #y坐标轴的网格使用次刻度show()
    ax1.plot(xa,ya, color='g', linestyle='-', marker='')
    plt.show()



if __name__ == '__main__':
    #filetest=open('G:\\test.txt','w')
    # s=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\dat2txt\\send_fixed.txt','utf8')
    # dataPreprocessingTest(s)
    #orbitDelayGps.timeCorrectByGpsTest(50,250,-21)

    # orbitDelayGps.gpsDisDelayEasyModeTest('3.2')
    # timeDataCoincidence.timeCoinEasyModeTest(170,190,-19,'12.12')
    # List1=fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_GPSTime.txt','utf8'))
    # List2=fileToList.fileToList(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\recv_fixed_850Time.txt','utf8'))
    # for i in range(10000,1000000):
    #     print (List1[i]-List1[i-1])%10000000,(List2[i]-List2[i-1])%10000000
    # factor=clockTimeCalibrate.clockTimeFactor(List1)
    # timeList=clockTimeCalibrate.timeCalibrate(List2,factor)
    # print timeList
    #timeAnalysis.adjacentAnalysisTest('12.12')
    # filter.freqFilterTest()
    # satOrbit.satOrbSecTest()
    # timeAnalysis.leastsqToSecTest()
    # satOrbit.groundSecTest()
    #satOrbit.distanceTest()
    #calculate.gpsClock()
    #orbitDelayGps.delayOrbitFitTest()
    # gpsOrbit.gpsLagInterTest()
    # fitting.polyLeastFitTest('3.2')
    # fitting.polyLeastFitSegmentTest('3.2')
    # fitting.polyFitSegmentTest('3.2')
    # timeDataCoincidence.timeCoinFinalEfficent(180, 200, -19, '3.2',1)
    # timeDataCoincidence.timeCoinEasyModeTest(85, 250, -18, '3.2')

    timeDataCoincidence.timeCoinTest(85, 250, -18, '3.2',0)
    # timeDataCoincidence.coincidenceDelayTest(85, 200, -18, '3.2')
    # fitting.fitComObsTest('3.2')
    # for sec in range(10):
    #     print sec
    #     timeDataCoincidence.timeCoinEasyModeTest(55, 75, -sec-15, '3.2',1)
    # satOrbit.disUncertainTest(1,10000,100)
    # fitting.clockDiffByDistanceTest('3.2')
    # dataPreprocessing.dataSelectBySec(150,154)
