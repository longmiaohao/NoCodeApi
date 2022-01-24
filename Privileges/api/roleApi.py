from django.http import JsonResponse
from ..Util_Methods import ParsePost, db_log, params_check
from ..PrivilegesWrapper import *
from ..api import role
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(['POST'])
@PrivilegesWrapper(check_type="api", api_type='I',  path_name="/qtmj/create_role")
def create_role(request):
    """
    角色创建接口
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    try:
        post_data = ParsePost(request)
    except Exception as e:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数解析失败: %s" % str(e)}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    sql = "select count(*) from ROLE where NAME='%s'" % post_data['role_name']
    rawsql = RawSql()
    if rawsql.get_list(sql)[0] == 1:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "角色%s已经存在" % post_data['role_name']}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    if 'role_name' not in post_data.keys():
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "角色名称不可为空"}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    if role.create_role(post_data['role_name'], call_user):
        db_log('privilege', call_user, '新增角色%s成功' % post_data['role_name'], request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "新增角色%s成功" % post_data['role_name']}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '新增角色%s失败' % post_data['role_name'], request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "新增角色%s失败" % post_data['role_name']}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['role_name'])
@PrivilegesWrapper(check_type="api", api_type='D', path_name="/qtmj/del_role")
def del_role(request):
    """
    角色删除及其撤销用户该角色的权限
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    try:
        post_data = ParsePost(request)
    except Exception as e:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数解析失败: %s" % str(e)}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    if 'role_name' not in post_data.keys():
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "角色名称不可为空"}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    if role.del_role(post_data['role_name']):
        db_log('privilege', call_user, '删除角色%s成功' % post_data['role_name'], request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "删除角色%s成功" % post_data['role_name']}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '删除角色%s失败' % post_data['role_name'], request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "删除角色%s失败" % post_data['role_name']}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['role_id', 'role_name'])
@PrivilegesWrapper(check_type="api", api_type='U', path_name="/qtmj/update_role")
def update_role(request):
    """
    角色更新
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    try:
        post_data = ParsePost(request)
    except Exception as e:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数解析失败: %s" % str(e)}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    if 'role_name' not in post_data.keys() or 'role_id' not in post_data.keys():
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "角色id或者名称不可为空"}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    if role.update_role(post_data['role_id'], post_data['role_name']):
        db_log('privilege', call_user, '更新角色为%s成功' % post_data['role_name'], request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "更新角色%s成功" % post_data['role_name']}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '更新角色%s失败' % post_data['role_name'], request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "更新角色%s失败" % post_data['role_name']}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['username'])
@PrivilegesWrapper(check_type="api", api_type='S', path_name="/qtmj/get_user_roles")
def get_user_roles(request):
    """
    获取某角色下的所有用户
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    try:
        post_data = ParsePost(request)
    except Exception as e:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数解析失败: %s" % str(e)}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "获取成功", "DATA": role.get_user_roles((post_data['username']
                                                                                           or call_user))}, status=200,
                        safe=False, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['role_name'])
@PrivilegesWrapper(check_type="api", api_type='S', path_name="/qtmj/get_role_users")
def get_role_users(request):
    """
    获取角色下的用户
    :param request:
    :return:
    """
    try:
        post_data = ParsePost(request)
    except Exception as e:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数解析失败: %s" % str(e)}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "获取成功", "DATA": role.get_roles_user((post_data['role_name']))}, status=200,
                        safe=False, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['username', 'role_id'])
@PrivilegesWrapper(check_type="api", api_type='I', path_name="/qtmj/grant_role_to_user")
def grant_role_to_user(request):
    """
    授权某用户某角色
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    try:
        post_data = ParsePost(request)
    except Exception as e:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数解析失败: %s" % str(e)}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    rawsql = RawSql()
    sql = "select NAME from ROLE where ROLE_ID=%s" % post_data['role_id']
    role_name = rawsql.get_list(sql)
    if role_name:
        role_name = role_name[0]
    else:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": 'ID为%s的角色不存在' % post_data['role_id']},
                            status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    sql = "select count(*) from USER_ROLE where ROLE_ID=%s and USERNAME='%s'" % (post_data['role_id'], post_data['username'])

    if rawsql.get_list(sql)[0]:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '%s已经为%s角色' % (post_data['username'], role_name)},
                            status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    if role.grant_role_to_user(username=post_data['username'], create_user=call_user, role_id=post_data['role_id']):
        db_log('privilege', call_user, '授权角色%s给%s成功' % (role_name, post_data['username']),
               request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '授权角色%s给%s成功' % (post_data['username'], role_name)},
                            status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '授权角色%s给%s失败' % (role_name, post_data['username']),
           request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '授权角色%s给%s失败' % (role_name, post_data['username'])},
                        status=200, safe=False, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['username', 'role_id'])
@PrivilegesWrapper(check_type="api", api_type='D', path_name="/qtmj/revoke_role_from_user")
def revoke_role_from_user(request):
    """
    撤销某用户某角色
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    try:
        post_data = ParsePost(request)
    except Exception as e:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数解析失败: %s" % str(e)}, status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    rawsql = RawSql()
    sql = "select NAME from ROLE where ROLE_ID=%s" % post_data['role_id']
    role_name = rawsql.get_list(sql)
    if role_name:
        role_name = role_name[0]
    else:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": 'ID为%s的角色不存在' % post_data['role_id']},
                            status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    sql = "select count(*) from USER_ROLE where USERNAME='%s' and ROLE_ID=%s" % (post_data['username'], post_data['role_id'])
    if not rawsql.get_list(sql)[0]:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '%s没有%s的角色' % (post_data['username'], role_name)},
                            status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    if role.revoke_role_from_user(username=post_data['username'], role_id=post_data['role_id']):
        db_log('privilege', call_user, '撤销%s的%s角色成功' % (post_data['username'], role_name),
               request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '撤销%s的%s角色成功' % (post_data['username'], role_name)},
                            status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '撤销%s的%s角色成功' % (post_data['username'], role_name),
           request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '撤销%s的%s角色成功' % (post_data['username'], role_name)},
                        status=200, safe=False, json_dumps_params={"ensure_ascii": False})


def error(request, info):
    """
    错误消息反馈
    :param request:
    :param info:
    :return:
    """
    return JsonResponse(info, json_dumps_params={"ensure_ascii": False})
