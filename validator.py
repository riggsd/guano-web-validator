#!/usr/bin/env python2

import os.path
from collections import OrderedDict

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug import secure_filename

import guano

__version__ = '0.0.1'


MAX_FILE_SIZE_MB = 24
UPLOAD_FOLDER = '/tmp'


app = Flask(__name__)
app.config.from_object(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.context_processor
def inject_versions():
    """Make global app config info available to templates"""
    return {'guano_version': guano.__version__, 'validator_version': __version__}


def validate(f):
    """
    Validate a (presumably) GUANO file.
    Return a dict of the following format:

    {
      'guano': boolean,
      'valid': boolean,
      'filename': string,
      'guano_fields': {key:value, ...},
      'errors': {key:value, ...},
      'warnings': {key:value, ...},
    }
    """
    res = {'guano':False, 'valid':False, 'filename':os.path.basename(f), 'guano_fields':{}, 'errors':{}, 'warnings':{}}
    try:
        g = guano.GuanoFile(f)
    except Exception, e:
        res['errors'][1] = str(e)
        return res

    res['guano_fields'] = OrderedDict(g.items())
    if 'GUANO|Version' in g:
        res['guano'] = True

    if g.get('GUANO|Version', 0.0) >= 1.0:
        res['valid'] = True

    # TODO: perform some lower-level validation of metadata

    return res


@app.route('/', methods=['GET', 'POST'])
def show_form():
    error, guanofile  = None, None
    if request.method == 'POST':
        print request.files
        guanofile = request.files.get('guanofile', None)
        if not guanofile or not guanofile.filename:
            error = 'Please browse to or drag-and-drop a GUANO file for validation.'
            return render_template('upload_form.html', error=error)
        fname = secure_filename(guanofile.filename)
        fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
        guanofile.save(fpath)
        result = validate(fpath)
        app.logger.debug(result)
        return render_template('results.html', valid=result['valid'], guano_fields=result['guano_fields'], filename=result['filename'])

    return render_template('upload_form.html', error=error, guanofile=guanofile)


if __name__ == '__main__':
    app.run(debug=True)
