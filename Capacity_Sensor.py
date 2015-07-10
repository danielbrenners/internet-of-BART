import RPi.GPIO as GPIO
import picamera
import numpy as np
from scipy import misc
from scipy import ndimage
import time as thyme

import smbus
import time
import os

import requests
from datetime import datetime,time,timedelta
import json


GPIO.setmode(GPIO.BCM)

GPIO.setup(19, GPIO.OUT)
GPIO.output(19,1)
GPIO.setup(16, GPIO.IN)

def pushtobase(index):
	print "index to write = ",index
	print "reading density model, and rating"
	densityValues=readIndex(index)
	startTime=datetime.utcnow().isoformat()[0:-7] + 'Z'
	density=densityValues['density']
	crowded="Low Crowding"
	if(density>7):
		crowded="Overcrowded"
	elif density>4:
		crowded="Medium Crowding"
	train_density_index=2
	payload={"actor": {"displayName": "BARTtrain","id": "1","objectType": "train"},"verb": "checkin","published": startTime,"status": "completed","object": {"displayName":"Car1","dataFields": {"train_length": 1,"train_route": 7,"train_index": 72,"route_start": "SFIA","route_end": "PITT","station_previous": "ROCK","station_next": "ORIN","car_1": {"car_density_index": density,"overcrowded": crowded}},"objectType": "trainRecord"},"target" : {"url": "http://example.org/blog/","objectType": "blog","id": "tag:example.org,2011:abc123","displayName": "Berkeley"}}
	url="http://russet.ischool.berkeley.edu:8080/activities"
	headers = { 'Content-Type': 'application/stream+json' }
	try:
		print "NOW MAKING THE PUSH !!!!"
		r = requests.post(url, data=json.dumps(payload), headers=headers)
		print r
	except Exception as e:
		print e

def readIndex(index):
	#build a model to convert raw pixel counts into index
	scale=float(index)
	minScale=100
	maxScale=5000000
	newindex=(scale-minScale)*10/(maxScale-minScale)
	print newindex
	if index<minScale:
		return {'density':0}
	elif index>maxScale:
		return {'density':10}
	else:
		print (scale-minScale)*10/(maxScale-minScale)
		return {'density':int(round((scale-minScale)*10/(maxScale-minScale)))}

class Accel():
        myBus=1
        if GPIO.RPI_REVISION == 1:
            myBus=1
        elif GPIO.RPI_REVISION == 2:
            myBus=1
        b = smbus.SMBus(myBus)
        def setUp(self):
            self.b.write_byte_data(0x1D,0x16,0x55) # Setup the Mode
            self.b.write_byte_data(0x1D,0x10,0) # Calibrate
            self.b.write_byte_data(0x1D,0x11,0) # Calibrate
            self.b.write_byte_data(0x1D,0x12,0) # Calibrate
            self.b.write_byte_data(0x1D,0x13,0) # Calibrate
            self.b.write_byte_data(0x1D,0x14,0) # Calibrate
            self.b.write_byte_data(0x1D,0x15,0) # Calibrate
        def getValueX(self):
            return self.b.read_byte_data(0x1D,0x06)
        def getValueY(self):
            return self.b.read_byte_data(0x1D,0x07)
        def getValueZ(self):
            return self.b.read_byte_data(0x1D,0x08)


MMA7455 = Accel()
MMA7455.setUp()

#Calibrate the resting state of X acceleration
calibrateX = False
while calibrateX == False:
    read1 = MMA7455.getValueX()
    read2 = MMA7455.getValueX()
    read3 = MMA7455.getValueX()
    read4 = MMA7455.getValueX()
    read5 = MMA7455.getValueX()
    Xvalues = [read1, read2, read3, read4, read5]
    
    if (max(Xvalues) - min(Xvalues)) < 3:
        calibrateX = True
        restingX = sum(Xvalues) / len(Xvalues)
        
movementSensitivity = 4 #How sensitive the BART is to movement

while True:
    x = MMA7455.getValueX()
    y = MMA7455.getValueY()
    z = MMA7455.getValueZ()
    print("X = ", x)
    print("Y = ", y)
    print("Z = ", z)
#   time.sleep(0.5)
    os.system("clear")


    if GPIO.input(16) == 1:
        with picamera.PiCamera() as camera:
            camera.capture('background.jpg')
        background = misc.imread('background.jpg')

    if x > (restingX + movementSensitivity):
        with picamera.PiCamera() as camera:
            camera.capture('newPicture.jpg')
        newPicture = misc.imread('newPicture.jpg')

        bigResult = abs(background-newPicture)
        result = misc.imresize(bigResult, 0.5)

        for i in range(0, 3):
            result[:,:,i][result[:,:,i]<50] = 0
            result[:,:,i][result[:,:,i]>200] = 0
        for i in range(0, 3):
	        if i == 0:
    	        result[:,:,i][result[:,:,1]==0] = 0
  	            result[:,:,i][result[:,:,2]==0] = 0
       		if i == 1:
            	result[:,:,i][result[:,:,0]==0] = 0
            	result[:,:,i][result[:,:,2]==0] = 0
        	if i == 2:
            	result[:,:,i][result[:,:,0]==0] = 0
            	result[:,:,i][result[:,:,1]==0] = 0

        result = ndimage.filters.minimum_filter(result,3)
        misc.imsave('result.jpg', result)
            
	index = np.count_nonzero(result)
	print index
	thyme.sleep(2)
	pushtobase(index)
	

			