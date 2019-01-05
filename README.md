# Daily Timelapse Generator
Who doesn't want to use an Old Webcam + Raspberry Pi Zero (or equivalent) to generate a timelapse of the world whilst you're stuck in an office.

This repository is split into two parts: 

1) Webserver (PHP) scripts that shows the latest timelapse in a HTML 5 video element
2) Timelapse device (Linux) with the Python code that captures photos during the day, and generates a timelapse at the end of it.

## Requirements

1) A webserver that supports PHP and which is accessible with a specific FTP account.
2) A Linux PC/single board computer/whatever with a webcam attached that is SUPPORTED by the operating system. 


3) The Linux instance will need the following installed: fswebcam, ffmpeg, run-one, python3, bash etc.

## Installation
1) Copy the stuff in the 'public_html' to a PHP enabled webserver, make sure the that contains this code is accessible by an FTP account
2) Copy the stuff in the 'python' folder to a folder on your Linux instance. Ensure this folder is writeable by the user account that owns the scripts. 
3) Adjust the configuration settings in config.py
4) Add something along the lines of the following to your crontab (preferably your local user based one, which can be adjusted by typing 'crontab -u <your_account> -e':

`# Every 2 minutes past the hour check to see that the webcam script is running
2 * * * * <your_account> run-one /home/<your_account>/timelapse-python-folder/capture_loop.py &> /dev/null
`
## Troubleshooting
You are most likely to have issues if the webcam isn't supported by Linux. Any decent Logitech or generic Chinese Webcam off eBay should be supported by Linux. Please check this before you buy. 

If you plug in a webcam to your Linux device's USB port you can double check by typing:
` lsusb
Bus 004 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Device 002: ID 046d:0809 Logitech, Inc. Webcam Pro 9000
`
You can see above appears to be detected, you can get the device address by typing:
`ls -ltrh /dev/video*``

If you have one webcam the device address will generally always be /dev/video0 
