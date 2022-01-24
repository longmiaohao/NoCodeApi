from django.http import JsonResponse
from ..Util_Methods import ParsePost, db_log, params_check
from ..PrivilegesWrapper import *
from utils.RawSql import *
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['role_id', 'menu_id'])
@PrivilegesWrapper(check_type="api", api_type='I', path_name="/qtmj/grant_role_menu")
def grant_role_menu(request):
    """
    根据角色id和菜单id授权角色访问菜单权限
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    rawsql = RawSql()
    sql = "select NAME from MENU_LINKS where LINK_ID=%s union select NAME from ROLE where ROLE_ID=%s"
    data = rawsql.get_list(sql, (post_data['menu_id'], post_data['role_id']))
    if len(data) != 2:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "菜单或者角色不存在"})
    sql = "select * from ROLE_MENU_PRIVILEGES where ROLE_ID=%s and MENU_ID=%s"
    if rawsql.get_list(sql, (post_data['role_id'], post_data['menu_id'])):
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "改角色已经具有该菜单权限"})
    sql = "insert into ROLE_MENU_PRIVILEGES(ROLE_ID, MENU_ID, GRANT_USER) VALUES (%s, %s, '%s')"
    if rawsql.execute(sql, (post_data['role_id'], post_data['menu_id'], call_user)):
        db_log('privilege', call_user, '授权角色%s访问%s权限成功' % (data[1], data[0]), request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '授权角色%s访问%s权限成功' % (data[1], data[0])}, status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '授权角色%s访问%s权限失败' % (data[1], data[0]), request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '授权角色%s访问%s权限失败' % (data[1], data[0])}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['role_id', 'menu_id'])
@PrivilegesWrapper(check_type="api", api_type='D', path_name="/qtmj/revoke_role_menu")
def revoke_role_menu(request):
    """
    根据角色id和菜单id撤销角色访问菜单权限
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    rawsql = RawSql()
    sql = "select NAME from MENU_LINKS where LINK_ID=%s union select NAME from ROLE where ROLE_ID=%s" \
          % (post_data['menu_id'], post_data['role_id'])
    data = rawsql.get_list(sql)
    sql = "delete from ROLE_MENU_PRIVILEGES where MENU_ID=%s and ROLE_ID=%s" % (post_data['menu_id'],
                                                                                post_data['role_id'])
    if rawsql.execute(sql):
        db_log('privilege', call_user, '撤销角色%s访问%s权限成功' % (data[1], data[0]), request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '撤销角色%s访问%s权限成功' % (data[1], data[0])}, status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '撤销角色%s访问%s权限失败' % (data[1], data[0]), request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": ' 撤销角色%s访问%s权限失败' % (data[1], data[0])}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['role_id', 'api_id', 'menu_id', 'api_type'])
