import os

from project.models import Slide
from project import (
    MEDIA_DIR,
    celery,
    create_app,
)

from project.downloader.utils import (
    convert_pdf,
    parse_slide,
    wget,
)
from flask_sqlalchemy import SQLAlchemy


@celery.task
def slide2img(url):
    import sys
    app = create_app()
    db = SQLAlchemy(app)
    sys.setrecursionlimit(100000)
    print('db session', db, type(db))
    info = parse_slide(url)

    s = Slide(url)
    s.title = info.title
    s.description = info.description
    s.author = info.author
    s.thumbnail = '{}/0.jpg'.format(info.title)

    saved_dir = os.path.join(MEDIA_DIR, info.title)
    os.makedirs(saved_dir, exist_ok=True)  # Only python >= 3.2

    images_cnt = len(list(info.images))

    for idx, image in enumerate(info.images):
        image_url = image['data-full'].split('?')[0]
        wget(image_url, saved_dir, filename='{}.jpg'.format(str(idx)))

        metadata = {
            'current': idx,
            'author': info.author,
            'description': info.description,
            'title': info.title,
            'thumbnail': '/media/{}'.format(s.thumbnail),
            'total': images_cnt,
        }
        print(idx)

    s.pdf_path = convert_pdf(info.title)
    db.session.add(s)
    db.session.commit()

    result = {
        'current': images_cnt,
        'total': images_cnt,
        'title': info.title,
        'author': info.author,
        'description': info.description,
        'thumbnail': '/media/%s/0.jpg' % info.title,
        'pdf_url': '/media/{0}/{0}.pdf'.format(info.title)
    }
    return result
