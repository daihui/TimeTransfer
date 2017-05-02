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

def dataPreprocessingTest(s):
    f,g,l=dataPreprocessing.getFileNime(s)
    dataPreprocessing.classifyData(f,g,l)




if __name__ == '__main__':
    #filetest=open('G:\\test.txt','w')
    #s=unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\LJ\\recv_fixed.txt','utf8')
    # dataPreprocessingTest(s)
    #orbitDelayGps.timeCorrectByGpsTest(50,250,-21)
    #timeDataCoincidence.timeCoinTest()
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
    #filter.freqFilterTest()
    # satOrbit.satOrbSecTest()
    # timeAnalysis.leastsqToSecTest()
    # satOrbit.groundSecTest()
    #satOrbit.distanceTest()
    #calculate.gpsClock()
    #orbitDelayGps.delayOrbitFitTest()
    # gpsOrbit.gpsLagInterTest()
    # fitting.polyLeastFitTest('3.2')
    fitting.polyLeastFitSegmentTest('3.2')
    # timeDataCoincidence.timeCoinFinalEfficent(180, 200, -19, '3.2',1)
    # timeDataCoincidence.timeCoinEasyModeTest(190, 200, -19, '3.2',1)
    # for sec in range(10):
    #     print sec
    #     timeDataCoincidence.timeCoinEasyModeTest(55, 75, -sec-15, '3.2',1)