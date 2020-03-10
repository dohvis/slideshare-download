from collections import namedtuple
from os.path import (
    abspath,
    join as os_join,
)
from os import walk

from bs4 import BeautifulSoup
from img2pdf import convert
from natsort import natsorted
from requests import get

from project import (
    MEDIA_DIR,
)


def convert_pdf(title):
    def _get_dir_files(title):
        files = []
        for (dirpath, dirnames, filenames) in walk(os_join(MEDIA_DIR, title)):
            # print(dirpath, filenames)
            for f in filenames:
                if f[-4:] == '.jpg':
                    files.append(abspath(os_join(dirpath, f)))
            break
        return files

    files = natsorted(_get_dir_files(title))
    # To sort number in string. ex) [1.jpg, 10.jpg, 2.jpg ...] --> [1.jpg, 2.jpg, ... 10.jpg]
    print(files)
    pdf_bytes = convert(files, dpi=300, x=None, y=None)
    filepath = '{}.pdf'.format(os_join(title, title))

    with open(os_join(MEDIA_DIR, filepath), 'wb') as doc:
        doc.write(pdf_bytes)
    return filepath


def wget(url, saved_dir, filename=None):
    resp = get(url)
    filename = filename or url.split('/')[-1]

    with open(os_join(saved_dir, filename), "wb") as fp:
        fp.write(resp.content)
    return True


def parse_slide(url):
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
    named_tuple = namedtuple('info', ['title', 'author', 'images', 'description'])
    info = named_tuple(title, author, images, description)
    return info


def get_hash_of_file(_file, blocksize=1024):
    from hashlib import md5
    with open(_file, 'rb') as fp:
        buf = fp.read(blocksize)
        res = md5(buf)
        while len(buf) > 0:
            res.update(buf)
            buf = fp.read(blocksize)
    return res.hexdigest()
