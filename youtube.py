from concurrent.futures import ThreadPoolExecutor
import logging
import os
import queue
import recycle
import youtube_dl


# The maximum length of the requested video (in second)
DURATION_LIMIT = 600
# The supported extensions, make sure there is a corresponding YoutubeDL opt in get_opts if you add your own ones
SUPPORTED_EXT = ('mp3', 'mp4')
# The maximum amount of workers that the thread pool can hold
MAX_WORKERTHREADS = 10
# To enable the embed-thumbnail opt, make sure you have applied the patch mentioned in README
EMBED_THUMBNAIL = True


path = os.path.dirname(os.path.realpath(__file__))
_ytdl = youtube_dl.YoutubeDL({
    'noplaylist': True
})
threadexecuter = ThreadPoolExecutor(max_workers=MAX_WORKERTHREADS)


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
                },
                { 'key': 'FFmpegMetadata' }
            ]
        }
    elif ext == 'mp3':
        return {
            'writethumbnail': True,
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
                { 'key': 'EmbedThumbnail' },
                { 'key': 'FFmpegMetadata' }
            ]
        } if EMBED_THUMBNAIL else {
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
                { 'key': 'FFmpegMetadata' }
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
        recycle.touch(ext, vid)
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
            imglnk = info['thumbnails'][-1]['url']
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
