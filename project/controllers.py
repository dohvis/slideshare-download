from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from project import (
    BASE_DIR,
    db,
)
from project.models import (
    Slide,
)

downloader_bp = Blueprint('controller', __name__)


@downloader_bp.route('', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        from re import search
        url = request.form['url']
        if url[:4] != "http":
            url = "http://{}".format(url)
        if not search(r"((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)", url):
            return "올바르지 않은 url입니다."
        slide = db.session.query(Slide).filter_by(slideshare_url=url).first()
        if slide:
            return redirect('/slides/{}.pdf'.format(slide.title))
        from project.downloader.tasks import slide2img
        task = slide2img.delay(url)
        # task = slide2img(url)
        print(task, db)
        return redirect('/slides/')
    return render_template("index.html")


@downloader_bp.route('slides/')
def slides():
    return render_template("slides.html")


@downloader_bp.route('slides/<string:filename>')
def deliver_file(filename):
    import os
    return send_from_directory(os.path.join(BASE_DIR, 'media', filename.split(".")[0]), filename)
