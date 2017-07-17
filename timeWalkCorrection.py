#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

import math
import fileToList

def timeWalkPE(A,t0,y0,x):
    y=A*math.exp(-x/t0)+y0
    return y

def timeWalkPECorrection(A,t0,y0,countList):
    timeWalkList=[]
    for i,item in enumerate(countList):
        timeWalk0=timeWalkPE(A,t0,y0,countList[i][1])
        timeWalk1=timeWalkPE(A,t0,y0,countList[i][2])
        timeWalkList.append([countList[i][0],timeWalk0,timeWalk1])
        print '%s\t%s\t%s'%(countList[i][0],timeWalk0,timeWalk1)
    print 'time walk calculation finished!'
    return timeWalkList

def timeWalkPECompensation(countFile,coinFile):
    A=-85.30828
    t0=-51219.66687
    y0=79.54769
    factor=1
    countList=fileToList.fileToList(countFile)
    timeWalkList=timeWalkPECorrection(A,t0,y0,countList)
    saveFile=coinFile[:-4]+'_timeWalkComp.txt'
    coinList=fileToList.fileToList(coinFile)
    index=0
    for i, item in enumerate(coinList):
        sec=int(item[0]/1000000000000)
        while timeWalkList[index][0]<sec:
            index+=1
        if timeWalkList[index][0]==sec:
            item[2]=item[2]-factor*timeWalkList[index][1]+factor*timeWalkList[index][2]
        else:
            print 'not find time walk compensation'
    fileToList.listToFile(coinList,saveFile)
    print 'time walk compensation finished!'




if __name__=='__main__':
    countFile=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.27NS\\6.27NSCount.txt',encoding='utf-8')
    coinFile=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.27NS\\6.27NS_channel_0-1-1900-2080s_classified_coindence.txt',encoding='utf-8')
    timeWalkPECompensation(countFile,coinFile)