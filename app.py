from flask import *
import logging
import os
import recycle
import utility
import youtube

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s / %(name)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

app = Flask('YoutubeDL')
app.config['TEMPLATES_AUTO_RELOAD'] = True


ext_opts = utility.get_ext_opts(youtube.SUPPORTED_EXT)
path = os.path.dirname(os.path.realpath(__file__))


@app.route('/')
def root():
    vid = request.args.get('vid')
    return render_template('index.html', ext_opts=ext_opts, vid=(vid if vid else ''))


@app.route('/script')
def script():
    return render_template('script.html')


@app.route('/vreq')
def vreq():
    vid = request.args.get('vid')
    ext = request.args.get('ext')
    if not vid or not ext or ext not in youtube.SUPPORTED_EXT:
        abort(400)

    vdata = youtube.validatevid(vid)
    if vdata['ok']:
        return render_template('vreq.html', vtitle=vdata['name'], vimg=vdata['imglnk'], vid=vid, ext=ext, EXT=ext.upper(), errhandle='')
    return render_template('vreq.html', errhandle=f'error_redirect("{vdata["err"]}")')


@app.route('/post', methods=['POST'])
def post():
    action = request.form.get('action')
    vid = request.form.get('vid')
    ext = request.form.get('ext')
    if not vid or not ext or ext not in youtube.SUPPORTED_EXT:
        abort(400)
    elif action == 'file':            # Check if the file requested already exists
        if os.path.isdir(f'{path}/output/file/{ext}/{vid}'):
            return ''
        return '1'
    elif action == 'convert':       # Check if the file requested is converting
        if os.path.isfile(f'{path}/output/converting/{ext}/{vid}'):
            return ''
        return '1'
    elif action == 'start':         # Request a convertion of the file
        if not os.path.isfile(f'{path}/output/converting/{ext}/{vid}'):
            open(f'{path}/output/converting/{ext}/{vid}', 'w').close()
            youtube.startDL(vid, ext)
            return ''
        return '1'
    elif action == 'complete':      # Check if a requested convertion has completed
        if os.path.isfile(f'{path}/output/converting/{ext}/{vid}'):
            return ''
        elif os.path.isdir(f'{path}/output/file/{ext}/{vid}'):
            return 'complete'
        return 'error'
    else:
        abort(400)


@app.route('/download/<ext>')
def download(ext):
    vid = request.args.get('vid')
    if not vid or not ext or ext not in youtube.SUPPORTED_EXT:
        abort(400)

    vidpath = f'{path}/output/file/{ext}/{vid}'
    recycle.DOWNLOAD_LCK.acquire()
    if (os.path.isdir(vidpath)):
        files = next(os.walk(vidpath))[2]
        if len(files):
            filename = [file for file in files if file.endswith(ext)][0]
            recycle.touch(ext, vid)
            recycle.DOWNLOAD_LCK.release()
            logging.info(f'Updated file lifetime - {vid}.{ext}')
            return send_file(vidpath + '/' + filename, as_attachment=True)
    recycle.DOWNLOAD_LCK.release()
    return redirect(url_for('vreq', vid=vid, ext=ext))


if __name__ == '__main__':
    utility.reset_output_directory(path, youtube.SUPPORTED_EXT)
    recycle.startGC()
    app.run(host='0.0.0.0', port=8888)
