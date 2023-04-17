#############################################################################################################
# Script Name       : tesla_cam_file_script.py
# script version    : 1
# Author            : Ross McKinnon
# contact:          : srossmckinnon@gmail.com
# Date              : April 17, 2023
# Python Version    : python 3.9.0 windows
# Description       : helps manage total file size taken up by teslacam footage on synology nas
#############################################################################################################

from datetime import datetime
import os
import re

#returns the total size of the whole directory
def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def oldest_date_folder(folder_list):
    folder_list.sort()
    oldest_folder = folder_list[0]
    return oldest_folder

def delete_folder_tree(directory_to_delete):
    for dirpath, dirnames, filenames in os.walk(directory_to_delete):
        for f in filenames:
            print(directory_to_delete + "/" + f)
            deletefile = directory_to_delete + "/" + f

            #this shouldn't throw an error because we've already located the files
            #best to keep it running even if not maintained
            try:
                os.remove(deletefile)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

    #after removing the files delete the containing file
    #can also just use shutil module and use shutil.rmtree() on the containing folder but this way we can keep the folder for organization
    #or archiving
    os.rmdir(directory_to_delete)
    output = "deleted " + directory_to_delete + " and all files"
    return output

#script start

#we are measuring script run time for the log file
starttime = datetime.now()

#what is the parent directory for keeping recordings?
#size gets returned in bytes, convert to gigabytes
cam_footage_path = r""
total_size = get_size(cam_footage_path) / 1000000000

#get the list of directories with dates.
list_tesla_folders = os.listdir(cam_footage_path)
list_tesla_folders_as_strings = list(map(str, list_tesla_folders))
date_folders = list(filter(lambda x: re.match(r'^\d{4}-\d{2}-\d{2}$', x), list_tesla_folders_as_strings))

#if there are folders and the total size of the parent directory is greater than 300 gb then delete the oldest one
#this script is set to run once per day. I'd only like to delete the oldest file for now, that will give some natural buffer
#to this system. If there are a few big file days in a row, then then this system will spend a few days playing catch up
#to reduce the volume used, but it shouldn't be a problem over the long run.

#if this script gets developed, perhaps bring all file locations and file size parameters in to a config file that a user can edit.
if len(date_folders) != 0 and total_size > 300:
    rank = []
    #get a list of oldest to newest
    for folder in date_folders:
        year = int(folder[:4])
        month = int(folder[5:7])
        day = int(folder[8:])
        
        rank.append(datetime(year, month, day))

    oldest = oldest_date_folder(rank).strftime("%Y-%m-%d")
    oldest_path = cam_footage_path + oldest

    #get this size of the folder before it gets deleted
    size_deleted = get_size(oldest_path) / 1000000000

    #delete folder and all contents
    deleted_folder = delete_folder_tree(oldest_path)

else:
    #this only runs if no folders were deleted
    deleted_folder = "No folders deleted"
    size_deleted = "0"

#for log file name.
currentDateAndTime = datetime.now()
currentTime = currentDateAndTime.strftime("%H-%M-%S")
currentDay = currentDateAndTime.strftime("%d-%m-%Y")

#logfiles to be kept with script location
filepath = r"" + currentDay + ", " + currentTime + " log" + ".txt"   

#how long did this script take to run?
finishtime = datetime.now()
total_script_time = (finishtime - starttime).total_seconds()

#what's in the logfile?
file_line1 = "total file size: {} Gb".format(total_size)
file_line2 = "filesize deleted: {} Gb".format(size_deleted)
file_line3 = "total script runtime : {} s".format(total_script_time)
    
#output a log file
with open(filepath, 'w') as fp:
    fp.write("%s\n" % file_line1)
    fp.write("%s\n" % deleted_folder)
    fp.write("%s\n" % file_line2)
    fp.write("%s\n" % file_line3)
