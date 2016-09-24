# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 10:59:18 2016

@author: dwight
"""


import cv2, re, json, subprocess
import numpy as np
from matplotlib import pyplot as plt

###############################################################################
#Functions
###############################################################################
def removeWhite(img):
    (wH, wW) = img.shape[:2]
    img = np.dstack([img, np.ones((wH, wW), dtype="uint8") * 1])
    (x,y,z)=img.shape
    x=x
    y=y
    z=z-1
    for i in range(0,x) :
        for j in range(0,y) :
            sm=0
            for k in range(0,z) :
                sm=sm+ int(img[i-1, j-1, z-2])
            if sm>650:
                img[i-1,j-1,:]=0
                
                
    
    (B, G, R, A) = cv2.split(img)
    B = cv2.bitwise_and(B, B, mask=A)
    G = cv2.bitwise_and(G, G, mask=A)
    R = cv2.bitwise_and(R, R, mask=A)
    img = cv2.merge([B, G, R, A])
    return img
#------------------------------------------------------------------------------        
def addData(event,x,y,flags,param):
    global overlayTxt, txtMoveMode, indx
    
    if event == cv2.EVENT_LBUTTONDBLCLK:
        txtMoveMode = 'FOLLOW_MOUSE'
        print event, txtMoveMode, overlayTxt[0]['txt']
        indx=closeTxt(x,y)
        if indx<0:
            txtMoveMode = 'NONE'
        
    if (event == cv2.EVENT_MOUSEMOVE) and (txtMoveMode == 'FOLLOW_MOUSE'):       
        overlayTxt[indx]['pos_X']=x
        overlayTxt[indx]['pos_Y']=y
        
    if (event == cv2.EVENT_LBUTTONDOWN) and (txtMoveMode == 'FOLLOW_MOUSE'):
        txtMoveMode = 'NONE'
        overlayTxt[indx]['pos_X']=x
        overlayTxt[indx]['pos_Y']=y
#------------------------------------------------------------------------------
def closeTxt(mouseX,mouseY):
    global overlayTxt
    for i in range(0, len(overlayTxt)):
        if (abs(overlayTxt[i]['pos_X']-mouseX)<100) and (abs(overlayTxt[i]['pos_Y']-mouseY)<10):
            break
        else:
            i=-1
    print 'Nearest text is at: ',i 
    return i
            
#------------------------------------------------------------------------------
def updateOverlay(originalOverlay):
    global overlayTxt,h,w
    overlayTxt[0]['txt'] = "core 1 temperature: " + str(json.loads(getCpuData())["Core 0"])
    overlayTxt[1]['txt'] = "core 2 temperature: " + str(json.loads(getCpuData())["Core 1"])
    overlayTxt[2]['txt'] = 'frame count: ' + str(frameCnt)

    newOverlay=originalOverlay
    
    for element in overlayTxt:
        if element['type']=='text':
            txt = element['txt']
            pos_X = element['pos_X']
            pos_Y = element['pos_Y']
            cv2.putText(newOverlay,txt,(pos_X,pos_Y), font, 0.5,(7, 246, 10),2)
        if element['type']=='image':
            
            img = cv2.imread(element['txt'])            
            img = removeWhite(img)
            (wH, wW) = img.shape[:2]
            
            pos_X = element['pos_X']
            pos_Y = element['pos_Y']
            
            img_X1 = pos_X-wW/2
            img_X2 = pos_X+wW/2
            img_Y1 = pos_Y-wH/2
            img_Y2 = pos_Y+wH/2
            
            fence = 10
            margin = fence + 5
            
            if (img_X2>=w-fence) or (pos_X>=w):
                print "violation"
                img_X1 = w - wW - margin
                img_X2 = w-margin
                pos_X = img_X2 - wW/2
                
            if img_X1<=fence:
                print "violation"
                img_X1 = margin
                img_X2 = img_X1 + wW
                pos_X = img_X1 + wW/2
                
            if img_Y2>=h-fence:
                print "violation"
                img_Y1 = h - wH - margin
                img_Y2 = h-margin
                pos_Y = img_Y2 - wH/2
                
            if img_Y1<=fence:
                print "violation"
                img_Y1 = margin#h - wH - 10
                img_Y2 = img_Y1 + wH#h-10
                pos_Y = img_Y2 - wH/2
            
            element['pos_X'] = pos_X
            element['pos_Y'] = pos_Y
            newOverlay[img_Y1:img_Y2, img_X1:img_X2] = img
            cv2.putText(newOverlay,str(pos_X),(pos_X,pos_Y), font, 0.5,(7, 246, 10),2)
    
    return newOverlay
#------------------------------------------------------------------------------
def getCpuData():
    sensors = subprocess.check_output("sensors")
    data = {match[0]: float(match[1]) for match in re.findall("^(.*?)\:\s+\+?(.*?)°C", sensors, re.MULTILINE)}
    return json.dumps(data)
###############################################################################
#Init setup
###############################################################################
cv2.namedWindow('overlayedVideo')
cv2.setMouseCallback('overlayedVideo',addData)

img = cv2.imread("icon2.jpg")

img = removeWhite(img)

(wH, wW) = img.shape[:2]
cap=cv2.VideoCapture(0)
ret, firstFrame = cap.read()
(h, w) = firstFrame.shape[:2]
###############################################################################
#Globals
###############################################################################
font = cv2.FONT_HERSHEY_SIMPLEX

frameCnt=0
indx = -1
txtMoveMode='NONE'

overlayTxt= np.array([(384,155, 'text', 'Hello'),
                      (384,55, 'text', frameCnt),
(384,255, 'text', 'World')],
dtype=[('pos_X', 'i'),('pos_Y', 'i'),('type', 'S10'),('txt', 'S200')])

###############################################################################
#Loop
###############################################################################

while(cap.isOpened()):
    ret, frame = cap.read()
    frameCnt=frameCnt+1
    
    (h, w) = frame.shape[:2]
    frame = np.dstack([frame, np.ones((h, w), dtype="uint8") * 255])
    
    overlay = np.zeros((h, w, 4), dtype="uint8")
    overlay[h - wH - 10:h - 10, w - wW - 10:w - 10] = img
    
    overlay = updateOverlay(overlay)
    
    cv2.addWeighted(overlay, 0.25, frame, 1.0, 0, frame)
 	   
    cv2.imshow('overlayedVideo',frame)
    
    if cv2.waitKey(35) & 0xFF == ord('q'):
        break
    
   

cap.release()
cv2.destroyAllWindows()