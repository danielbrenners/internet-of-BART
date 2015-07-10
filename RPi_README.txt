-- To change from direct connection to wifi --

$ sudo cp /boot/cmdline.wifi /boot/cmdline.txt
$ sudo cp /etc/network/interfaces.CalVisitor /etc/network/interfaces

-- To change from wifi to direct --

$ sudo cp /boot/cmdline.direct /boot/cmdline.txt
$ sudo cp /etc/network/interfaces.direct /etc/network/interfaces

-- To VNC ---

ssh into raspberry pi
vncserver :1 
On desktop, open VNC viewer and input Pi’s IP with “:1” appended (xxx.xxx.xxx.xxx:1)

-- To transfer files --

$ sftp pi@IPAddress
“>> put file.ext” to transfer files onto pi
“>> get file.ext” to transfer files from pi to local machine

-- OpenCV --

source ~/.profile
workon cv

-- Take picture --

$ python
>> import picamera
>> with picamera.PiCamera() as camera:
>>		camera.capture('foo.jpg')




