from flask import *
import logging
import os
import youtube

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s / %(name)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

app = Flask('YoutubeDL')
app.config['TEMPLATES_AUTO_RELOAD'] = True

path = ''


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/vreq')
def vreq():
    vid = request.args.get('vid')
    ext = request.args.get('ext')
    vdata = youtube.validatevid(vid)
    if vdata['ok']:
        return render_template('vreq.html', vtitle=vdata['name'], vimg=vdata['imglnk'], vid=vid, ext=ext, errhandle='')
    return render_template('vreq.html', errhandle=f'error_redirect("{vdata["err"]}")')


@app.route('/checkfile', methods=['POST'])
def check_file():
    vid = request.form.get('vid')
    ext = request.form.get('ext')
    if (os.path.isdir(f'{path}/output/file/{ext}/{vid}')):
        return '1'
    return ''


@app.route('/checkconverting', methods=['POST'])
def check_converting():
    vid = request.form.get('vid')
    ext = request.form.get('ext')
    if (os.path.isfile(f'{path}/output/converting/{ext}/{vid}')):
        return '1'
    return ''


@app.route('/start', methods=['POST'])
def start_convert():
    vid = request.form.get('vid')
    ext = request.form.get('ext')
    if (os.path.isfile(f'{path}/output/converting/{ext}/{vid}')):
        return ''
    open(f'{path}/output/converting/{ext}/{vid}', 'w').close()
    youtube.startDL(vid, ext)
    return '1'


@app.route('/download/<ext>')
def download(ext):
    vid = request.args.get('vid')
    vidpath = f'{path}/output/file/{ext}/{vid}'
    if (os.path.isdir(vidpath)):
        files = next(os.walk(vidpath))[2]
        if len(files):
            filename = files[0]
            return send_file(vidpath + '/' + filename, as_attachment=True)
    return abort(404)


if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir(path + '/output/file/mp3'):
        os.makedirs(path + '/output/file/mp3')
    if not os.path.isdir(path + '/output/file/mp4'):
        os.makedirs(path + '/output/file/mp4')
    if not os.path.isdir(path + '/output/converting/mp3'):
        os.makedirs(path + '/output/converting/mp3')
    if not os.path.isdir(path + '/output/converting/mp4'):
        os.makedirs(path + '/output/converting/mp4')
    app.run(host='0.0.0.0', port=8888)
