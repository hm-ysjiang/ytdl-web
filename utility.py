import os


def ensure_output_directory(path, exts):
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
