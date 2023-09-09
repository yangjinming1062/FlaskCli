from sqlalchemy import true
from sqlalchemy.orm import Session

from . import *
from ..api import *

bp = get_blueprint(__name__, '系统管理')


@bp.route('/users', methods=['GET'])
@api_wrapper(
    request_param=PaginateRequestSchema({
        'sort': ParamDefine(List[str], False, '排序字段', default=['-updated_at']),
        'keyword': ParamDefine(str, False, '账号/用户名'),
    }),
    response_param={
        RespEnum.OK: PaginateResponseSchema(ParamDefine({
            'id': ParamDefine(str, True, '用户ID'),
            'account': ParamDefine(str, True, '账号'),
            'role': ParamDefine(RoleEnum, True, '角色'),
            'username': ParamDefine(str, True, '用户名'),
            'phone': ParamDefine(str, True, '手机号'),
            'email': ParamDefine(str, True, '邮箱'),
        }, True)),
    },
    permission={RoleEnum.Admin}
)
def get_users(**kwargs):
    """
    用户列表
    """
    sql = (
        select(
            User.id,
            User.account,
            User.role,
            User.username,
            User.phone,
            User.email,
        )
        .where(User.valid == true())
    )
    if keyword := kwargs.get('keyword'):
        sql = sql.where(User.account.like(f'%{keyword}%') | User.username.like(f'%{keyword}%'))
    return paginate_query(sql, kwargs, False)


@bp.route('/users', methods=['POST'])
@api_wrapper(
    request_param=ParamDefine({
        'account': ParamDefine(str, True, '账号', valid=User.valid_account, resp=RespEnum.InvalidAccount),
        'password': ParamDefine(str, True, '密码', valid=User.valid_password, resp=RespEnum.InvalidPassword),
        'username': ParamDefine(str, True, '用户名', valid=User.valid_username, resp=RespEnum.InvalidUsername),
        'phone': ParamDefine(str, True, '手机号', valid=User.valid_phone, resp=RespEnum.InvalidPhone),
        'email': ParamDefine(str, True, '邮箱', valid=User.valid_email, resp=RespEnum.InvalidEmail),
    }, True),
    response_param={
        RespEnum.Created: ParamDefine(str, True, '用户ID'),
    },
    response_header=TextPlainSchema(),
    permission={RoleEnum.Admin}
)
def post_user(**kwargs):
    """
    新建用户
    """
    kwargs['role'] = RoleEnum.User
    kwargs['password'] = User.generate_hash(kwargs['password'])
    return orm_create(User, kwargs)


@bp.route('/users/<uid>', methods=['PATCH'])
@api_wrapper(
    request_param=ParamDefine({
        'username': ParamDefine(str, False, '用户名', valid=User.valid_username, resp=RespEnum.InvalidUsername),
        'phone': ParamDefine(str, False, '手机号', valid=User.valid_phone, resp=RespEnum.InvalidPhone),
        'email': ParamDefine(str, False, '邮箱', valid=User.valid_email, resp=RespEnum.InvalidEmail),
    }),
    permission={RoleEnum.Admin}
)
def patch_user(uid, **kwargs):
    """
    编辑用户
    """
    return orm_update(User, uid, kwargs)


@bp.route('/users', methods=['DELETE'])
@api_wrapper(
    request_param=ParamDefine({
        'id': ParamDefine(List[str], True, '用户ID'),
    }),
    permission={RoleEnum.Admin}
)
def delete_user(**kwargs):
    """
    删除用户
    """
    session = kwargs['oltp_session']
    for uid in kwargs['id']:
        user = session.get(User, uid)
        if user.role != RoleEnum.Admin:
            user.valid = False
            user.credential.clear()
            session.flush()


