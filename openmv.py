import sensor, image, time, os, tf, math, uos, gc
#import sensor, image, time
import math
import ustruct
import json
import pyb
from pyb import UART,LED
#设置阈值，（0，100）检测黑色线
#THRESHOLD = (0, 46, -32, 38, -68, -14) # Grayscale threshold for dark things...
#THRESHOLD = (0, 46, -32, 38, -68, -14)  # Blue
#THRESHOLD=(0, 43, 1, 31, -51, -5)
#THRESHOLD=(0, 58, -128, 127, -42, -10) #grass
THRESHOLD=(0, 33, -128, 127, -38, 39) #without grass
roi1=(0,160,120,80)
roi2=(200,160,120,80)
#THRESHOLD=(28, 55, 20, 69, 20, 70) #RED
valid_threshold=0.01  #判断像素点是否符合要求
roi1_center=(50,200)  #roi的中心
roi2_center=(260,200)
roi1_aimdeg=50      #目标线的角度
roi2_aimdeg=130
roi1_aimtheta=roi1_aimdeg/360*2*3.14    #转成弧度
roi2_aimtheta=roi2_aimdeg/360*2*3.14
roi1_aimline=(int(roi1_center[0]+50/math.tan(roi1_aimtheta)),int(roi1_center[1]-50),int(roi1_center[0]-50/math.tan(roi1_aimtheta)),int(roi1_center[1]+50))
roi2_aimline=(int(roi2_center[0]+50/math.tan(roi2_aimtheta)),int(roi2_center[1]-50),int(roi2_center[0]-50/math.tan(roi2_aimtheta)),int(roi2_center[1]+50))
lab_threshold=(int(THRESHOLD[0]/2),int(THRESHOLD[1]/2-1),int((THRESHOLD[2]+128)/2),int((THRESHOLD[3]+128)/2-1),int((THRESHOLD[4]+128)/2),int((THRESHOLD[5]+128)/2-1))
#theta_coe=0.8
theta_coe=0
xaxis_coe=1
yaxis_coe=-1
uart = UART(3,115200)   #定义串口3变量
uart.init(115200, bits=8, parity=None, stop=1) # init with given parameters
def sending_data(bias,cy,cw,ch):
    global uart;
    #frame=[0x2C,18,cx%0xff,int(cx/0xff),cy%0xff,int(cy/0xff),0x5B];
    #data = bytearray(frame)
    data = ustruct.pack("<bbhhhhb",      #格式为俩个字符俩个短整型(2字节)
                   0x2C,                      #帧头1
                   0x12,                      #帧头2
                   str(bias), # up sample by 4   #数据1
                   int(bias_sign), # up sample by 4    #数据2
                   int(cw), # up sample by 4    #数据1
                   int(ch), # up sample by 4    #数据2
                   0x5B)
    uart.write(data);   #必须要传入一个字节数组

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_whitebal(True)
sensor.set_auto_gain(True)
#sensor.set_auto_gain(False)  # must be turned off for color tracking
#sensor.set_auto_whitebal(False)  # must be turned off for color tracking
#####################################

net = None
labels = None
min_confidence = 0.5

try:
    # load the model, alloc the model file on the heap if we have at least 64K free after loading
    net = tf.load("trained.tflite", load_to_fb=uos.stat('trained.tflite')[6] > (gc.mem_free() - (64*1024)))
