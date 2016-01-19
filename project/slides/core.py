from os.path import (
    abspath,
    join,
)
from os import (
    system,
    makedirs,
    walk,
)
from .. import (
    celery,
    MEDIA_DIR,
)
from requests import get
from .. import db
from .models import Slide

def get_dir_files(title):
    files = []
    for (dirpath, dirnames, filenames) in walk(join(MEDIA_DIR, title)):
        # print(dirpath, filenames)
        for f in filenames:
            if f[-4:] == '.jpg':
                files.append(abspath(join(dirpath, f)))
        break
    return files


def convert_pdf(title):
    from img2pdf import convert
    from natsort import natsorted
    files = natsorted(get_dir_files(title))
    # To sort number in string. ex) [1.jpg, 10.jpg, 2.jpg ...] --> [1.jpg, 2.jpg, ... 10.jpg]
    print(files)
    pdf_bytes = convert(files, dpi=300, x=None, y=None)
    filepath = '{}.pdf'.format(join(title, title))

    with open(join(MEDIA_DIR, filepath), 'wb') as doc:
        doc.write(pdf_bytes)
    return filepath


@celery.task(bind=True)
def slide2img(self, url):
    import sys
    sys.setrecursionlimit(100000)
    from bs4 import BeautifulSoup
    html = get(url).content
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string
    title = title.replace(" ", "-")
    author = soup.find('span', {'itemprop': 'name'}).string
    images = soup.findAll('img', {'class': 'slide_image'})
    try:
        description = soup.find('p', {'id': 'slideshow-description-paragraph'}).string
    except AttributeError:
        description = ''
    saved_dir = join(MEDIA_DIR, title)
    makedirs(saved_dir, exist_ok=True)  # Only python >= 3.2
    total = len(list(images))
    for i, image in enumerate(images):
        image_url = image['data-full'].split('?')[0]
        result = get(image_url)
        filename = '{}.jpg'.format(join(saved_dir, str(i))) # full path of image
        with open(filename, "wb") as fp:
            fp.write(result.content)
        if i == 0:
            s = Slide.query.filter_by(slideshare_url=url).first()
            s.title = title
            s.description = description
            s.author = author
            s.thumbnail = '{}/0.jpg'.format(title)
            db.session.add(s)
            db.session.commit()

        self.update_state(state='PROGRESS',
                          meta={'current': i,
                                'author': author,
                                'description': description,
                                'title': title,
                                'thumbnail': '/media/{}'.format(s.thumbnail),
                                'total': total,
                                })
        print(i)
    s.pdf_path = convert_pdf(title)
    db.session.commit()
    Slide.get_hash_of_pdf(url)

    return {'current': total,
            'total': total,
            'title': title,
            'author': author,
            'description': description,
            'thumbnail': '/media/%s/0.jpg' % title,
            'pdf_url': '/media/%s/%s.pdf' % (title, title)}
