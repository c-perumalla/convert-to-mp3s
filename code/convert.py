'''
read from config 
save video
convert and save audio
remove 
log
'''
from datetime import date, datetime, timedelta
import os
from pytube import YouTube
import subprocess

import json

# contains the list of series to be converted in current batch run

# -------------------------------------
series_list = ['Living A Life That Matters', 'Finding the Real Jesus', 'Retreat 2017', 'Living with a Mission', 'Faith amidst Fear', 'Retreat 2019', 'Christ Centered Marriage', "Discovering Jesus - John's Gospel", "Me 2.0", "Expect the Unexpected - Advent Promises in Isaiah", "Vision", "Hope Rising", "5th Anniversary", "Warriors in Christ", "Loving Others", "Jesus Christ: The Beginnings"]

batchname = 'batch3'
# -------------------------------------

# import logging and initialize logging
import logging
logging.basicConfig(filename='logfile.log', filemode='w', level=logging.INFO, format='%(asctime)s %(message)s')

# to ease batch processing
basepath = ""  # TODO: set local path — root folder for mp3 output
batchpath = os.path.join(basepath, batchname)
if not(os.path.exists(batchpath)):
    os.mkdir(batchpath)
basepath = batchpath

video_save_path = ""  # TODO: set local path — scratch folder for downloaded videos
fail_list = set()

# date pattern ??

save_pattern = '{sermon_name}_{date}.mp3'

with open('./config.json') as fp:
    config = json.load(fp)

def get_info(series_name):
    return config[series_name]

def get_date_pattern(date):
    # get datetime object
    # see if you need to adjust date to closest previous sunday
    try:
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        sunday = dt - timedelta(days=dt.day)
        return datetime.strftime(sunday, '%b_%d_%Y')
    except:
        return date    

def get_sermon_name(vidname):
    # string split and get sermon name; different for different series
    return os.path.split(vidname)[1][:-4] # exclude 'mp4' and get just name of vidname

def _pull(vidlink, vidname, info, folder_name):
    '''
    vidlink = link to video or other identified
    return: path to saved video (str)
    '''
    vidname += '.mp4'
    # object creation using YouTube
    date = get_date_pattern(info['upload_date'])
    dummy = os.path.join(video_save_path, vidname)
    mp3name = save_pattern.format(sermon_name=get_sermon_name(dummy), date=date)
 
    if os.path.exists(os.path.join(folder_name, mp3name)):
        return 0

    try: 
        yt = YouTube(vidlink) 
        logging.info('Creating youtube object')
    
    except Exception as e:
        logging.error(e)
        fail_list.add(vidname)
        return

    try:
        yt.streams.filter(progressive = True, file_extension = "mp4").first().download(output_path=video_save_path, filename=vidname)
    except Exception as e:
        logging.error(e)
        fail_list.add(vidname)
        return
    logging.info('successfully pulled and saved: {}'.format(os.path.join(video_save_path, vidname)))
    return os.path.join(video_save_path, vidname)

def _convert(vidpath, info, folder_name, vid_name):
    """
    converts video at vidpath to mp3 using ffmpeg
    vidpath = str
    retursn: path to saved audio (str)
    """
    date = get_date_pattern(info['upload_date'])
    mp3name = save_pattern.format(sermon_name=vid_name, date=date)
    logging.info('-------------converting to mp3-------------')
    
    try: 
        subprocess.call(['ffmpeg', '-i', vidpath,  os.path.join(folder_name, mp3name)])
    except Exception as e:
        logging.error('could not convert {}'.format(vidpath))
        logging.error(e)
        fail_list.add(vidpath)
        return 
    
    logging.info('successfully converted: {} to mp3'.format(vidpath))
    return os.path.join(folder_name, mp3name)    

def _remove_vid(vidpath):
    """
    removes video at vidpath to optimize storage
    """ 
    logging.info('removing video: '.format(vidpath))
    os.remove(vidpath)

def convert_series(vid_info, folder_name):
    """
    pulls, converts, saves, removes all the videos in the series by calling helper functions
    vid_info: {vidname: {
        'upload_date': int,
        'link': str,
        'id': str
        }
    }
    returns: None
    """
    saved_mp3s = []
    total_num_videos = len(vid_info)
    cnt = 0
    for vid_name, info in vid_info.items():
        cnt += 1
        logging.info('processing video number {} of {} videos'.format(cnt, total_num_videos))
        logging.info('pulling video {}...'.format(vid_name))
        mp4_saved_path = _pull(info['link'], vid_name, info, folder_name)
        
        if mp4_saved_path is None:
            logging.info('video not saved abondoning video:{}'.format(vid_name))           
            continue

        if mp4_saved_path == 0:
            logging.info('video: {} already exists, abondoning'.format(vid_name))
            continue

        logging.info('converting to audio...')
        mp3_saved_name = _convert(mp4_saved_path, info, folder_name, vid_name)
        
        logging.info('removing saved video')
        _remove_vid(mp4_saved_path)
        saved_mp3s.append(mp3_saved_name)
    return saved_mp3s

def main():
    for series_name in series_list:
        # make a folder for series if you have to
        folder_name = os.path.join(basepath, series_name)
        if not(os.path.exists(folder_name)):
            os.mkdir(folder_name)

        # name of the video, link to the video, upload date, 
        vid_info  = get_info(series_name)

        # log stuff
        logging.info('converting series: {}'.format(series_name))

        # convert full series
        saved_mp3s = convert_series(vid_info, folder_name)
        for i in saved_mp3s:
            logging.info('saved mp3: {}'.format(i))

    logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> conversion complete :D <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

if __name__ == '__main__':
    start = datetime.now()
    logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> starting <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    main()
    stop = datetime.now()
    logging.info('total time in seconds: {}'.format((stop - start).total_seconds()))
