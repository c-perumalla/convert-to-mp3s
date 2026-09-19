'''
Rename all the files correctly
config.json has the correct dates

Run through each file
Get the correct date from config.json
Convert to human readable (get code from previous code)
make new name by getting sermon name and correct date + mp3
copy the file name to new location with new name 
'''
import os
import json
from datetime import datetime, timedelta
import shutil

new_location = ""  # TODO: set local path — destination for renamed files
series_dict_path = ""  # TODO: set local path — series_dict.json
config_path = ""  # TODO: set local path — config.json


# master
master_folder = os.path.join(new_location, 'master')
if not os.path.exists(master_folder):
    os.makedirs(master_folder)

with open(series_dict_path) as fh:
    series_dict = json.load(fh) # {full/path/toseries/: ['full/path/tovideo', ....]}

with open(config_path) as fh:
    config = json.load(fh) # {full/path/toseries/: ['full/path/tovideo', ....]}

def get_old_fname(fname_str):
    if 'mp4' in fname_str:
        name = fname_str.replace('.mp4_Jan_31_2022.mp3', '')
    else:
        name = fname_str.replace('_Jan_31_2022.mp3', '')
    return name

def get_correct_date(series_name, sermon_name):
    date = config.get(series_name, {}).get(sermon_name, {}).get("upload_date")
    dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    sunday = dt - timedelta(days=dt.day)
    return datetime.strftime(sunday, '%b_%d_%Y')

def get_new_name(sermon_name, date):
    return '{}_{}.mp3'.format(sermon_name, date)

def save_new(old_path, series_name, new_name):
    dest_folder = os.path.join(new_location, series_name)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    new_full_path = os.path.join(dest_folder, new_name)
    if not os.path.exists(new_full_path):
        shutil.copy(old_path, new_full_path)
        print('copy successfully! "old name: {} , new name: {}'.format(old_path, new_name))
    else:
        print('mp3 file already renamed')
    # copying to master folder

    new_master_full_path = os.path.join(master_folder, new_name)
    if not os.path.exists(new_master_full_path):
        shutil.copy(old_path, new_master_full_path)
        print('copy successfully to master! new name: {}'.format(new_master_full_path))
    else:
        print('master path exists')
def get_name(path):
    return os.path.basename(path)

def main():
    for series_path, video_paths in series_dict.items():
        print("------ working on series: {}".format(get_name(series_path)))
        for old_sermon_name in video_paths:
            print("------------ working on video: {}".format(old_sermon_name))
            old_filepath = os.path.join(series_path, old_sermon_name)
            series_name = get_name(series_path)
            sermon_name = get_old_fname(old_sermon_name) 
            correct_date_str = get_correct_date(series_name, sermon_name)
            new_name = get_new_name(sermon_name, correct_date_str)
            print("old name: {} , new name: {}".format(old_sermon_name, new_name))
            save_new(old_filepath, series_name, new_name)

if __name__ == '__main__':
    main()