#Библиотеки
import math
import numpy as np
import cv2
import rospy
from clover import srv
from std_srvs.srv import Trigger
from mavros_msgs.srv import CommandBool
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from clover.srv import SetLEDEffect
import time

rospy.init_node('flight')

bridge = CvBridge()

get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
navigate_global = rospy.ServiceProxy('navigate_global', srv.NavigateGlobal)
set_position = rospy.ServiceProxy('set_position', srv.SetPosition)
set_velocity = rospy.ServiceProxy('set_velocity', srv.SetVelocity)
set_attitude = rospy.ServiceProxy('set_attitude', srv.SetAttitude)
set_rates = rospy.ServiceProxy('set_rates', srv.SetRates)
land = rospy.ServiceProxy('land', Trigger)
arming = rospy.ServiceProxy('mavros/cmd/arming', CommandBool)
set_effect = rospy.ServiceProxy('led/set_effect', SetLEDEffect)  # define proxy to ROS-service


DEBUG = False
# Предварительный просмотр отладочного изображения 
def imshow(n, i):
    global DEBUG
    if DEBUG:
        cv2.imshow(n, i)

# Распознавание
def rec(img):
  
    ret = ""
    h, w, _ = img.shape # Размеры изображения
    img = img[0+20:h-20,0+50:w-50] # Обрезка изображения

    # Копирование изображения
    deb = img.copy()
    
    # Фильтрация
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    d = np.clip(11*(hsv[:, :, 1].astype("float")*hsv[:, :, 2].astype("float") / (255*255))**1.6, 0, 1)
    d2 = d > 0.25
    d2 = (d2*255).astype("uint8")
    d3 = d2.copy()
    # d3 = cv2.erode(d2, np.ones((3, 3), dtype="uint8"))
    d3 = cv2.dilate(d3, np.ones((6, 6), dtype="uint8"))
    # d3 = cv2.medianBlur(d3, 5)
    # d3 = cv2.erode(d3, np.ones((5, 5), dtype="uint8"))

    imshow("hsv", hsv)
    imshow("d", (d*255).astype("uint8"))
    imshow("d2", d2)
    imshow("d3", d3)

    dout = d3

    cnts = cv2.findContours(dout, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cnts) == 0:
        return "", deb
    
    
    # contour 
    cnts = sorted([cnt for cnt in cnts if cv2.contourArea(cnt) > 2700], key=cv2.contourArea, reverse=True)
    cv2.drawContours(deb, cnts, -1, (0,255,0), 3)
    if len(cnts) == 0:
        return "", deb
    
    cnt = cnts[0]

    # print(cv2.contourArea(cnt))
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.array(box, dtype="int")
    
    
    cv2.drawContours(deb, [cnt], -1, (0,0,255), 3)
    cv2.drawContours(deb,[box],0,(255,0,0),2)
    

    for i, b in enumerate(box):
        cv2.circle(deb, (b[0], b[1]), 10, (0, 255.0*(i)/4.0, 0), -1)


    # croping 

    pts2 = np.float32([[0, 50], [0, 0], [50, 0], [50, 50]])
    # print(box)
    pts1 = np.float32(box)
    M = cv2.getPerspectiveTransform(pts1, pts2)
    croped = cv2.warpPerspective(img, M, (50, 50))
    imshow("croped", croped)

    # classifying 
    croped_hsv = cv2.cvtColor(croped, cv2.COLOR_BGR2HSV)
    chsv_d = croped_hsv.astype("float")/255.0
    cd = (chsv_d[:, :, 1] > 0.2)*(chsv_d[:, :, 2] > 0.2)

    red_t = ((chsv_d[:, :, 0] > 0.5)*(chsv_d[:, :, 0] < 1))*cd
    rr = (red_t < 0.5)*chsv_d[:, :, 0]*cd
    # green = ((chsv_d[:, :, 0] > 0.44)*(chsv_d[:, :, 0] < 0.45))*cd
    # blue = ((chsv_d[:, :, 0] > 0.45)*(chsv_d[:, :, 0] < 0.5))*cd
    imshow("cd", (cd*255*chsv_d[:, :, 0]).astype("uint8"))
    imshow("rr", (rr*255).astype("uint8"))
    # imshow("green", (green*255).astype("uint8"))
    # imshow("blue", (blue*255).astype("uint8"))
    red = np.count_nonzero(red_t) > 100
    green = np.count_nonzero((rr > 0.36)*(rr< 0.4)) > 100
    blue = np.count_nonzero((rr > 0.405)*(rr< 0.5)) > 100
    yellow = np.count_nonzero((rr < 0.58)*(rr > 0.4)) > 100
    # print(red, green, blue)
    flag = (red, green, blue)
    if red == True:
        ret = "red"
    if green == True:
        ret = "green"
    if blue == True:
        ret = "blue"
    if yellow == True:
        ret = "Germany"
        
    if flag == (True, True, False):
        ret = "Italy"
    if flag == (True, False, True):
        ret = "USA"
    if flag == (True,False, False):
        ret = "George"
    if flag == (False, False, True):
        ret = "Finland"
    # red = 
    # blue = 
    # green = 
    

    imshow("deb", deb)
    return ret, deb


