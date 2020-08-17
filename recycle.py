import datetime
import logging
import os
import threading
import time


def getnewlifetime():
    return datetime.datetime.now() + TTL


def recycle(interval):
    global path, lifemap, DOWNLOAD_LCK
    if not path:
        path = os.path.realpath(os.path.dirname(__file__))
 
    while True:
        DOWNLOAD_LCK.acquire()
        logging.info('Start recycling')
        kv = list(lifemap.items())
        now = datetime.datetime.now()
        for k, i in kv:
            if i < now:
                lifemap.pop(k)
                ext, vid = k.split('/')
                vidpath = f'{path}/output/file/{ext}/{vid}'
                try:
                    os.remove(f'{vidpath}/{next(os.walk(vidpath))[2][0]}')
                    os.rmdir(f'{vidpath}')
                except Exception as e:
                    logging.exception(e)
                logging.info(f'Removed file - {vid}.{ext}')

        DOWNLOAD_LCK.release()
        logging.info('Complete recycling')
        time.sleep(interval)


# Before accessing the lifemap, you should always acquire the DOWNLOAD_LCK first
lifemap = {
    # key: "<ext>/<vid>"
    # val: a datetime.datetime obj representing the end of file's lifecycle
}
path = None

# The time-to-live added to a file whenever it is requested, MAKE SURE this is big enough or the file might be recycled before the user completes his download
TTL = datetime.timedelta(minutes=15)

DOWNLOAD_LCK = threading.Lock()
# The argument in args is the recycle interval in seconds
GC = threading.Thread(target=recycle, args=(600, ))


def startGC():
    GC.start()
