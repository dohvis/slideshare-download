from flask import (
    request as req,
    render_template,
    redirect,
    send_from_directory,
)
from . import db
from .slides.models import Slide
from .accounts.models import User


def index():
    from .slides.models import Slide
    if req.method == 'GET':
        slides = db.session.query(Slide).all()
        u = len(list(db.session.query(User).all()))
        s = len(list(db.session.query(Slide).all()))

        return render_template('index.html', slides=slides, current_users=u, current_slides=s)
    else:
        url = req.form['url']
        from .slides.models import Slide
        s, created = Slide.get_or_create(url)
        if created:
            return redirect('/api/serve/%s' % s._hash)
        from .slides.core import slide2img
        """
        from . import db
        db.session.query(Slide).filter_by(url=url)
        """
        task = slide2img.delay(url)
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
                'title': task.info.get('title', ''),
                'author': task.info.get('author', ''),
                'description': task.info.get('description', ''),
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


def redirect_real_path(_hash):
    s = Slide.query.filter_by(_hash=_hash).first()
    if not s:
        return 404
    return redirect('/media/{}'.format(s.pdf_path))


def static_serving(filename):
    from . import STATIC_DIR
    return send_from_directory(STATIC_DIR, filename)


def media_serving(filename):
    from . import MEDIA_DIR
    return send_from_directory(MEDIA_DIR, filename)