except Exception as e:
    raise Exception('Failed to load "trained.tflite", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

try:
    labels = [line.rstrip('\n') for line in open("labels.txt")]
except Exception as e:
    raise Exception('Failed to load "labels.txt", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

colors = [ # Add more colors if you are detecting more than 7 types of classes at once.
    (255,   0,   0),
    (  0, 255,   0),
    (255, 255,   0),
    (  0,   0, 255),
    (255,   0, 255),
    (  0, 255, 255),
    (255, 255, 255),
    (170,20,255)
]
recognition_stack=[]

#####################################
clock = time.clock()
while(True):
    clock.tick()
    #img = sensor.snapshot().binary([THRESHOLD]) if BINARY_VISIBLE else sensor.snapshot()
    img=sensor.snapshot()
    img.draw_rectangle(190,50,96,96)
    label_value = 0
#####################################
    for i, detection_list in enumerate(net.detect(img,roi=(190,50,96,96), thresholds=[(math.ceil(min_confidence * 255), 255)])):
        if (i == 0): continue # background class
        if (len(detection_list) == 0): continue # no detections for this class?

        label = labels[i]
        print("********** %s **********" % label)


        if label == "background":
            label_value = 0
        elif label == "green":
            label_value = 1
        elif label == "left":
            label_value = 2
        elif label == "red":
            label_value = 3
        elif label == "right":
            label_value = 4
        elif label == "straight":
            label_value = 5
        elif label == "yellow":
            label_value = 6
        elif label == "yellowred":
            label_value = 7


        for d in detection_list:
            [x, y, w, h] = d.rect()
            center_x = math.floor(x + (w / 2))
            center_y = math.floor(y + (h / 2))
            print('x %d\ty %d' % (center_x, center_y))
            img.draw_circle((center_x, center_y, 12), color=colors[i], thickness=2)
    #max number record
    recognition_stack.append(label_value)
    if (len(recognition_stack)>20) : del recognition_stack[0]
    labelcount=[0,0,0,0,0,0,0,0]
    for element in recognition_stack:
        for index in range (0,7):
            if (element==index) : labelcount[index]=labelcount[index]+1
    final_label=labelcount.index(max(labelcount))
    if (labelcount[final_label]<8) : final_label=0

    # 检测到绿色标签时立即判断为绿色
    if labelcount[1] > 0:
        final_label = 1
    else:
        final_label = labelcount.index(max(labelcount))
        if labelcount[final_label] < 8:
            final_label = 0
    #print(clock.fps(), "fps", end="\n\n")
    print(final_label)


#####################################
    img.draw_cross(roi1_center,color=170)
    img.draw_cross(roi2_center,color=80)
    img.draw_line(roi1_aimline)
    img.draw_line(roi2_aimline)
    #Get two histogram classes
    hist1=img.get_histogram(roi=roi1,l_bins=50,a_bins=128,b_bins=128)
    hist2=img.get_histogram(roi=roi2,l_bins=50,a_bins=128,b_bins=128)
    #Get histogram for 3 tunnels of 2 regions
    l_hist1=hist1.l_bins()
    b_hist1=hist1.b_bins()
    a_hist1=hist1.a_bins()
    l_hist2=hist2.l_bins()
    b_hist2=hist2.b_bins()
    a_hist2=hist2.a_bins()
    #Get count of blue pixel in 3 tunnels of 2 regions
    roi1_l_pixelcount=0
    roi1_a_pixelcount=0
    roi1_b_pixelcount=0
    roi2_l_pixelcount=0
    roi2_a_pixelcount=0
    roi2_b_pixelcount=0
    for lindex in range(lab_threshold[0],lab_threshold[1]):
        roi1_l_pixelcount=roi1_l_pixelcount+l_hist1[lindex]
        roi2_l_pixelcount=roi2_l_pixelcount+l_hist2[lindex]
    for aindex in range(lab_threshold[2],lab_threshold[3]):
        roi1_a_pixelcount=roi1_a_pixelcount+a_hist1[aindex]
        roi2_a_pixelcount=roi2_a_pixelcount+a_hist2[aindex]
    for bindex in range(lab_threshold[4],lab_threshold[5]):
        roi1_b_pixelcount=roi1_b_pixelcount+b_hist1[bindex]
        roi2_b_pixelcount=roi2_b_pixelcount+b_hist2[bindex]
    #Determine if the result in both region is valid.
    if (roi1_l_pixelcount>valid_threshold and roi1_a_pixelcount>valid_threshold and roi1_b_pixelcount>valid_threshold):
        roi1_valid=1
    else:roi1_valid=0
    if (roi2_l_pixelcount>valid_threshold and roi2_a_pixelcount>valid_threshold and roi2_b_pixelcount>valid_threshold):
        roi2_valid=1
    else: roi2_valid=0
    #img.median(1, percentile=0.5)

    # Returns a line object similar to line objects returned by find_lines() and
    # find_line_segments(). You have x1(), y1(), x2(), y2(), length(),
    # theta() (rotation in degrees), rho(), and magnitude().
    #
    # magnitude() represents how well the linear regression worked. It goes from
    # (0, INF] where 0 is returned for a circle. The more linear the
    # scene is the higher the magnitude.

    # 函数返回回归后的线段对象line，有x1(), y1(), x2(), y2(), length(), theta(), rho(), magnitude()参数。
    # x1 y1 x2 y2分别代表线段的两个顶点坐标，length是线段长度，theta是线段的角度。
    # magnitude表示线性回归的效果，它是（0，+∞）范围内的一个数字，其中0代表一个圆。如果场景线性回归的越好，这个值越大。
    line1=0
    line2=0
    if(roi1_valid):line1 = img.get_regression([THRESHOLD],roi=roi1)
    if(roi2_valid):line2 = img.get_regression([THRESHOLD],roi=roi2)
    img.draw_rectangle(roi1)
    img.draw_rectangle(roi2)
    if (line1):
        img.draw_line(line1.line(), color = 255)
    if (line2):
        img.draw_line(line2.line(), color = 255)

    #print("FPS %f, mag = %s  x1=%s theta1=%s " % (clock.fps(), str(line1.magnitude()) if (line1) else "N/A",str(line1.x1()) if (line1) else "N/A",str(line1.theta()) if (line1) else "N/A"))
    if (line1):
        if(line2):#Use right line if both line exist
            xbias=(line2.x1()+line2.x2()-2*roi2_center[0])*xaxis_coe
            ybias=(line2.y1()+line2.y2()-2*roi2_center[1])*yaxis_coe
            cornerangle=line2.theta()-roi2_aimdeg
            if (cornerangle>90): cornerangle=cornerangle-180
            if (cornerangle<-90): cornerangle=cornerangle+180
            thetabias=cornerangle*theta_coe
            bias=xbias+thetabias+ybias
        else:#have line1 no line2
            xbias=(line1.x1()+line1.x2()-2*roi1_center[0])*xaxis_coe
            #ybias=-(line1.y1()+line1.y2()-2*roi1_center[1]) #y-axis manhatten distance and bias have opposite sign
            cornerangle=line1.theta()-roi1_aimdeg
            if (cornerangle>90): cornerangle=cornerangle-180
            if (cornerangle<-90): cornerangle=cornerangle+180
            thetabias=cornerangle*theta_coe
            bias=xbias+thetabias
    else:#No line1
        if(line2):#no line1 have line2
            xbias=(line2.x1()+line2.x2()-2*roi2_center[0])*xaxis_coe
            ybias=(line2.y1()+line2.y2()-2*roi2_center[1])*yaxis_coe
            cornerangle=line2.theta()-roi2_aimdeg
            if (cornerangle>90): cornerangle=cornerangle-180
            if (cornerangle<-90): cornerangle=cornerangle+180
            thetabias=cornerangle*theta_coe
            bias=xbias+thetabias+ybias
        else:#no line1 no line2
            bias=0

    bias=int(bias)
    #if (line1):print("xbias= %f | ybias= %f | cornerangle= %f | thetabias= %f | bias= %d \n" %(xbias,0,cornerangle,thetabias,bias))
    #print(bias)
    #print(clock.fps())
    #print("roi1_valid = %d| roi2_valid = %d" %(roi1_valid,roi2_valid))
    #print("r1_l= %f \ r1_a= %f \ r1_b= %f" %(roi1_l_pixelcount,roi1_a_pixelcount,roi1_b_pixelcount))
    #print(a_hist1)
    #print(lab_threshold)
    if bias>=0: bias_sign=0
    else:
        bias_sign=1
        bias=-bias



    FH = bytearray([0x2C, 0x12, int(bias), bias_sign, final_label, 0, 0x5B])
    uart.write(FH)
# About negative rho values:
# 关于负rho值:
#
# A [theta+0:-rho] tuple is the same as [theta+180:+rho].
# A [theta+0:-rho]元组与[theta+180:+rho]相同
