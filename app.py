import os
# import time
# import cPickle
import uuid
import datetime
import logging
import flask
import werkzeug
# import optparse
# import tornado.wsgi
# import tornado.httpserver
# import numpy as np
# import pandas as pd
from PIL import Image
import cStringIO as StringIO
import urllib
import exifutil
# matlab engine
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath('~/mondrian/src_matlab/')

UPLOAD_FOLDER = 'data'
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'bmp', 'jpg', 'jpe', 'jpeg', 'gif'])

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html', has_result=False)


@app.route('/classify_url', methods=['GET'])
def classify_url():
    imageurl = flask.request.args.get('imageurl', '')
    try:
        string_buffer = StringIO.StringIO(
            urllib.urlopen(imageurl).read())
        filename_base = uuid.uuid1().hex +'.jpg'
        filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
            werkzeug.secure_filename(filename_base)
        filename = os.path.join(UPLOAD_FOLDER, filename_)
        im = Image.open(string_buffer)
        im.save(filename)
    except Exception as err:
        # For any exception we encounter in reading the image, we will just
        # not continue.
        logging.info('URL Image open error: %s', err)
        return flask.render_template(
            'index.html', has_result=True,
            result=(False, 'Cannot open image from URL.')
        )

    logging.info('Image: %s', imageurl)
    pred = eng.exp_test(filename)
    result=(True, pred['label'],pred['score'])
    return flask.render_template(
        'index.html', has_result=True, result=result, imagesrc=imageurl)


@app.route('/classify_upload', methods=['POST'])
def classify_upload():
    try:
        # We will save the file to disk for possible data collection.
        imagefile = flask.request.files['imagefile']
        filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
            werkzeug.secure_filename(imagefile.filename)
        filename = os.path.join(UPLOAD_FOLDER, filename_)
        imagefile.save(filename)
        logging.info('Saving to %s.', filename)
        image = exifutil.open_oriented_im(filename)

    except Exception as err:
        logging.info('Uploaded image open error: %s', err)
        return flask.render_template(
            'index.html', has_result=True,
            result=(False, 'Cannot open uploaded image.')
        )
        # return flask.render_template('index.html')

    pred = eng.exp_test(filename)
    result=(True, pred['label'],pred['score'])
    return flask.render_template(
        'index.html', has_result=True, result=result,
        imagesrc=embed_image_html(image)
    # return redirct
    )


def embed_image_html(image):
    """Creates an image embedded in HTML base64 format."""
    image_pil = Image.fromarray((255 * image).astype('uint8'))
    image_pil = image_pil.resize((256, 256))
    string_buf = StringIO.StringIO()
    image_pil.save(string_buf, format='png')
    data = string_buf.getvalue().encode('base64').replace('\n', '')
    return 'data:image/png;base64,' + data


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS
    )

if __name__ == '__main__':
    app.run('0.0.0.0',port=80, threaded=True)
    # app.run(port = 5001, debug=True)