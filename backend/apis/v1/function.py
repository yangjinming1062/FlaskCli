"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : function.py
Author      : jinming.yang
Description : 实现各种操作类的API接口
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from io import BytesIO

from flask import send_file

from apis.api import *

bp = get_blueprint(__name__)


@bp.route('/download', methods=['GET'])
@api_wrapper(
    request_param=None,
    response_param={
        RespEnum.OK: ParamDefine(Any, '文件')
    },
)
def get_download(**kwargs):
    """
    文件下载下载
    """
    file_cache = BytesIO()  # 将文件放到内存中，并不进行保留
    # TODO 文件内容
    file_cache.seek(0)
    rv = send_file(file_cache, download_name=f'file.pdf', as_attachment=True)
    file_cache.close()
    rv.headers['Cache-Control'] = 'no-cache'
    return rv
