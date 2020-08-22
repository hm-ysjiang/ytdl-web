import datetime
import logging
import os
import threading
import time

# The time-to-live added to a file whenever it is requested, MAKE SURE this is big enough or the file might be recycled before the user completes his download
TTL = datetime.timedelta(minutes=15)
# The interval between two GC runs (in second)
GC_INTERVAL = 600
DOWNLOAD_LCK = threading.Lock()


# Before accessing the lifemap, you should always acquire the DOWNLOAD_LCK first
lifemap = {
    # key: "<ext>/<vid>"
    # val: a datetime.datetime obj representing the end of file's lifecycle
}
path = os.path.dirname(os.path.realpath(__file__))


# Remember to acquire the DOWNLOAD_LCK before calling this
def touch(ext, vid):
    global TTL
    lifemap[f'{ext}/{vid}'] = datetime.datetime.now() + TTL


def recycle():
    global path, lifemap, gc, DOWNLOAD_LCK, GC_INTERVAL

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
                    for root, dirs, files in os.walk(vidpath, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                except Exception as e:
                    logging.exception(e)
                logging.info(f'Removed file - {vid}.{ext}')

        DOWNLOAD_LCK.release()
        logging.info('Complete recycling')
        time.sleep(GC_INTERVAL)


gc = threading.Thread(target=recycle)


def startGC():
    gc.start()