@PrivilegesWrapper(check_type="api", api_type='I', path_name="/qtmj/grant_role_api")
def grant_role_api(request):
    """
    根据角色id,菜单id，接口类型和接口id授权角色访问接口权限 接口有增删改查四类
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    rawsql = RawSql()
    sql = "select NAME from MENU_LINKS where LINK_ID=%s union all select NAME from ROLE where ROLE_ID=%s" \
          " union all select NAME from API_LINKS where LINK_ID=%s" \
          % (post_data['menu_id'], post_data['role_id'], post_data['api_id'])
    data = rawsql.get_list(sql)
    if len(data) != 3:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "菜单或者角色或者接口不存在"})
    sql = "select %s from API_LINKS where LINK_ID=%s" % (post_data['api_type'], post_data['api_id'])
    if rawsql.get_list(sql)[0] == 0:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该接口不支持%s操作" % post_data['api_type']})
    sql = "select * from ROLE_API_PRIVILEGES where ROLE_ID=%s and API_ID=%s and MENU_ID=%s and API_TYPE='%s'" % \
          (post_data['role_id'], post_data['api_id'], post_data['menu_id'], post_data['api_type'])
    if rawsql.get_list(sql):
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该角色已具有该接口权限"})
    sql = "insert into ROLE_API_PRIVILEGES(ROLE_ID, MENU_ID, API_ID, API_TYPE, GRANT_USER) VALUES (%s, %s, %s, '%s'," \
          " '%s')" % (post_data['role_id'], post_data["menu_id"], post_data['api_id'], post_data['api_type'], call_user)
    if rawsql.execute(sql):
        db_log('privilege', call_user, '授权角色%s有属于%s菜单下的%s接口的%s权限成功' %
               (data[1], data[0], data[2], post_data['api_type']), request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '授权角色%s有属于%s菜单下的%s接口的%s权限成功' %
                                                          (data[1], data[0], data[2], post_data['api_type'])},
                            status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '授权角色%s有属于%s菜单下的%s接口的%s权限失败' %
           (data[1], data[0], data[2], post_data['api_type']), request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '授权角色%s有属于%s菜单下的%s接口的%s权限失败' %
                                                      (data[1], data[0], data[2], post_data['api_type'])}, status=200,
                        safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['role_id', 'api_id', 'menu_id', 'api_type'])
@PrivilegesWrapper(check_type="api", api_type='D', path_name="/qtmj/revoke_role_api")
def revoke_role_api(request):
    """
    撤销角色所具有的接口权限
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    rawsql = RawSql()
    sql = "select NAME from MENU_LINKS where LINK_ID=%s union all select NAME from ROLE where ROLE_ID=%s" \
          " union all select NAME from API_LINKS where LINK_ID=%s" \
          % (post_data['menu_id'], post_data['role_id'], post_data['api_id'])
    data = rawsql.get_list(sql)
    if len(data) != 3:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "菜单或者角色或者接口不存在"})
    sql = "delete from ROLE_API_PRIVILEGES where ROLE_ID=%s and MENU_ID=%s and API_ID=%s and API_TYPE='%s'"\
          % (post_data['role_id'], post_data["menu_id"], post_data['api_id'], post_data['api_type'])
    if rawsql.execute(sql):
        db_log('privilege', call_user, '撤销角色%s有属于%s菜单下的%s接口的%s权限成功' %
               (data[1], data[0], data[2], post_data['api_type']), request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '撤销角色%s有属于%s菜单下的%s接口的%s权限成功' %
                                                          (data[1], data[0], data[2], post_data['api_type'])},
                            status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '撤销角色%s有属于%s菜单下的%s接口的%s权限失败' %
           (data[1], data[0], data[2], post_data['api_type']), request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '撤销角色%s有属于%s菜单下的%s接口的%s权限失败' %
                                                      (data[1], data[0], data[2], post_data['api_type'])}, status=200,
                        safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['username', 'menu_id'])
@PrivilegesWrapper(check_type="api", api_type='I', path_name="/qtmj/grant_user_menu")
def grant_user_menu(request):
    """
    授权用户的单独的菜单权限
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    rawsql = RawSql()
    sql = "select NAME from MENU_LINKS where LINK_ID=%s union select NAME from USERS where USERNAME=%s" %\
          (post_data['menu_id'], post_data['username'])
    data = rawsql.get_list(sql)
    if len(data) != 2:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "用户或者菜单不存在"})
    sql = "select username from USER_MENU_PRIVILEGES where USERNAME='%s' and MENU_ID=%s" % \
          (post_data['username'], post_data['menu_id'])
    if rawsql.get_list(sql):
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该用户已有该菜单权限"})
    sql = "insert into USER_MENU_PRIVILEGES(USERNAME, MENU_ID, GRANT_USER) VALUES (%s, %s, '%s')" \
          % (post_data['username'], post_data['menu_id'], call_user)
    if rawsql.execute(sql):
        db_log('privilege', call_user, '授权用户%s访问%s权限成功' % (post_data['username'], data[0]), request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '授权用户%s访问%s权限成功' % (post_data['username'], data[0])},
                            status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '授权用户%s访问%s权限失败' % (post_data['username'], data[0]), request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '授权用户%s访问%s权限失败' % (post_data['username'], data[0])},
                        status=200, safe=False, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['username', 'menu_id'])
@PrivilegesWrapper(check_type="api", api_type='D', path_name="/qtmj/revoke_user_menu")
def revoke_user_menu(request):
    """
    撤销用户的单独菜单权限
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    rawsql = RawSql()
    sql = "select NAME from USERS where USERNAME=%s union select NAME from MENU_LINKS where LINK_ID=%s"
    data = rawsql.get_list(sql, [post_data['username'], post_data['menu_id']])
    sql = "select username from USER_MENU_PRIVILEGES where USERNAME=%s and MENU_ID=%s"
    if len(rawsql.get_list(sql, [post_data['username'], post_data['menu_id']])) != 1:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该用户不具有该菜单权限"})
    sql = "delete from USER_MENU_PRIVILEGES where MENU_ID=%s and USERNAME=%s" % (post_data['menu_id'],
                                                                                 post_data['username'])
    if rawsql.execute(sql):
        db_log('privilege', call_user, '撤销用户%s访问%s权限成功' % (post_data['username'], data[0]), request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '撤销用户%s访问%s权限成功' % (post_data['username'], data[0])},
                            status=200, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '撤销用户%s访问%s权限失败' % (post_data['username'], data[0]), request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '授权用户%s访问%s权限失败' % (post_data['username'], data[0])}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['username', 'api_id', 'menu_id', 'api_type'])
