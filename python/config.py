#!/usr/bin/env python

# CONFIGURATION

# Application Root
application_directory   = '/home/user/webcam/'

# Webcam Image Capture Resolution
webcam_device			= '/dev/video0'
webcam_image_width 		= '1280'
webcam_image_height 	= '720'
webcam_image_directory	= application_directory + 'photo/'

# Capture Start and End Time (must be within the same day)
# NOTE: 24 HOUR TIME!
capture_start_hour = '4'
capture_end_hour   = '23'

#capture_start_hour = '6' # updated for winter in the uk
#capture_end_hour   = '19'

# Timelapse Video Length
timelapse_video_length_in_seconds = 15 # Length in seconds
timelapse_video_directory		  = application_directory + 'timelapse/'

# Web/FTP Server Upload account
ftps_host 		= 'xxxxx'
ftps_username	= 'yyyyy'
ftps_password   = 'zzzzz'

ftp_directory	= 'timelapse/' # depends on where you want to store it within public_html


