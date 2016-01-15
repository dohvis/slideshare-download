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
                'task_id': uuid,
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'task_id': uuid,
                'state': task.state,
                'thumbnail': task.info.get('thumbnail', ''),
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
            if 'pdf_url' in task.info:
                response['pdf_url'] = task.info['pdf_url']
        else:
            # something went wrong in the background job
            response = {
                'task_id': uuid,
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
