#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import dataPreprocessing
import orbitDelayGps
import timeDataCoincidence
import fileToList
import timeAnalysis
import filter
import satOrbit
import jdutil
import clockTimeCalibrate
import TDCDataConvert
import fitting
import matplotlib.pyplot as plt
import varianceStatistics
import dataPlot
import TDCTest

def calculateGPS(groundDataFile1,groundDataFile2,GPSDistance1,GPSDistance2,coinfile):
    freq,window,threshold=10000000, 30, 1000000
    startSec, endSec, gpsShift=100,200,-19
    dataFile1,gpsTime1,synTime1=dataPreprocessing.getFileNime(groundDataFile1)
    dataPreprocessing.classifyData(dataFile1,gpsTime1,synTime1)
    dataFile2,gpsTime2,synTime2=dataPreprocessing.getFileNime(groundDataFile2)
    dataPreprocessing.classifyData(dataFile2,gpsTime2,synTime2)
    gpsDelList=orbitDelayGps.gpsDisDelayEasyMode(GPSDistance1,GPSDistance2)
    synTimeList1=fileToList.fileToList(synTime1)
    synTimeList2=fileToList.fileToList(synTime2)
    gpsTimeList1=fileToList.fileToList(gpsTime1)
    gpsTimeList2=fileToList.fileToList(gpsTime2)
    # synTimeList1=filter.freqFilter(synTimeList1,freq,window,threshold)
    # synTimeList2=filter.freqFilter(synTimeList2,freq,window,threshold)
    coincidenceList=timeDataCoincidence.timeCoincidenceEasyMode(synTimeList1,synTimeList2,gpsDelList,gpsTimeList1,gpsTimeList2,startSec,endSec,coinfile,gpsShift)
    analysisList=timeAnalysis.adjacentAnalysis(coincidenceList,coinfile)
    resultList=timeAnalysis.leastsqToSec(analysisList,100000000000)
    #resultList=timeAnalysis.interSec(resultList)
    #print resultList
    fileToList.listToFileLong(resultList,coinfile[:-4]+'_result_100milliSec.txt')

def gpsClock():
    gpsTimeFile1=unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\LJ\\recv_fixed_GPSTime.txt','utf8')
    gpsTimeFile2=unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\DLH\\recv_fixed_GPSTime.txt','utf8')
    gpsTimeList1=fileToList.fileToList(gpsTimeFile1)
    gpsTimeList2=fileToList.fileToList(gpsTimeFile2)
    timeFactor1 = clockTimeCalibrate.clockTimeFactor(gpsTimeList1)
    timeFactor2 = clockTimeCalibrate.clockTimeFactor(gpsTimeList2)
    gpsTimeList1 = clockTimeCalibrate.timeCalibrate(gpsTimeList1, timeFactor1)
    gpsTimeList2 = clockTimeCalibrate.timeCalibrate(gpsTimeList2, timeFactor2)
    detTime=[]
    if len(gpsTimeList1)>len(gpsTimeList2):
        Sec=len(gpsTimeList2)
    else:Sec=len(gpsTimeList1)
    for i in range(Sec-1):
        det=(gpsTimeList1[i+1][0]-gpsTimeList1[i][0])-(gpsTimeList2[i+1][0]-gpsTimeList2[i][0])
        detTime.append([i,det])
        #print gpsTimeList1[i+1][0]-gpsTimeList1[i][0]
        #print gpsTimeList2[i+1][0]-gpsTimeList2[i][0]
    print "the difference between GPS time record by two station"
    #fileToList.listToFile(detTime,gpsTimeFile2[:-4]+'_det.txt')

