import config
import os
import re
import datetime
import tempfile
import subprocess
import shutil
from www import app
from flask import send_file, request, render_template


@app.route('/')
def front():
    return render_template('index.html')


@app.route('/en')
def front_en():
    return render_template('index.en.html')


@app.route('/render', methods=['POST'])
def render():
    options = {}
    variables = {}

    # bounding box
    if 'bbox' in request.form:
        bbox = request.form['bbox']
        if re.match('^[0-9.-]+(?:,[0-9.-]+){3}$', bbox):
            options['bbox'] = ' '.join(bbox.split(','))

    # image dimensions
    mode = request.form.get('dim', 'both')
    if mode == 'zoom' and 'zoom' in request.form:
        zoom = request.form['zoom']
        if re.match('^\d\d?$', zoom):
            options['zoom'] = zoom
    elif 'width' in request.form or 'height' in request.form:
        dim = '{} {}'.format(
            request.form.get('width', '0') if mode != 'height' else 0,
            request.form.get('height', '0') if mode != 'width' else 0)
        if not re.match('^\d{1,5} \d{1,5}$', dim):
            return 'Dimensions are  incorrect: ' + dim
        if request.form.get('units', '') == 'px':
            whkey = 'size-px'
        else:
            whkey = 'size'
            options['ppi'] = '300'
        options[whkey] = dim
        if 'margin' in request.form:
            margin = request.form['margin']
            if re.match('^\d\d?$', margin):
                options['margin'] = margin
        if mode == 'width' or mode == 'height':
            options['norotate'] = None

        # test for size limit
        size = dim.split(' ')
        mult = max(int(size[0]), int(size[1]))
        mult = mult * mult
        if 'ppi' in options:
            mult = mult * 16
        if mult > 2000*2000:
            return 'Dimensions are too big'

    # GPX trace (specific to veloroad style)
    traceFile = None
    if config.ROUTE and 'trace' in request.files and request.files['trace'].filename:
        traceFile = tempfile.NamedTemporaryFile('wb+', delete=False)
        request.files['trace'].save(traceFile)
        traceFile.close()

        variables['route'] = traceFile.name
        if 'fit' in request.form:
            del options['bbox']
            if 'norotate' in options:
                del options['norotate']
            options['fit'] = config.ROUTE
        if 'drawtrace' in request.form:
            options['add-layers'] = config.ROUTE

    # scale bar (specific to veloroad style)
    if config.SCALE and 'scale' in request.form:
        scalepos = request.form.get('scalepos', '')
        if re.match('^[0-9.-]+, *[0-9.-]+$', scalepos):
            options['add-layers'] = ','.join(
                [config.ROUTE, config.SCALE]) if 'add-layers' in options else config.SCALE
            variables['scale'] = scalepos
            scalens = re.match('^([1-9])-([1-5][05]?)$', request.form.get('scalens', '5-1'))
            variables['scalen'] = scalens.group(1) if scalens else 5
            variables['scales'] = scalens.group(2) if scalens else 1

    # map style, file format and mime type
    style = request.form.get('style', '')
    if style not in config.STYLES:
        style = next(iter(config.STYLES))
    fmt = request.form.get('format', '')
    if fmt not in config.FORMATS:
        fmt = next(iter(config.FORMATS))
    options['format'] = fmt
    mime = config.FORMATS[fmt]

    # build command line for nik4
    outfile, outputName = tempfile.mkstemp()
    command = ['/usr/bin/env', config.PYTHON, config.NIK4]
    for k, v in options.items():
        command.append('--{}'.format(k))
        if v is not None:
            command.extend(v.split(' '))
    command.append(config.STYLES[style])
    command.append(outputName)
    if config.PARAMETRIC:
        command.append('--vars')
        for k, v in variables.items():
            command.append('{}={}'.format(k, v))

    # check for running nik4
    ps = subprocess.Popen('ps -e|grep nik4.py', shell=True, stdout=subprocess.PIPE)
    psout, _ = ps.communicate()
    if 'nik4' in psout:
        if traceFile:
            os.remove(traceFile.name)
        return 'Nik4 is running, please try later.'

    # start nik4 process
    process = subprocess.Popen(command, stderr=subprocess.PIPE)
    _, err = process.communicate()
    code = process.returncode
    # Remove the temporary trace file
    if traceFile:
        os.remove(traceFile.name)
    if code == 0 and os.stat(outputName).st_size > 0:
        if fmt == 'svg':
            # run mapnik-group-text
            from mapnik_group_text import mapnik_group_text as mgt
            mgt_opt = {'dmax': 60, 'group': True}
            mgt.process_stream(open(outputName, 'rb'), outputName, mgt_opt)
            # run svn-resize if dimensions are known
            if 'size' in options or 'size-px' in options:
                from svg_resize import svg_resize as svgr
                svgr_opt = {}
                if 'size' in options:
                    d = options['size'].split(' ')
                    suffix = 'mm'
                else:
                    d = options['size-px'].split(' ')
                    suffix = 'px'
                if 'norotate' in options or not d[0] or not d[1]:
                    if d[0]:
                        svgr_opt['width'] = d[0] + suffix
                    if d[1]:
                        svgr_opt['height'] = d[1] + suffix
                else:
                    svgr_opt['longest'] = max(d[0], d[1]) + suffix
                    svgr_opt['shortest'] = min(d[0], d[1]) + suffix
                if 'margin' in options:
                    svgr_opt['margin'] = options['margin']
                svgr_opt['frame'] = True
                svgr_opt['input'] = outputName
                svgr.process_stream(svgr_opt)
        afn = '{}-{}.{}'.format(
            style, datetime.datetime.now().strftime('%y%m%d-%H%M'), fmt)
        fp = tempfile.TemporaryFile()
        with open(outputName, 'rb') as f:
            shutil.copyfileobj(f, fp)
        os.remove(outputName)
        fp.seek(0)
        return send_file(
            fp,
            mimetype=mime,
            add_etags=False,
            as_attachment=True,
            attachment_filename=afn)

    else:
        os.remove(outputName)
        if code > 0:
            msg = 'Error {} happened.'.format(code)
        else:
            msg = 'Resulting file is empty.'
        msg += '\nCommand line:\n{}\n\nOutput:\n'.format(' '.join(command))
        msg += err
        return app.response_class(msg, mimetype='text/plain')
