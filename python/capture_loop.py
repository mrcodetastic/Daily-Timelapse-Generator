#!/usr/bin/env python

# Be a good citizen and don't pollute the namespace: http://stackoverflow.com/questions/17255737/importing-variables-from-another-file
import config; 

from database import * # Database Wrapping Class
from ftplib import FTP
import ftplib
import datetime
import time
import subprocess
import os, random, sys

# Start the running / heartbeat file
start_datetime  = datetime.datetime.now().strftime('%d %B %Y at %H:%M')
logfile         = config.application_directory + 'capture_loop.log'

# Try and open logfile
try:
    global applog
    applog = open(logfile, "w", 0) # 0 = unbuffered, instant write
    applog.write("Capture Loop Started: %s \n" % start_datetime)
except IOError:
    _count = 0

def appendlog(message):
    print message
    applog.write(message + '\n')

def deletelog():
    os.remove(logfile)
    
import atexit
atexit.register(deletelog)

    
# START: Timelapse Calculations
_start_second   = datetime.datetime.strptime(config.capture_start_hour,'%H')
_end_second     = datetime.datetime.strptime(config.capture_end_hour,'%H')
_timelapse_duration_in_sec = int((_end_second-_start_second).total_seconds())
_calc_timelapse_photos_required = config.timelapse_video_length_in_seconds*30 # 30fps
_calc_seconds_between_reallife_photos = int(_timelapse_duration_in_sec/(config.timelapse_video_length_in_seconds*30)) # Seconds between shots at XXfps
print ('Seconds between shots (or inverse fps): ' + str(_calc_seconds_between_reallife_photos))
# END: Timelapse Calculations

def create_timelapse_video():

    # Check to see if there are unprocessed, if so, for what CoB?
    result = query('SELECT CASE WHEN MAX(DATE(timestamp)) IS NULL THEN \'NO_PENDING\' ELSE MAX(DATE(timestamp)) END AS PENDING_DATE FROM timelapse_photo WHERE processed_flag = \'N\'')
    pending_date = result[0]["PENDING_DATE"]
    if pending_date == 'NO_PENDING':
        appendlog('There is no outstanding timelapse days to process. Happy Days!')
    else:
    
        # ffmpeg needs a start number
        result = query('SELECT MIN(photo_id) AS START_NUMBER FROM timelapse_photo WHERE DATE(timestamp) = \'' + pending_date + '\'')
        start_number = str(result[0]["START_NUMBER"])
        
        appendlog ('The date ' + pending_date + ' is pending processsing. Starting with photo id: ' + start_number)

        # Create the compiled video for site background i.e.: https://codepen.io/dudleystorey/pen/knqyK 
        # Constant rate factor of 28 - http://slhck.info/video/2017/02/24/crf-guide.html
        sql_current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    
        # http://stackoverflow.com/questions/11107206/how-to-restrict-ffmpeg-to-use-only-50-of-my-cpu
        output_video_filename = 'timelapse_' + pending_date + '.mp4'
        command = 'ffmpeg -threads 1 -start_number ' + start_number + ' -i ' + config.webcam_image_directory + 'photo_' + pending_date + '_' + '%06d.jpg -c:v libx264 -r 30 -crf 28 -y -pix_fmt yuv420p ' + config.timelapse_video_directory + output_video_filename
        execute('INSERT INTO `timelapse_log` (`timestamp`, `status`, `command`) VALUES (?, ?, ?)', (pending_date, 'Compiling x264 video: ' + output_video_filename, command))
        appendlog('Creating x264 video: ' + command)
        capture_output = subprocess.call(command.split(), shell=False)
           
        # Update all the photos for that date as processed
        query('UPDATE timelapse_photo SET processed_flag = \'Y\' WHERE DATE(timestamp) = \'' + pending_date + '\'')
        
        # Add to the database log of things that have happened
        execute('INSERT INTO `timelapse_log` (`timestamp`, `status`) VALUES (?, ?)', (sql_current_time, 'Completed video compilation for: ' + output_video_filename))
        
        # Add to the log of timelapse videos
        execute('INSERT INTO `timelapse_video` (`filename`, `timestamp`, `date` ) VALUES (?, ?, ?)', (output_video_filename, sql_current_time, pending_date))      
        appendlog ('Completed video compliation for ' + pending_date)
        
        # Upload video to server
        upload_timelapse_video(output_video_filename)