# points coordinates
Z_POINTS = 1.43

points = {
    "p1" : [0.75, 0.75, Z_POINTS],
    "p2" : [1.5, 0, Z_POINTS],
    "p3" : [0.75*4, 0.75*2, Z_POINTS],
    "land" : [0, 0, 1.5]
}

to_display = ""

# debug publishers 
image_pub = rospy.Publisher('/detect/debug', Image)
image_pub2 = rospy.Publisher('/detect/debug2', Image)

prev_t = ""
prev_t_tt = time.time()

# callback for subcriber to /main_camera/image_raw_throttled
def image_callback(data):
    global to_display, image_pub, image_pub2, prev_t, prev_t_tt
    img_cam = bridge.imgmsg_to_cv2(data, 'bgr8')
    img_debug = img_cam.copy()

    t, deb = reg(img_cam)
    if t != "":
        to_display = t
    elif (time.time() - prev_t_tt) < 2:
        to_display = prev_t
    
    cv2.putText(img_debug, to_display, (20, 20), 1, 1, (0, 255, 0))

    image_pub.publish(bridge.cv2_to_imgmsg(img_debug, "bgr8"))
    image_pub2.publish(bridge.cv2_to_imgmsg(deb, "bgr8"))
    prev_t_tt = time.time()
    prev_t = t


# sub to /main_camera/image_raw_throttled
image_sub = rospy.Subscriber('main_camera/image_raw_throttled', Image, image_callback)

# navigate to point and wait
def navigate_wait(x=0, y=0, z=0, yaw=float('nan'), speed=0.5, frame_id='', auto_arm=False, tolerance=0.2):
    navigate(x=x, y=y, z=z, yaw=yaw, speed=speed, frame_id=frame_id, auto_arm=auto_arm)

    while not rospy.is_shutdown():
        telem = get_telemetry(frame_id='navigate_target')
        if math.sqrt(telem.x ** 2 + telem.y ** 2 + telem.z ** 2) < tolerance:
            break
        rospy.sleep(0.2)



print("points", points)

# takeoff
navigate(z=1, x=0, y=0, yaw=float('nan'), frame_id="body", speed=1, auto_arm=True)
rospy.sleep(3)
navigate(x=0, y=0, z=1, yaw=float('nan'), frame_id="aruco_map", speed=0.5)
rospy.sleep(2)
######

def navigate_to_pnt(name):
    global points
    print("going to", name)
    navigate_wait(x=points[name][0], y=points[name][1], z=points[name][2], frame_id="aruco_map", speed=0.65, tolerance=0.3)
    print("at", name)


# fly to points
rep = []

for i, f in enumerate(["p1", "p2", "p3"]):
    set_effect(r=0, g=0, b=0)
    navigate_to_pnt(f)
    rospy.sleep(2)
    t = to_display
    if t != "":
        print(t)
    if t == "red":
        set_effect(r=255, g=0, b=0)
    if t == "blue":
        set_effect(r=0, g=0, b=255)
    if t == "green":
        set_effect(r=0, g=255, b=0)
    if t == "yellow":
        set_effect(r=255, g=255, b=0)
    
    rep.append(str(i+1) + ") " + t + " (" + str(points[f][0]) + ", " + str(points[f][1]) + ")")
    rospy.sleep(3)
    set_effect(r=0, g=0, b=0)


# write report 
open("report_fly_5.txt", "w").write("\n".join(rep))

# land
navigate_to_pnt("land")
land()
rospy.sleep(3)
arming(False)
