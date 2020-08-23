from bs4 import BeautifulSoup as Soup
from mutagen.easyid3 import EasyID3
import json
import logging
import os
import requests as req


INFO_KEY_TRANS = [
    {
        'artist': 'Artist',
        'album': 'Album'
    },
    {
        'artist': '演出者',
        'album': '專輯'
    }
]
path = os.path.dirname(os.path.realpath(__file__))


def reset_output_directory(path, exts):
    if os.path.isdir(path + '/output'):
        for root, dirs, files in os.walk(path + '/output', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    for ext in exts:
        if not os.path.isdir(path + '/output/file/' + ext):
            os.makedirs(path + '/output/file/' + ext)
        if not os.path.isdir(path + '/output/converting/' + ext):
            os.makedirs(path + '/output/converting/' + ext)


def get_ext_opts(exts):
    opts = ''
    for ext in exts:
        opts += f'<option value="{ext}">{ext.upper()}</option>'
    return opts


def get_raw_ytinfo(vid):
    r = req.get('https://www.youtube.com/watch?v=' + vid)
    if r.ok:
        r.encoding = 'utf-8'
        soup = Soup(r.text, 'html.parser')
        try:
            sc = [s.contents[0] for s in soup.find_all('script') if len(
                s.contents) > 0 and s.contents[0].find('window["ytInitialData"]') > 0][0]
            l, r = sc.find('window["ytInitialData"]'), sc.find(
                'window["ytInitialPlayerResponse"]')
            sc = sc[l + len('window["ytInitialData"]'):r]
            sc = sc[3:sc.rfind(';')]
            sc = json.loads(sc)
            contents = sc['contents']['twoColumnWatchNextResults']['results']['results']['contents']
            secondaryinforenderer = [c['videoSecondaryInfoRenderer']
                                     for c in contents if 'videoSecondaryInfoRenderer' in c.keys()][0]
            metarows = secondaryinforenderer['metadataRowContainer']['metadataRowContainerRenderer']['rows']
            metarows = [meta['metadataRowRenderer']
                        for meta in metarows if 'metadataRowRenderer' in meta and 'title' in meta['metadataRowRenderer']]

            keys = None
            for lang in INFO_KEY_TRANS:
                for meta in metarows:
                    if meta.get('title').get('simpleText') in lang.values():
                        keys = lang
                        break
                if keys:
                    break

            if keys:
                artist = None
                album = None
                for meta in metarows:
                    if meta.get('title').get('simpleText') == keys['artist']:
                        for cont in meta.get('contents'):
                            if 'runs' in cont:
                                for run in cont['runs']:
                                    if 'text' in run:
                                        artist = run['text']
                            if 'simpleText' in cont:
                                artist = cont['simpleText']
                    elif meta.get('title').get('simpleText') == keys['album']:
                        for cont in meta.get('contents'):
                            if 'runs' in cont:
                                for run in cont['runs']:
                                    if 'text' in run:
                                        album = run['text']
                            if 'simpleText' in cont:
                                album = cont['simpleText']
                if artist is not None or album is not None:
                    return {'artist': artist, 'album': album}
        except Exception:
            return


def try_writemeta(vid, ext):
    filepath = os.path.join(path, 'output/file', ext, vid)
    if os.path.isdir(filepath):
        files = [file for file in next(os.walk(filepath))[
            2] if file.endswith(ext)]
        if len(files) > 0:
            filename = files[0]
            if ext in ('mp3', ):
                logging.info(f'Trying to write metadata to {vid}.{ext}')
                info = get_raw_ytinfo(vid)
                if info is None:
                    logging.info('Metadata not found, skipping')
                    return
                meta = EasyID3(os.path.join(filepath, filename))
                if info['artist']:
                    meta['artist'] = info['artist']
                    meta['albumartist'] = info['artist']
                if info['album']:
                    meta['album'] = info['album']
                meta['title'] = filename[:-(len(ext)+1)]
                meta.save()
                logging.info(f'Metadata {info} written into {vid}.{ext}')
