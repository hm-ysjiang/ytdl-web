import os


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
