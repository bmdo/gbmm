from flask import Blueprint, render_template
from config import config

bp = Blueprint('index', config.SERVER_NAME)


@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')
