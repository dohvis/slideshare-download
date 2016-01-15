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
    path = join(MEDIA_DIR, title)
    with open('%s.pdf' % join(path, title), 'wb') as doc:
        doc.write(pdf_bytes)
    return True


@celery.task(bind=True)
def slide2img(self, url):
    import sys
    sys.setrecursionlimit(100000)
    from bs4 import BeautifulSoup
    from requests import get
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
    for i, image in enumerate(images):
        image_url = image['data-full'].split('?')[0]
        command = 'wget \'%s\' -O \'%s.jpg\' --quiet' % (image_url, join(saved_dir, str(i)))
        print("command : %s" % command)
        self.update_state(state='PROGRESS',
                          meta={'current': i,
                                'author': author,
                                'description': description,
                                'title': title,
                                'thumbnail': '/media/%s/0.jpg' % title,
                                'total': len(list(images)),
                                'status': command})
        system(command)

    convert_pdf(title)
    return {'current': 100,
            'total': 100,
            'title': title,
            'author': author,
            'description': description,
            'status': 'Task completed!',
            'thumbnail': '/media/%s/0.jpg' % title,
            'pdf_url': '/media/%s/%s.pdf' % (title, title)}
