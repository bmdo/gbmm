from flask import Blueprint
from config import config
from server.database import Download

bp = Blueprint('definitions', config.SERVER_NAME, url_prefix='/api/definitions')


@bp.route('/get', methods=('GET',))
def get():
    return {
        'download_statuses': {e.name: e.value for e in Download.DownloadStatus}
    }