def twoLocalTDCDataProcess(dataFile1,dataFile2,fineTimeFile1,fineTimeFile2,order,tau):
    channel1=int(fineTimeFile1[-8])
    channel2=int(fineTimeFile2[-8])
    saveFile1 = dataFile1[:-4] + '_channel%s.txt'%channel1
    dataList1 = TDCDataConvert.TDCDataParse(dataFile1, fineTimeFile1, 8, channel1-1)
    saveFile2 = dataFile2[:-4] + '_channel%s.txt' % channel2
    dataList2 = TDCDataConvert.TDCDataParse(dataFile2, fineTimeFile2, 8, channel2 - 1)
    fileToList.listToFile(dataList1, saveFile1)
    fileToList.listToFile(dataList2, saveFile2)
    num1=len(dataList1)
    num2=len(dataList2)
    if num1!=num2:
        print 'data lenght is not equal!'
        return 0
    xa=[]
    xb=[]
    ya=[]
    for i in range(num1):
        xa.append(dataList1[i][0])
        xb.append([dataList1[i][0]])
        ya.append(dataList1[i][0]-dataList2[i][0])
    xa, ya, fitList, residual =fitting.polyFitSegment(xa, ya, order, 10000)
    del xa[:]
    del fitList[:]
    xOneSec, residualOneSec = filter.normalByTime(xb, residual, 1000000000000)
    fileToList.listToFileLong(residualOneSec, saveFile1[:-4] + '-%s_residual-%s-1s-ps.txt'%(channel2,order))
    xTau,residualTau=filter.normalByTime(xb, residual, tau)
    residualFile=saveFile1[:-4] + '-%s_residual-%s-%.3fs-ps.txt' % (channel2, order,tau/1000000000000.0)
    fileToList.listToFileLong(residualTau, residualFile)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for i,item in enumerate(xOneSec):
        xOneSec[i]=item/1000000000000.0
        residualOneSec[i][0]=residualOneSec[i][0]*1000000000000
    ax1.plot(xOneSec,residualOneSec, color='g', linestyle='-', marker='*')
    ax1.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
    ax1.yaxis.grid(True, which='major')  # y坐标轴的网格使用次刻度show()
    plt.show()

    tdevFile = residualFile[:-4] + '_TDEV.txt'
    tdev = varianceStatistics.TDEV(residualTau, tau/1000000000000.0)
    fileToList.listToFileFloat(tdev, tdevFile)
    print 'TDEV calculation finished!'

    fig = plt.figure()
    dataPlot.logPlotAx(tdev, fig, 'r','--','s', '11.25 tdev')
    dataFile1 = unicode(
        'C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171114200130-tdc2-13-2k-500s-3_residual-1-0.01s-ps_TDEV.txt',
        'utf8')
    List1 = fileToList.fileToList(dataFile1)
    dataPlot.logPlotAx(List1, fig, 'g', '--', 'o', '11.14')
    plt.show()

def twoLightTDCDataProcess(channel1,channel2,delay,window,dataFile1,dataFile2,fineTimeFile1,fineTimeFile2,order,tau,tdevName,tdevComp,tdevCompFile):

    saveFile1 = dataFile1[:-4] + '_channel_%s.txt'%channel1
    dataList1 = TDCDataConvert.TDCDataParse(dataFile1, fineTimeFile1, 8, channel1-1)
    fileToList.listToFile(dataList1, saveFile1)
    dataList1_filter=filter.freqFilter(dataList1,10000200,6,300000)
    dataList1_filterN=filter.reflectNoiseFilter(dataList1_filter,1000000,0)
    fileToList.listToFile(dataList1_filterN, saveFile1[:-4]+'_filterN.txt')
    saveFile2 = dataFile2[:-4] + '_channel_%s.txt' % channel2
    dataList2 = TDCDataConvert.TDCDataParse(dataFile2, fineTimeFile2, 8, channel2 - 1)
    fileToList.listToFile(dataList2, saveFile2)
    dataList2_filter = filter.freqFilter(dataList2, 10000200, 6, 300000)
    dataList2_filterN = filter.reflectNoiseFilter(dataList2_filter, 1000000, 0)
    fileToList.listToFile(dataList2_filterN, saveFile2[:-4] + '_filterN.txt')
    saveCoinFile = dataFile1[:-4] + '_filterN_coindence.txt'
    coindenceList,averSecCount=TDCTest.coindenceTest(dataList1_filterN, dataList2_filterN, delay, window, saveCoinFile)
    tdevName=tdevName+' %s'%averSecCount
    del dataList1,dataList1_filter,dataList1_filterN
    del dataList2,dataList2_filter,dataList2_filterN
    num=len(coindenceList)
    xa = []
    xb = []
    ya = []
    for i in range(num):
        xa.append(coindenceList[i][0])
        ya.append(coindenceList[i][2])
    xa, ya, coindenceList, fitList, residual = filter.fitFilter(coindenceList, 3000 / 1000000000000.0, 1, 1)
    xa, ya, fitList, residual = fitting.polyFitSegment(xa, ya, order, 10000)
    for i in range(len(xa)):
        xb.append([xa[i]])
    xOneSec, residualOneSec = filter.normalByTime(xb, residual, 1000000000000)
    del xa[:]
    del fitList[:]
    del coindenceList[:]
    fileToList.listToFileLong(residualOneSec, saveFile1[:-4] + '-%s_residual-%s-1s-ps.txt' % (channel2, order))
    xTau, residualTau = filter.normalByTime(xb, residual, tau)
    residualFile = saveFile1[:-4] + '-%s_residual-%s-%.3fs-ps.txt' % (channel2, order, tau / 1000000000000.0)
    fileToList.listToFileLong(residualTau, residualFile)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for i, item in enumerate(xOneSec):
        xOneSec[i] = item / 1000000000000.0
        residualOneSec[i][0] = residualOneSec[i][0] * 1000000000000
    ax1.plot(xOneSec, residualOneSec, color='g', linestyle='-', marker='*')
    ax1.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
    ax1.yaxis.grid(True, which='major')  # y坐标轴的网格使用次刻度show()
    plt.show()

    tdevFile = residualFile[:-4] + '_TDEV.txt'
    tdev = varianceStatistics.TDEV(residualTau, tau / 1000000000000.0)
    fileToList.listToFileFloat(tdev, tdevFile)
    print 'TDEV calculation finished!'

    fig = plt.figure()
    dataPlot.logPlotAx(tdev, fig, 'r', '--', 's', tdevName)
    List1 = fileToList.fileToList(tdevCompFile)
    dataPlot.logPlotAx(List1, fig, 'g', '--', 'o', tdevComp)
    plt.show()

