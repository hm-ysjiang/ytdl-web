import os
import queue
import threading
import youtube_dl

path = None

#
# Multi-thread download
#

def run():
    path = os.path.dirname(os.path.realpath(__file__))
    while True:
        try :
            if jobq.qsize():
                lck.acquire()
                vid, url = jobq.get()
                lck.release()
                ytdl = youtube_dl.YoutubeDL({
                    # 'writethumbnail': True,
                    'outtmpl': path + '/temp/file/' + vid + '/' + '%(title)s.%(ext)s',
                    'format': 'bestaudio/best',
                    'noplaylist': True,
                    'prefer_ffmpeg': True,
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '256',
                        },
                        # {
                        #     'key': 'EmbedThumbnail'
                        # }
                    ]
                })
                ytdl.download([url])
                print(f'Download complete - {vid}')
                os.remove(f'{path}/temp/converting/{vid}')
        except Exception as e:
            print(e)


lck = threading.Lock()
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
        print(e)
        return {
            'ok': False,
            'err': 'Video does not exist!'
        }


def startDL(vid):
    lck.acquire()
    jobq.put((vid, f'https://www.youtube.com/watch?v={vid}'))
    lck.release()
    print(f'Added to download queue - {vid}')
