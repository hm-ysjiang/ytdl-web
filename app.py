from flask import *
import youtube
import os

app = Flask('YoutubeDL')
app.config['TEMPLATES_AUTO_RELOAD'] = True

path = ''


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/vidreq', methods=['POST'])
def vid_request():
    vid = request.form['vid']
    return redirect('/vid='+vid)


@app.route('/vid=<vid>')
def vid(vid):
    vdata = youtube.validatevid(vid)
    print(vdata)
    if vdata['ok']:
        return render_template('vid.html', vtitle=vdata['name'], vimg=vdata['imglnk'], vid=vid, errhandle='')
    return render_template('vid.html', errhandle=f'error_redirect("{vdata["err"]}")')


@app.route('/checkfile/<vid>')
def check_file(vid):
    if (os.path.isdir(path + '/temp/file/' + vid)):
        return '1'
    return ''


@app.route('/checkconverting/<vid>')
def check_converting(vid):
    if (os.path.isfile(path + '/temp/converting/' + vid)):
        return '1'
    return ''


@app.route('/start/<vid>')
def start_convert(vid):
    if (os.path.isfile(path + '/temp/converting/' + vid)):
        return ''
    open(path + '/temp/converting/' + vid, 'w').close()
    youtube.startDL(vid)
    return '1'


@app.route('/dl/<vid>')
def download(vid):
    vidpath = path + '/temp/file/' + vid
    if (os.path.isdir(vidpath)):
        files = next(os.walk(vidpath))[2]
        if len(files):
            filename = files[0]
            return send_file(vidpath + '/' + filename, as_attachment=True)
    return abort(404)


if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir(path + '/temp/file/'):
        os.makedirs(path + '/temp/file/')
    if not os.path.isdir(path + '/temp/converting/'):
        os.makedirs(path + '/temp/converting/')
    app.run(host='0.0.0.0', port=8888)