def upload_timelapse_video(filename):

    appendlog ('Begin FTP upload of '  + filename)
	
    # Upload video via normal FTP
    try:
        ftp = FTP(config.ftps_host, config.ftps_username, config.ftps_password)  
		
        # Begin FTP binary upload. Overwrite if the file is already there.
        file = open (config.timelapse_video_directory + filename, 'rb')
        ftp.storbinary('STOR ' + config.ftp_directory + filename, file)
        file.close

        # Write the latest name of the timelapse to a file
        target = open(config.application_directory + 'latest_timelapse_file.txt', 'w')
        target.write(filename) # write the most recent filename / video to the file
        target.close()
        
        # Sent it via FTP
        file = open (config.application_directory + 'latest_timelapse_file.txt', 'r')
        ftp.storlines('STOR ' + config.ftp_directory + 'latest_timelapse_file.txt', file)
        file.close

        # Write the latest timelapse date to a file
        last_updated = datetime.datetime.now().strftime('%A, %d %B %Y %Z')
        target = open(config.application_directory + 'last_updated.txt', 'w')
        target.write(last_updated) # write the most recent filename / video to the file
        target.close()
        
        # Sent it via FTP
        file = open (config.application_directory + 'last_updated.txt', 'r')
        ftp.storlines('STOR ' + config.ftp_directory + 'last_updated.txt', file)
        file.close

        # Log completion of the upload
        sql_current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')     
        message = ('Finished FTP upload of ' + config.timelapse_video_directory + filename + ' to ' + config.ftp_directory + filename )       
        appendlog(message)
        execute('INSERT INTO `timelapse_log` (`timestamp`, `status`) VALUES (?, ?)', (sql_current_time, message))
            
        ftp.quit()
        
    except (IOError, ftplib.error_proto, ftplib.error_perm) as e:
        #print "I/O error({0}): {1}".format(e.strerror)     
        print e.message
        appendlog ('Failed to upload ' + filename)
		
        # Log the failure to upload
        execute('INSERT INTO `timelapse_log` (`timestamp`, `status`) VALUES (?, ?)', (sql_current_time, 'Failed to upload ' + filename))
                    
 

def take_webcam_photo():

    current_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    sql_current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    
    appendlog('Taking a photo from the camera at ' + sql_current_time)  

    # Get the MAX value from the Photo ID sequence and +1.
    result = query ('SELECT MAX(seq)+1 AS next_photo_id from sqlite_sequence WHERE name = \'timelapse_photo\'')
    next_photo_id = result[0]["next_photo_id"]
    
    # Next filename
    next_filename = 'photo_' + current_date + '_' + '{0:06d}'.format(next_photo_id) + '.jpg'
    appendlog('Next filename is: ' + next_filename)

    next_filename_full_path = config.webcam_image_directory + next_filename
    command = 'fswebcam --device ' + config.webcam_device + ' --resolution ' + config.webcam_image_width + 'x' + config.webcam_image_height + ' --jpeg 80 --delay 5 --skip 25 --save ' + next_filename_full_path
    #capture_output = subprocess.call(command.split(), shell=False)
    capture_output = subprocess.call(command, shell=True)
    
    # Check to see if fswebcam actually created the file before we get to existed
    if (os.path.exists(next_filename_full_path)):
        # Record new image
        execute('INSERT INTO `timelapse_photo` (`filename`, `timestamp`, `processed_flag`) VALUES (?, ?, ?)', (next_filename, sql_current_time, 'N'))
        execute('INSERT INTO `timelapse_log` (`timestamp`, `status`, `command`) VALUES (?, ?, ?)', (sql_current_time, 'Captured Photo: ' + next_filename, command))
    else:
        # fswebcam failed to create the image. We need to immediately try again before we increment the sequence number
        appendlog('For some reason fswebcam failed to create an image that was intended to be ' + next_filename + '. Retrying')
        # Wait a few seconds
        time.sleep(10)
        take_webcam_photo() # Try again
        
    
# The main loop
while True:

    # http://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python
    # http://stackoverflow.com/questions/18884017/how-to-check-in-python-if-im-in-certain-range-of-times-of-the-day
    timestamp   = datetime.datetime.now().time() # Throw away the date information
    start       = datetime.time(int(config.capture_start_hour))
    end         = datetime.time(int(config.capture_end_hour))
    
    if (start <= timestamp <= end): # >>> depends on what time it is
        take_webcam_photo()
        print ('Sleeping for %s seconds..' % _calc_seconds_between_reallife_photos)
        time.sleep(_calc_seconds_between_reallife_photos)
    else:
        print 'Creating timelapse video, or sleeping for 10 minutes'
        create_timelapse_video();
        print 'Sleeping'
        time.sleep(60*10);
        
