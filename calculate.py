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


if __name__ == '__main__':
    groundDataFile1=unicode('G:\时频传输数据处理\双站数据处理\\12.12\\send_fixed.txt','utf8')
    GPSDistance1=unicode('G:\时频传输数据处理\双站数据处理\\12.12\\GPS_send.txt','utf8')
    groundDataFile2=unicode('G:\时频传输数据处理\双站数据处理\\12.12\\recv_fixed.txt','utf8')
    GPSDistance2=unicode('G:\时频传输数据处理\双站数据处理\\12.12\\GPS_recv.txt','utf8')
    coinfile=unicode('G:\时频传输数据处理\双站数据处理\\12.12\Result\\synCoincidenceEM.txt','utf8')
    calculateGPS(groundDataFile1,groundDataFile2,GPSDistance1,GPSDistance2,coinfile)