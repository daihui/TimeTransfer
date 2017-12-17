#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

# 钟差数据的稳定度分析，包括艾伦方差（ADEV），修正艾伦方差（MDEV），时间方差（TDEV）

import math
import fileToList

#use overlapping method
def ADEV(clockDataList,tau):
    totN=len(clockDataList)
    tauN=int(math.log(totN,2))-2
    adev=[]
    if tauN<=0:
        print 'need more clock data to calculate!'
        return 0
    for i in range(tauN+1):
        m=int(math.pow(2,i))
        simTau=m*tau
        sigma=0
        for j in range(totN-2*m):
            sigma+=(clockDataList[j+2*m][0]+clockDataList[j][0]-2*clockDataList[j+m][0])**2
        sigma=math.sqrt(sigma/(2*(totN-2*m)*simTau**2))
        adev.append([simTau,sigma])
        print '%.2f\t %s'%(simTau,sigma)
    return adev

def MDEV(clockDataList,tau):
    totN = len(clockDataList)
    tauN = int(math.log(totN, 2)) - 2
    mdev = []
    if tauN <= 0:
        print 'need more clock data to calculate!'
        return 0
    for i in range(tauN + 1):
        m = int(math.pow(2, i))
        simTau = m * tau
        sigma=0
        a=0
        for k in range(m):
            a += (clockDataList[k + 2 * m][0] + clockDataList[k][0] - 2 * clockDataList[k + m][0])
        sigma += a ** 2
        for j in range(1,totN-3*m+1):
            a+=(clockDataList[j+3*m-1][0]-3*clockDataList[j+2*m-1][0]+3*clockDataList[j+m-1][0]-clockDataList[j-1][0])
            sigma+=a**2
        sigma=math.sqrt(sigma/(2*(simTau**2)*m**2*(totN-3*m+1)))
        mdev.append([simTau,sigma])
        print '%.2f\t %s %s' % (simTau, sigma,m)
    return mdev

def TDEV(clockDataList,tau):
    totN = len(clockDataList)
    tauN = int(math.log(totN, 2)) - 2
    tdev = []
    if tauN <= 0:
        print 'need more clock data to calculate!'
        return 0
    for i in range(tauN + 1):
        m = int(math.pow(2, i))
        simTau = m * tau
        sigma = 0
        a = 0
        for k in range(m):
            a += (clockDataList[k + 2 * m][0] + clockDataList[k][0] - 2 * clockDataList[k + m][0])
        sigma += a ** 2
        for j in range(1, totN - 3 * m + 1):
            a += (
            clockDataList[j + 3 * m - 1][0] - 3 * clockDataList[j + 2 * m - 1][0] + 3 * clockDataList[j + m - 1][0] -
            clockDataList[j - 1][0])
            sigma += a ** 2
        sigma=math.sqrt(sigma/(6*m**2*(totN-3*m+1)))
        tdev.append([simTau,sigma])
        print '%.2f\t %s %s' % (simTau, sigma,m)
    return tdev

def ADEVTest():
    dataFile=unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171114200130-tdc2-13-2k-500s-3_residual-1-0.01s-ps.txt','utf8')
    saveFile=dataFile[:-4]+'_ADEV.txt'
    dataList=fileToList.fileToList(dataFile)
    adev=ADEV(dataList,0.01)
    fileToList.listToFileFloat(adev,saveFile)

def MDEVTest():
    dataFile=unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171121\\20171121230538-tdc2-13-2k-500s-dating-1_residual-2-0.01s-ps.txt','utf8')
    dataList=fileToList.fileToList(dataFile)
    saveFile = dataFile[:-4] + '_MDEV.txt'
    mdev=MDEV(dataList,0.01)
    fileToList.listToFileFloat(mdev, saveFile)

def TDEVTest():
    # dataFile=unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171125\\20171125162259-tdc2-2-4-2k-2_residual-1-0.01s-ps.txt','utf8')
    dataFile = unicode(
        'C:\Users\Levit\Experiment Data\德令哈测试\\20171213\\20171214003506-tdc2-2k-5-1_coindence_residual-2-0.01s-ps.txt',
        'utf8')

    dataList=fileToList.fileToList(dataFile)
    saveFile = dataFile[:-4] + '_TDEV.txt'
    tdev=TDEV(dataList,0.01)
    fileToList.listToFileFloat(tdev, saveFile)

if __name__=='__main__':
    TDEVTest()
