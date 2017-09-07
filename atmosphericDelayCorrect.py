#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'

#激光的大气延时修正模型

import math

#根据温度计算饱和蒸汽压: https://en.wikipedia.org/wiki/Vapour_pressure_of_water
# 采用 Arden Buck equation: https://en.wikipedia.org/wiki/Arden_Buck_equation
#返回单位 kPa
def saturatedVaporPressure(t):
    if t>=0:
        Ps=0.61121*(math.exp((18.678-t/234.5)*(t/(257.14+t))))
    else:
        Ps=0.61115*(math.exp((23.036-t/333.7)*(t/(279.82+t))))
    #print 'Saturated Vapor Pressure at %s degree is %s kPa'%(t,Ps)
    return Ps

#根据相对湿度和温度计算大气的水汽压
def surfaceWaterVaporPressure(t,RH):
    Pe=saturatedVaporPressure(t)*RH/100.0
    #print 'the Surface Water Vapor Pressure at %s degree Celsius, %s percent relative humidity is %s kPa'%(t,RH,Pe)
    return Pe

#Mendes-Pavlis zenith delay model
#文献：High-accuracy zenith delay prediction at optical wavelengths
#波长单位um,纬度单位为弧度，高度单位千米，大气压单位为Pa,返回值为延迟量，单位为米
def MPZenithDelayModel(wavelength,latitude,height,baroPressure,es):
    hk0=238.0185;hk1=5792105;hk11=19990.975;hk2=57.362;hk33=579.55174;hk3=167917
    w0=295.235;w1=2.6422;w2=-0.032380;w3=0.004028;cf=1.022
    sigma=1.0/wavelength;xc=375;Cco2=1.0+0.534*(xc-450)/1000000.0
    Pd=101325;Td=288.15;td=15.0;Tw=293.15;Pw=1333.0
    a0=1.58123/1000000.0;a1=-2.9331/100000000.0;a2=1.1043/10000000000.0;d0=1.83/100000000000.0
    Rd=287.07153;v=4;epsion=0.621996
    Zd=1-(Pd/Td)*(a0+a1*td+a2*td**2)+d0*(Pd/Td)**2
    Ngaxs=(hk1*(hk0+sigma**2)/(hk0-sigma**2)**2+hk3*(hk2+sigma**2)/(hk2-sigma**2)**2)*Cco2/100.0
    dh=Ngaxs*(Td/Pd)*Zd*Rd*baroPressure/(9.784*(1-0.00266*math.cos(2*latitude)-0.00028*height))/1000000.0
    #fh=(hk11*(hk0+sigma**2)/(hk0-sigma**2)**2+hk33*(hk2+sigma**2)/(hk2-sigma**2)**2)*Cco2/100.0
    #dh=0.00002416579*fh*baroPressure/(9.784*(1-0.00266*math.cos(2*latitude)-0.00028*height))

    Ngws=cf*(w0+3*w1*sigma**2+5*w2*sigma**4+7*w3*sigma**6)/100.0
    dnh=0.000001*(Ngws*(Tw/Pw)-Ngaxs*(Td/Pd)*epsion)*Rd*es/(v*9.784*(1-0.00266*math.cos(2*latitude)-0.00028*height))
    #fnh=0.003101*(w0+3*w1*sigma**2+5*w2*sigma**4+7*w3*sigma**6)
    #dnh1=0.000001*(5.316*fnh-3.759*fh)*es/((1-0.00266*math.cos(2*latitude)-0.00028*height))
    #print Ngaxs,dnh,dnh1
    delay=dh+dnh
    # print 'the zenith delay is %s m, and dry part is %s m, moist part is %s m'%(delay,dh,dnh)
    return delay

#俯仰角的Map函数
#文献：Improved mapping functions for atmospheric refraction correction in SLR
#俯仰角单位：弧度;温度：摄氏度；纬度：弧度；高度：米
def mapFun(elevationAngle,t,latitude,height):
    a10=12100.8*10**(-7);a11=1729.5*10**(-9);a12=319.1*10**(-7);a13=-1847.8*10**(-11)
    a20=30496.5*10**(-7);a21=234.6*10**(-8);a22=-103.5*10**(-6);a23=-185.6*10**(-10)
    a30=6877.7*10**(-5);a31=197.2*10**(-7);a32=-345.8*10**(-5);a33=106.0*10**(-9)
    a1=a10+a11*t+a12*math.cos(latitude)+a13*height
    a2=a20+a21*t+a22*math.cos(latitude)+a23*height
    a3=a30+a31*t+a32*math.cos(latitude)+a33*height
    mapFactor=(1+a1/(1+a2/(1+a3)))/(math.sin(elevationAngle)+a1/(math.sin(elevationAngle)+a2/(math.sin(elevationAngle)+a3)))
    #print 'elevation angle at %s,the mapFactor is %s'%(elevationAngle,mapFactor)
    return mapFactor

#根据激光波长、测站纬度、高度、温度、大气压、相对湿度、观测俯仰角等参数，利用上面天顶延迟函数和俯仰角map函数计算大气延时
#返回值为距离，单位米
def MPAtmDelayModelCal(wavelength,latitude,height,baroPressure,t,RH,elevationAngle):
    latitudeR=latitude*math.pi/180.0
    elevationAngleR=elevationAngle*math.pi/180.0
    heightK=height/1000.0
    es=surfaceWaterVaporPressure(t,RH)*1000.0
    zenithDelay=MPZenithDelayModel(wavelength,latitudeR,heightK,baroPressure,es)
    mapFactor=mapFun(elevationAngleR,t,latitudeR,height)
    delay=zenithDelay*mapFactor
    #print 'delay is %s m'%delay
    return delay

if __name__=='__main__':
    MPAtmDelayModelCal(0.85,37.37901,3153,69610,-10,50,20)
    MPAtmDelayModelCal(0.85,37.37901,3153,69610,-15,50,20)
    MPAtmDelayModelCal(0.532,32.33901,5045,45270,10,50,10)
    MPAtmDelayModelCal(1.064,32.33901,5045,45270,10,50,10)
    MPAtmDelayModelCal(1.064,32.33901,5045,45270,10,50,10.1)
