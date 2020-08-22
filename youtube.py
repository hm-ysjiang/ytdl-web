from concurrent.futures import ThreadPoolExecutor
import logging
import os
import queue
import recycle
import youtube_dl


DURATION_LIMIT = 600
SUPPORTED_EXT = ('mp3', 'mp4')
MAX_WORKERTHREADS = 10


path = os.path.dirname(os.path.realpath(__file__))
_ytdl = youtube_dl.YoutubeDL({
    'noplaylist': True
})


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

#
# Multi-thread download
#


def download(jobinfo):
    global path
    vid, ext, url = jobinfo
    try:
        opts = get_opts(vid, ext)
        if not opts:
            return
        with youtube_dl.YoutubeDL(opts) as ytdl:
            ytdl.download([url])
        logging.info(f'Download complete - {vid}.{ext}')

        recycle.DOWNLOAD_LCK.acquire()
        recycle.lifemap[f'{ext}/{vid}'] = recycle.getnewlifetime()
    except Exception as e:
        logging.exception(e)

        recycle.DOWNLOAD_LCK.acquire()
        lifemap.pop(k)
        vidpath = f'{path}/output/file/{ext}/{vid}'
        try:
            os.remove(f'{vidpath}/{next(os.walk(vidpath))[2][0]}')
            os.rmdir(f'{vidpath}')
        except Exception as e2:
            logging.exception(e2)
    finally:
        os.remove(f'{path}/output/converting/{ext}/{vid}')
        recycle.DOWNLOAD_LCK.release()


threadexecuter = ThreadPoolExecutor(max_workers=MAX_WORKERTHREADS)

#
#
#


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
    threadexecuter.submit(
        download, (vid, ext, f'https://www.youtube.com/watch?v={vid}'))
