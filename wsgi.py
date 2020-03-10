import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__)))
print(BASE_DIR)
sys.path.insert(0, BASE_DIR)
activate_this = '/home/nero/.virtualenvs/SSDownloader/bin/activate_this.py'

with open(activate_this) as f:
    code = compile(f.read(), activate_this, 'exec')
    exec(code)
from project import create_app
application = create_app()