def twoLocalTDCDataProcessTest():
    dataFile1 = unicode(
        'C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171125\\20171125205406-tdc2-2k-500s-4.dat',
        encoding='utf-8')
    fineTimeFile1 = unicode('C:\Users\Levit\Experiment Data\FineTimeCali\\tdc2\\tdc2_channel_4_43.txt',
                           encoding='utf-8')
    dataFile2 = unicode(
        'C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171125\\20171125205417-tdc13-2k-500s-4.dat',
        encoding='utf-8')
    fineTimeFile2 = unicode('C:\Users\Levit\Experiment Data\FineTimeCali\\tdc13\\tdc13_channel_4_43.txt',
                            encoding='utf-8')
    order=2
    tau=100000000000.0
    twoLocalTDCDataProcess(dataFile1,dataFile2,fineTimeFile1,fineTimeFile2,order,tau)

def twoLightTDCDataProcessTest():
    channel1 = 5
    channel2 = 5
    delay =-144000
    window = 500000
    order = 2
    tau = 10000000000.0
    tdevName='12.16 electronic'
    tdevComp='11.25 Electronic TDEV'
    dataFile1 = unicode(
        'C:\Users\Levit\Experiment Data\德令哈测试\\20171216\零基线实验\\20171217005308-tdc2-0baseline-1.dat',
        encoding='utf-8')
    dataFile2 = unicode(
        'C:\Users\Levit\Experiment Data\德令哈测试\\20171216\零基线实验\\20171217005308-tdc13-0baseline-1.dat',
        encoding='utf-8')
    fineTimeFile1 = unicode(
        'C:\Users\Levit\Experiment Data\FineTimeCali\\tdc2\\1216_tdc2_5C_channel_%s_4%s.txt' % (channel1, channel1 - 1),
        encoding='utf-8')
    fineTimeFile2 = unicode(
        'C:\Users\Levit\Experiment Data\FineTimeCali\\tdc13\\1216_tdc13_5C_channel_%s_4%s.txt' % (channel2, channel2 - 1),
        encoding='utf-8')
    tdevCompFile = unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171125\\20171125183452-tdc2-2k-500s-3_channel4-4_residual-2-0.010s-ps_TDEV.txt','utf8')
    twoLightTDCDataProcess(channel1,channel2,delay,window,dataFile1,dataFile2,fineTimeFile1,fineTimeFile2,order,tau,tdevName,tdevComp,tdevCompFile)


if __name__ == '__main__':
    # groundDataFile1=unicode('G:\时频传输数据处理\双站数据处理\\12.12\\send_fixed.txt','utf8')
    # GPSDistance1=unicode('G:\时频传输数据处理\双站数据处理\\12.12\\GPS_send.txt','utf8')
    # groundDataFile2=unicode('G:\时频传输数据处理\双站数据处理\\12.12\\recv_fixed.txt','utf8')
    # GPSDistance2=unicode('G:\时频传输数据处理\双站数据处理\\12.12\\GPS_recv.txt','utf8')
    # coinfile=unicode('G:\时频传输数据处理\双站数据处理\\12.12\Result\\synCoincidenceEM.txt','utf8')
    # calculateGPS(groundDataFile1,groundDataFile2,GPSDistance1,GPSDistance2,coinfile)
    # twoLocalTDCDataProcessTest()
    twoLightTDCDataProcessTest()