@PrivilegesWrapper(check_type="api", api_type='I', path_name="/qtmj/grant_user_api")
def grant_user_api(request):
    """
    授权用户独立的api权限
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    rawsql = RawSql()
    sql = "select NAME from MENU_LINKS where LINK_ID=%s union select NAME from API_LINKS where LINK_ID=%s"
    data = rawsql.get_list(sql, (post_data['menu_id'], post_data['api_id']))
    sql = "select %s from API_LINKS where LINK_ID=%s and OWNING_MENU_ID=%s"
    info = rawsql.get_list(sql, (post_data['api_type'], post_data['api_id'], post_data['menu_id']))
    if len(info) == 0:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "菜单和接口归属关系不正确"})
    elif info[0] == 0:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该接口不支持%s操作" % post_data['api_type']})
    sql = "select * from USER_API_PRIVILEGES where USERNAME=%s and API_ID=%s and MENU_ID=%s and API_TYPE=%s"
    if rawsql.get_list(sql, (post_data['username'], post_data['api_id'], post_data['menu_id'], post_data['api_type'])):
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该用户已具有该接口权限"})
    sql = "insert into USER_API_PRIVILEGES(USERNAME, MENU_ID, API_ID, API_TYPE, GRANT_USER) VALUES (%s, %s, %s, %s, %s)"
    if rawsql.execute(sql, (post_data['username'], post_data["menu_id"], post_data['api_id'], post_data['api_type'],
                            call_user)):
        db_log('privilege', call_user, '授权用户%s有属于%s菜单下的%s接口的%s权限成功' %
               (post_data['username'], data[0], data[1], post_data['api_type']), request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '授权用户%s有属于%s菜单下的%s接口的%s权限成功' %
                                                          (post_data['username'], data[0], data[1], post_data['api_type'])},
                            status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '授权用户%s有属于%s菜单下的%s接口的%s权限失败' % (post_data['username'],
                                                                   data[0], data[1], post_data['api_type']),
           request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '授权用户%s有属于%s菜单下的%s接口的%s权限失败' %
                                                      (post_data['username'],
                                                       data[0], data[1], post_data['api_type'])}, status=200,
                        safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@params_check(['username', 'api_id', 'menu_id', 'api_type'])
@PrivilegesWrapper(check_type="api", api_type='D', path_name="/qtmj/revoke_user_api")
def revoke_user_api(request):
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    rawsql = RawSql()
    sql = "select NAME from MENU_LINKS where LINK_ID=%s union select NAME from API_LINKS where LINK_ID=%s"
    data = rawsql.get_list(sql, (post_data['menu_id'], post_data['api_id']))
    sql = "delete from USER_API_PRIVILEGES where USERNAME=%s and MENU_ID=%s and API_ID=%s and API_TYPE=%s"
    if rawsql.execute(sql, (post_data['username'], post_data["menu_id"], post_data['api_id'], post_data['api_type'])):
        db_log('privilege', call_user, '撤销用户%s有属于%s菜单下的%s接口的%s权限成功' %
               (post_data['username'], data[0], data[1], post_data['api_type']), request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '撤销用户%s有属于%s菜单下的%s接口的%s权限成功' %
                                                          (post_data['username'], data[0], data[1],
                                                           post_data['api_type'])},
                            status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('privilege', call_user, '撤销用户%s有属于%s菜单下的%s接口的%s权限失败' % (post_data['username'],
                                                                   data[0], data[1], post_data['api_type']),
           request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '撤销用户%s有属于%s菜单下的%s接口的%s权限失败' %
                                                      (post_data['username'],
                                                       data[0], data[1], post_data['api_type'])}, status=200,
                        safe=False,
                        json_dumps_params={"ensure_ascii": False})


def error(request, info):
    """
    错误消息反馈
    :param request:
    :param info:
    :return:
    """
    return JsonResponse(info, json_dumps_params={"ensure_ascii": False})
