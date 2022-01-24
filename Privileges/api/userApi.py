from django.http import JsonResponse
from utils.AES import Aes
from ..Util_Methods import ParsePost, db_log, params_check
from . import user
from django.views.decorators.http import require_http_methods
from ..PrivilegesWrapper import *
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(['POST'])
@PrivilegesWrapper(check_type="api", api_type='I', path_name="/qtmj/create_user", log2db=True)
@params_check(['username', 'password', 'name'])
def create_user(request):
    """
    新增用户
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    if len(post_data['password']) < 6:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "密码长度不可少于6"})
    password = post_data['password']
    aes = Aes(32, settings.AES_KEY)
    post_data['password'] = aes.encrypt(password)
    post_data['create_user'] = call_user
    rawsql = RawSql()
    sql = "select username from USERS where USERNAME='%s'" % post_data['username']
    if rawsql.get_list(sql):
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "用户%s已存在" % post_data['username']}, status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    if user.create_user(post_data):
        db_log('user', call_user, '新增用户%s成功' % post_data['username'], request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "新增用户%s成功" % post_data['username']}, status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('user', call_user, '新增用户%s失败' % post_data['username'], request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "新增用户%s失败" % post_data['username']}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@PrivilegesWrapper(check_type="api", api_type='D', path_name="/qtmj/del_user", log2db=True)
@params_check(['username'])
def del_user(request):
    """
    删除用户
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    if user.del_user(post_data):
        db_log('user', call_user, '删除用户%s成功' % post_data['username'], request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "删除用户%s成功" % post_data['username']}, status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('user', call_user, '删除用户%s失败' % post_data['username'], request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "删除用户%s失败" % post_data['username']}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@PrivilegesWrapper(check_type="api", api_type='U', path_name="/qtmj/update_user", log2db=True)
@params_check(["condition", 'data'])
def update_user(request):
    """
    更新用户
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    if 'username' in post_data['data']:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "不可修改USERNAME"})
    if "password" in post_data['data'].keys() and len(post_data['data']['password']) < 6:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "密码长度不可少于6"})
    if "password" in post_data['data'].keys():
        password = post_data["data"]['password']
        aes = Aes(32, settings.AES_KEY)
        post_data["data"]['password'] = aes.encrypt(password)
    if user.update_user(post_data):
        db_log('user', call_user, '更新用户%s成功' % post_data["condition"]['username'], request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "更新用户%s成功" % post_data["condition"]['username']}, status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('user', call_user, '更新用户%s失败' % post_data["condition"]['username'], request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "更新用户%s失败" % post_data["condition"]['username']}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@PrivilegesWrapper(check_type="api", api_type='U', path_name="/qtmj/activeuser", log2db=True)
@params_check(["username"])
def active_user(request):
    """
     激活用户
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    if user.active_user(post_data['username']):
        db_log('user', call_user, '激活用户%s成功' % post_data['username'], request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "激活用户%s成功" % post_data['username']}, status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('user', call_user, '激活用户%s失败' % post_data['username'], request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "激活用户%s失败" % post_data['username']}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
@PrivilegesWrapper(check_type="api", api_type='U', path_name="/qtmj/deactivateuser", log2db=True)
@params_check(["username"])
def deactivate_user(request):
    """
     禁用用户
    :param request:
    :return:
    """
    call_user = request.COOKIES.get('username', None)
    post_data = ParsePost(request)
    if user.deactivate_user(post_data['username']):
        db_log('user', call_user, '禁用用户%s成功' % post_data['username'], request.META["PATH_INFO"],
               request.META["REMOTE_ADDR"])
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "禁用用户%s成功" % post_data['username']}, status=200,
                            safe=False,
                            json_dumps_params={"ensure_ascii": False})
    db_log('user', call_user, '禁用用户%s失败' % post_data['username'], request.META["PATH_INFO"],
           request.META["REMOTE_ADDR"])
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "禁用用户%s失败" % post_data['username']}, status=200, safe=False,
                        json_dumps_params={"ensure_ascii": False})


def error(request, info):
    """
    错误消息反馈
    :param request:
    :param info:
    :return:
    """
    return JsonResponse(info, json_dumps_params={"ensure_ascii": False})
