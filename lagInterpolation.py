# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 13:26:58 2016
@author: tete
@brief: 拉格朗日插值法
"""
import matplotlib.pyplot as plt

"""
@brief: 获得拉格朗日插值基函数
@param: xi      xi为第i个插值节点的横坐标
@param: x_set   整个插值节点集合
@return: 返回值为参数xi对应的插值基函数
"""


def get_li(xi, x_set=[]):
    def li(Lx):
        W = 1.0;
        c = 1.0
        for each_x in x_set:
            if each_x == xi:
                continue
            W = W * (Lx - each_x)
        for each_x in x_set:
            if each_x == xi:
                continue
            c = c * (xi - each_x)
        # 这里一定要转成float类型，否则极易出现严重错误. 原因就不说了
        return W / float(c)

    return li


"""
@brief: 获得拉格朗日插值函数
@param: x       插值节点的横坐标集合
@param: fx      插值节点的纵坐标集合
@return: 参数所指定的插值节点集合对应的插值函数
"""


def get_Lxfunc(x=[], fx=[]):
    set_of_lifunc = []
    for each in x:  # 获得每个插值点的基函数
        lifunc = get_li(each, x)
        set_of_lifunc.append(lifunc)  # 将集合x中的每个元素对应的插值基函数保存

    def Lxfunc(Lx):
        result = 0.0
        for index in range(len(x)):
            result = result + fx[index] * (set_of_lifunc[index](Lx))  # 根据根据拉格朗日插值法计算Lx的值
            # print fx[index]
        return result

    return Lxfunc


"""
demo:
"""

if __name__ == '__main__':

    ''' 插值节点, 这里用二次函数生成插值节点，每两个节点x轴距离位10 '''
    gps = open(unicode('G:\\时频传输数据处理\\双站数据处理\\3.2\\DLH\\GPS_Recv.txt', 'utf8'))
    sr_x = [i for i in range(1, 10)]
    sr_fx = []
    for i in range(1, 10):
        s = float(gps.readline().strip())
        sr_fx.append(s)
    gps.close()
    Lx = get_Lxfunc(sr_x, sr_fx)  # 获得插值函数
    tmp_x = [float(i / 10000.0) for i in range(1, 100)]  # 测试用例
    tmp_y = [Lx(float(i)) for i in tmp_x]  # 根据插值函数获得测试用例的纵坐标
    print tmp_y
    ''' 画图 '''
    plt.figure("play")
    ax1 = plt.subplot(111)
    plt.sca(ax1)
    # plt.plot(sr_x, sr_fx, linestyle = ' ', marker='o', color='b')
    plt.plot(tmp_x, tmp_y, linestyle='--', color='r')
    plt.show()
