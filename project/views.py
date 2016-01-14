from flask import (
    request as req,
    render_template,
    redirect,
    send_from_directory,
)


def index():
    if req.method == 'GET':
        return render_template('index.html')
    else:
        from .slides.core import slide2img
        task = slide2img.delay(req.form['url'])
    return redirect('/state/')


def result():
    return render_template('state.html')


def static_serving(filename):
    from . import STATIC_DIR
    return send_from_directory(STATIC_DIR, filename)


def media_serving(filename):
    from . import MEDIA_DIR
    return send_from_directory(MEDIA_DIR, filename)
