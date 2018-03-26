#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

# 数据分析画图

import matplotlib.pyplot as plt
import fileToList

# plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def logPlotAx(List,fig,c,l,m,lab):
    x=[]
    y=[]
    for item in List:
        x.append(item[0])
        y.append(item[1])
    ax=fig.add_subplot(111)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim((0.05,100))
    ax.set_ylim((5E-13,1E-9))
    ax.plot(x,y,color=c, linestyle=l, marker=m, label=lab)
    ax.xaxis.grid(True, which='minor') #x坐标轴的网格使用主刻度
    ax.yaxis.grid(True, which='minor') #y坐标轴的网格使用次刻度show()
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    ax.yaxis.grid(True, which='major') #y坐标轴的网格使用次刻度show()
    ax.set_ylabel('TDEV ',fontsize=24)
    ax.set_xlabel('Averaging Time (s)',fontsize=24)
    ax.set_title('Stability',fontsize=24)
    # ax.legend()
    plt.legend(loc=0, numpoints=1)
    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize=20)

def logPlotAxTest():
    # dataFile1=unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\6.13-2k-0.01s-all.txt','utf8')
    # dataFile2=unicode('E:\Experiment Data\时频传输数据处理\双站数据处理\\6.14NS\\6.14-60-170-timeWalkLinear.txt','utf8')
    # dataFile1=unicode('C:\Users\Levit\Experiment Data\德令哈测试\\20171226\零基线实验\\20171227015305-tdc2_5_filterN_coindence_filtered_250-350s_residual-1-0.1s-ps_TDEV.txt','utf8')
    # dataFile1 = unicode('C:\Users\Levit\Experiment Data\Rakon晶振测试数据\两TDC测试\\20171116\\20171116220334-tdc2-13-4-10-4000s_residual-1-0.1s-ps_TDEV.txt', 'utf8')
    # dataFile2 =unicode('C:\Users\Levit\Experiment Data\德令哈测试\\20171226\零基线实验\\20171227015305-tdc2_4_filterN_coindence_filtered_250-350s_residual-1-0.1s-ps_TDEV.txt','utf8')

    dataFile3  =unicode('C:\Users\Levit\Experiment Data\双站数据\\20180121\\result\\synCoincidence-124-216--17-1-Coin-紫台WGS84-atm-factor-haiji_laser改正_filtered_residual-2-0.1s-ps_TDEV.txt','utf8')
    # dataFile4  =unicode('C:\Users\Levit\Experiment Data\双站数据\\20180108\\result\\synCoincidence-165-265--11-0-Coin-紫台WGS84-atm-factor-neworbit_filtered_residual-6-0.1s-ps_TDEV.txt','utf8')
    # dataFile5 =unicode('C:\Users\Levit\Experiment Data\双站数据\\20180108\\result\\synCoincidence-165-265--11-0-Coin-紫台WGS84-atm-factor-neworbit_filtered_residual-7-0.1s-ps_TDEV.txt','utf8')
    # dataFile6 =unicode('C:\Users\Levit\Experiment Data\双站数据\\20180108\\result\\synCoincidence-165-265--11-0-Coin-紫台WGS84-atm-factor-neworbit_filtered_residual-20-0.1s-ps_TDEV.txt','utf8')

    # List1=fileToList.fileToList(dataFile1)
    # List2=fileToList.fileToList(dataFile2)
    List3=fileToList.fileToList(dataFile3)
    # List4=fileToList.fileToList(dataFile4)
    # List5=fileToList.fileToList(dataFile5)
    # List6 = fileToList.fileToList(dataFile6)
    fig=plt.figure()
    # logPlotAx(List1,fig,'g','--','o','12.26 DLH-DLH,250-350s light,1 order fit')
    # logPlotAx(List2,fig,'r','--','s','12.26 DLH-DLH,250-350s electronic,1 order fit')
    logPlotAx(List3,fig,'c','--','^','01.21 LJ-DLH,124-216s, Laser correction, 2 order fit')
    # logPlotAx(List4,fig,'b','--','v','01.08 LJ-DLH,165-265s, 6 order fit')
    # logPlotAx(List5, fig, 'y', '--', 'v', '01.08 LJ-DLH,165-265s, 7 order fit')
    # logPlotAx(List6, fig, 'k', '--', '+', '01.08 LJ-DLH,165-265s, 20 order fit')

    plt.show()

if __name__=='__main__':
    logPlotAxTest()
