#!/usr/bin/env python2

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug import secure_filename

import guano

import os.path


MAX_FILE_SIZE_MB = 16
UPLOAD_FOLDER = '/tmp'


app = Flask(__name__)
app.config.from_object(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def validate(f):
    """
    Validate a (presumably) GUANO file.
    Return a dict of the following format:

    {
      'guano': boolean,
      'valid: boolean,
      'guano_fields': {key:value, ...},
      'errors': {key:value, ...},
      'warnings': {key:value, ...},
    }
    """
    res = {'guano':False, 'valid':False, 'guano_fields':{}, 'errors':{}, 'warnings':{}}
    try:
        g = guano.GuanoFile(f)
    except Exception, e:
        res['errors'][1] = str(e)
        return res

    res['guano_fields'] = {k:v for k,v in g.items()}
    res['guano'] = True
    res['valid'] = True
    return res


@app.route('/', methods=['GET', 'POST'])
def show_form():
    error, guanofile  = None, None
    if request.method == 'POST':
        print request.files
        guanofile = request.files.get('guanofile', None)
        if not guanofile:
            error = 'Please browse to or drag-and-drop a GUANO file for validation.'
        # TODO: parse, validate, pass in validation struct
        fname = secure_filename(guanofile.filename)
        fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
        guanofile.save(fpath)
        result = validate(fpath)
        app.logger.debug(result)
        return render_template('results.html', valid=result['valid'], guano_fields=result['guano_fields'])
        # TODO: v2: parse, validate, persist validation struct, redirect(url_for('show_file'))
    return render_template('upload_form.html', error=error, guanofile=guanofile)


if __name__ == '__main__':
    app.run(debug=True)
