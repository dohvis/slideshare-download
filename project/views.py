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


def get_status():
    from flask import jsonify
    from .slides.core import slide2img
    from .utils import get_tasks
    res = []
    for uuid in get_tasks():
        task = slide2img.AsyncResult(uuid)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
            if 'result' in task.info:
                response['result'] = task.info['result']
        else:
            # something went wrong in the background job
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info),  # this is the exception raised
            }
        res.append(response)
    return jsonify(states=res)



def static_serving(filename):
    from . import STATIC_DIR
    return send_from_directory(STATIC_DIR, filename)


def media_serving(filename):
    from . import MEDIA_DIR
    return send_from_directory(MEDIA_DIR, filename)
