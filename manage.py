import os
import sys
from project import create_app, manager

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
app = create_app()

if __name__ == '__main__':
    manager.run()
