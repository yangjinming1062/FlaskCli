from io import BytesIO

from flask import Blueprint, send_file

from utils.api import *

bp = Blueprint("function", __name__)


@bp.route('/download', methods=['GET'])
@api_wrapper(requires=set())
def download(**kwargs):
    """
    文件下载下载
    """
    file_cache = BytesIO()  # 将文件放到内存中，并不进行保留
    # TODO 文件内容
    file_cache.seek(0)
    rv = send_file(file_cache, attachment_filename=f'file.pdf', as_attachment=True)
    file_cache.close()
    rv.headers["Cache-Control"] = "no-cache"
    return rv
