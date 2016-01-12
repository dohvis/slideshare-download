from flask import Flask, render_template, request as req
from celery import Celery
from os import path, walk, system, makedirs
from os.path import join, abspath


MEDIA = '/tmp/slideshare-vpn/'
tmpl_dir = path.join(path.dirname(path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


def create_app():
    app.config.from_pyfile('config.cfg')
    return app

app = create_app()
print(app.config['CELERY_BROKER_URL'])
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])


def get_dir_files(title):
    files = []
    for (dirpath, dirnames, filenames) in walk(join('/tmp/slideshare-vpn/', title)):
        print(dirpath, filenames)
        for f in filenames:
            print(f)
            files.append(abspath(join(dirpath, f)))
        break
    return files


def convert_pdf(title):
    from img2pdf import convert
    files = get_dir_files(title)
    files.sort()
    print(files)
    pdf_bytes = convert(files, dpi=300, x=None, y=None)
    with open('%s.pdf' % title, 'wb') as doc:
        doc.write(pdf_bytes)


@celery.task(bind=True)
def slide2img(self, url):
    from bs4 import BeautifulSoup
    from urllib import request

    html = request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string
    title = title.replace(" ", "-")
    print(title)
    images = soup.findAll('img', {'class': 'slide_image'})

    saved_dir = join(MEDIA, title)
    makedirs(saved_dir, exist_ok=True)  # Only python >= 3.2

    for i, image in enumerate(images):
        image_url = image['data-full'].split('?')[0]
        command = 'wget %s -O %s.jpg --quiet' % (image_url, join(saved_dir, str(i)))
        print("command : %s" % command)
        self.update_state(state='PROGRESS')
        system(command)

    convert_pdf(title)
    return title


@app.route("/", methods=['GET', 'POST'])
def index():
    if req.method == 'GET':
        return render_template('index.html')
    else:
        slide2img.apply_async((req.form['url'],))
    return "done!"


@app.route("/result", methods=['GET'])
def result():
    return render_template('result.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
