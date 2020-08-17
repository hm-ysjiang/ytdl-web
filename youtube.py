import logging
import os
import queue
import recycle
import threading
import youtube_dl

path = None

#
# Multi-thread download
#


def get_opts(vid, ext):
    if ext == 'mp4':
        return {
            'outtmpl': path + '/output/file/mp4/' + vid + '/' + '%(title)s.%(ext)s',
            'format': 'best',
            'noplaylist': True,
            'prefer_ffmpeg': True,
            'postprocessors': [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }
            ]
        }
    elif ext == 'mp3':
        return {
            'outtmpl': path + '/output/file/mp3/' + vid + '/' + '%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'noplaylist': True,
            'prefer_ffmpeg': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                },
                # {
                #     'key': 'FFmpegMetadata'
                # },
                # {
                #     'key': 'EmbedThumbnail',
                #     'already_have_thumbnail': True
                # } # Google seems to be sending a wrong labeled WEBM image, which cause ffmpeg failed to embed the thumbnail, see youtube-dl #25687
            ]
        }


def run():
    global path
    path = os.path.dirname(os.path.realpath(__file__))
    while True:
        sem.acquire()
        try:
            if jobq.qsize():
                lck.acquire()
                vid, ext, url = jobq.get()
                lck.release()
                opts = get_opts(vid, ext)
                if not opts:
                    continue
                with youtube_dl.YoutubeDL(opts) as ytdl:
                    ytdl.download([url])
                logging.info(f'Download complete - {vid}.{ext}')

                recycle.DOWNLOAD_LCK.acquire()
                recycle.lifemap[f'{ext}/{vid}'] = recycle.getnewlifetime()
                recycle.DOWNLOAD_LCK.release()

                os.remove(f'{path}/output/converting/{ext}/{vid}')
        except Exception as e:
            logging.exception(e)


lck = threading.Lock()
sem = threading.Semaphore(0)
jobq = queue.Queue()
dl_thread = threading.Thread(target=run)
dl_thread.start()

#
#
#


_ytdl = youtube_dl.YoutubeDL({
    'noplaylist': True
})
DURATION_LIMIT = 600
SUPPORTED_EXT = ('mp3', 'mp4')


def validatevid(vid):
    try:
        info = _ytdl.extract_info(
            f'http://www.youtube.com/watch?v={vid}',
            download=False
        )
        if info["duration"] > DURATION_LIMIT:
            return {
                'ok': False,
                'err': 'Video too long!'
            }
        try:
            imglnk = info['thumbnails'][-2]['url']
            return {
                'ok': True,
                'name': info['title'],
                'imglnk': imglnk
            }
        except:
            return {
                'ok': True,
                'name': info['title'],
                'imglnk': f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'
            }
    except Exception as e:
        logging.info(e)
        return {
            'ok': False,
            'err': 'Video does not exist!'
        }


def startDL(vid, ext):
    lck.acquire()
    jobq.put((vid, ext, f'https://www.youtube.com/watch?v={vid}'))
    sem.release()
    lck.release()
    logging.info(f'Added to download queue - {vid}.{ext}')
