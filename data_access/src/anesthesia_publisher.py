#! /home/lab129/anaconda3/bin/python3
import pandas as pd
import time
import socket
from hl7parser.hl7 import HL7Message
import rospy
from data_access.msg import Anesthesia
# 以下指标列表将会存一次完整测量中病人对应指标的序列
SYSP = []                           # 收缩压
DIAP = []                           # 舒张压
RATE = []                           # 血氧脉搏
SaO2 = []                           # 血氧
BIS = []                            # BIS
TIME = []                           #时间戳
ID = []
bfer = []                           #缓冲区
indexList = [                       #所有指标的列表
             SYSP,                    
             DIAP,
             RATE,
             SaO2,
             #MDC_ECG_HEART_RATE,
             BIS,
             #MNDRY_ECG_VPB_RATE,
             #MNDRY_ECG_PACING_NON_CAPT_RATE,
             #MNDRY_ECG_PACER_NOT_PACING_RATE,
             #SpO22,
             TIME,
             ID
             ]

nameList = [
            "SYSP",
            "DIAP",
            "RATE",
            "SaO2",
            "SpO2",
            #"MDC_ECG_HEART_RATE",
            "BIS",
            #"MNDRY_ECG_VPB_RATE",
            #"MNDRY_ECG_PACING_NON_CAPT_RATE",
            #"MNDRY_ECG_PACER_NOT_PACING_RATE",
            #"MDC_PULS_OXIM_PULS_RATE",
            "TIME"
            "ID"
        ]   
def datarec():
    #####################################################################
    ################# initialize ROS ####################################
    #####################################################################
    #ROS节点初始化
    rospy.init_node("anesthesia_publisher",anonymous = True)
    #创建一个Publisher,发布名是/anesthesia_info的topic，消息类型是main_topic::Anesthesia,队列长度为100
    anesthesia_info_pub = rospy.Publisher("/anesthesia_info",Anesthesia,queue_size = 1000)
    #设置循环的频率
    rate = rospy.Rate(10)
    #开始接受数据
    while not rospy.is_shutdown():
        #####################################################################
        ################# initialize get data from machine ##################
        #####################################################################
        #初始化 保证没有的数据会输出-1
        anesthesia_msg = Anesthesia()
        anesthesia_msg.MDC_PULS_RATE_NON_IN = -1
        anesthesia_msg.MDC_PRESS_CUFF_DIA = -1
        anesthesia_msg.MDC_PRESS_CUFF_SYS = -1
        anesthesia_msg.MDC_PULS_OXIM_SAT_O2 = -1
        anesthesia_msg.MDC_BLD_PERF_INDEX = -1
        # 创建套接字 socket
        tcpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 绑定本地信息 bind
        tcpServerSocket.bind(("", 7890))

        # 让默认的套接字由主动变为被动 listen                                             
        tcpServerSocket.listen(128)
                                        
        newClientSocket, clientAddr =tcpServerSocket.accept()                                 

        recv_data = newClientSocket.recv(1024) 
        rospy.loginfo('ready')
       
        timeStamp = time.asctime(time.localtime())

        #将接受到的信息转换成所需要的格式   
        message = str(recv_data,'utf-8')
        rospy.loginfo(message)
        li = message.split('\r')    
        if '' in li:
            li.remove('')   
        li[0] = li[0][1:]    
        finalmessage = ''        
        if li[0][0:3]=="MSH" and len(bfer)==0:
            bfer.append(li)
            print('appended!')
        else:
            if li[0][0:3]!="MSH":
                print("ceshi:",li[0][0:3])
                zhongjian = bfer[-1]
                zhongjian[-1] = zhongjian[-1] + li[0]
                for x in li[1:]:
                    zhongjian.append(x)
                bfer[0] = zhongjian
                continue
            else:
                li,bfer[0] = bfer[0],li
            for x in li:
                finalmessage += x+'\r'
            #print('finalmsg         ',finalmessage)

            msg = HL7Message(finalmessage)
            # 下面的分叉用于给各项指标和显示列表分发测量数据
            for t in msg.obx: 
                index = str(t[2]).split('^')[1]
                value = t[4]
                if index == 'MDC_ECG_HEART_RATE':
                    anesthesia_msg.RATE = str(value)    
                elif index == 'MDC_PRESS_CUFF_DIA':
                    anesthesia_msg.DIAP = str(value)
                elif index == 'MDC_PRESS_CUFF_SYS':
                    anesthesia_msg.SYSP = str(value)
                elif index == 'MDC_PULS_OXIM_SAT_O2':
                    anesthesia_msg.SpO2 = str(value)
                elif index == 'MDC_BLD_PERF_INDEX':
                    anesthesia_msg.SaO2 = str(value)
                elif index == 'MNDRY_EEG_BISPECTRAL_INDEX':
                    anesthesia_msg.BIS = str(value)
                if value == '':
                    pass
            #发布消息
            anesthesia_info_pub.publish(anesthesia_msg)
            rospy.loginfo("publish anesthesia message[%s %s %s %s %s]",anesthesia_msg.RATE
            ,anesthesia_msg.DIAP,anesthesia_msg.SYSP,anesthesia_msg.SpO2,
            anesthesia_msg.SaO2,anesthesia_msg.BIS)
            #按照循环频率延时
            rate.sleep()
    # 析构 of sockets
    newClientSocket.close()
    tcpServerSocket.close()
if __name__ == "__main__":
    try:
        rospy.loginfo('ready')
        datarec()
    except rospy.ROSInterruptException:
        pass