@bp.route('/users/password', methods=['PUT'])
@api_wrapper(
    request_param=ParamDefine({
        'old': ParamDefine(str, True, '旧密码'),
        'new': ParamDefine(str, True, '新密码', valid=User.valid_password, resp=RespEnum.InvalidPassword),
    }),
)
def put_password(**kwargs):
    """
    修改密码
    """
    user = kwargs['user']
    if not user.check_password(kwargs['old']):
        raise APIException(RespEnum.WrongPassword)
    user.password = User.generate_hash(kwargs['new'])
    raise APIException(RespEnum.NoContent)


@bp.route('/users/<uid>/password', methods=['PUT'])
@api_wrapper(
    request_param=ParamDefine({
        'password': ParamDefine(str, True, '密码', valid=User.valid_password, resp=RespEnum.InvalidPassword),
    }),
    permission={RoleEnum.Admin}
)
def reset_password(uid, **kwargs):
    """
    重置密码【管理员】
    """
    session: Session = kwargs['oltp_session']
    user = session.get(User, uid)
    user.password = User.generate_hash(kwargs['password'])


@bp.route('/logs', methods=['GET'])
@api_wrapper(
    request_param=PaginateRequestSchema({
        'sort': ParamDefine(List[str], False, '排序字段', default=['-created_at']),
        'ip': ParamDefine(str, False, 'IP'),
        'account': ParamDefine(str, False, '账号'),
        'username': ParamDefine(str, False, '用户名'),
        'method': ParamDefine(List[str], False, '请求类型'),
        'status': ParamDefine(List[int], False, '状态码'),
        'created_at_start': ParamDefine(datetime, False),
        'created_at_end': ParamDefine(datetime, False),
    }),
    response_param={
        RespEnum.OK: PaginateResponseSchema(ParamDefine({
            'account': ParamDefine(str, True, '账号'),
            'username': ParamDefine(str, True, '用户名'),
            'created_at': ParamDefine(datetime, True, '发生时间'),
            'method': ParamDefine(MethodEnum, True, '请求类型'),
            'blueprint': ParamDefine(str, True, '业务模块'),
            'uri': ParamDefine(str, True, '接口路径'),
            'status': ParamDefine(int, True, '响应状态'),
            'duration': ParamDefine(int, True, '响应耗时'),
            'source_ip': ParamDefine(str, True, '源IP'),
        }, True)),
    },
    permission={RoleEnum.Admin}
)
def get_logs(**kwargs):
    """
    日志列表
    """

    def format_func(x):
        return {
            'account': user_dict.get(x[0]).account if x[0] in user_dict else '',
            'username': user_dict.get(x[0]).username if x[0] in user_dict else '',
            'created_at': x[1],
            'method': x[2],
            'blueprint': x[3],
            'uri': x[4],
            'status': x[5],
            'duration': x[6],
            'source_ip': x[7]
        }

    sql = select(
        ApiRequestLogs.user_id,
        ApiRequestLogs.created_at,
        ApiRequestLogs.method,
        ApiRequestLogs.blueprint,
        ApiRequestLogs.uri,
        ApiRequestLogs.status,
        ApiRequestLogs.duration,
        ApiRequestLogs.source_ip,
    )
    account = kwargs.get('account')
    username = kwargs.get('username')
    if account or username:
        stmt = select(User)
        if account:
            stmt = stmt.where(User.account.like(f'%{account}%'))
        if username:
            stmt = stmt.where(User.username.like(f'%{username}%'))
        user_dict = {u.id: u for u in execute_sql(stmt, many=True, scalar=True)}
        sql = sql.where(ApiRequestLogs.user_id.in_(user_dict.keys()))
    else:
        user_dict = {u.id: u for u in execute_sql(select(User), many=True, scalar=True)}
    if ip := kwargs.get('ip'):
        sql = sql.where(func.IPv4NumToString(ApiRequestLogs.source_ip).like(f'%{ip}'))
    sql = query_condition(sql, kwargs, ApiRequestLogs.method, op_type='in')
    sql = query_condition(sql, kwargs, ApiRequestLogs.status, op_type='in')
    sql = query_condition(sql, kwargs, ApiRequestLogs.created_at, op_type='datetime')
    return paginate_query(sql, kwargs, False, format_func, session=kwargs['olap_session'])
