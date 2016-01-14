from flask import Blueprint
account_bp = Blueprint('/accounts', __name__)

from . import controllers
