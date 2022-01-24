import json
from utils.RawSql import *
from functools import wraps
from django.shortcuts import redirect, reverse
from django.http import JsonResponse
import redis
import warnings
import time


def get_privileges(username):
    """
    获取用户权限
    :param username:
    :return:
    """
    view_qx = []
    api_qx = []
    rawsql = RawSql()
    if username == 'admin':
        sql = "select LINK_ID from MENU_LINKS"
        view_qx = rawsql.get_list(sql)  # 获取视图权限
        sql = "select LINK_ID from API_LINKS"
        api_qx = rawsql.get_list(sql)  # 获取api权限
    else:
        sql = "select MENU_ID from ROLE_MENU_PRIVILEGES where ROLE_ID in (select ROLE_ID from  USERS t1, USER_ROLE t2" \
              " where t1.USERNAME=t2.USERNAME and t1.username=%s) union select MENU_ID from USER_MENU_PRIVILEGES " \
              "where USERNAME=%s"
        view_qx = rawsql.get_list(sql, (username, username))  # 获取视图权限
        sql = "select API_ID from ROLE_API_PRIVILEGES where ROLE_ID in (select ROLE_ID from  USERS t1, USER_ROLE t2 " \
              "where t1.USERNAME=t2.USERNAME and t1.username=%s) union select API_ID from  USER_API_PRIVILEGES t2 " \
              "where USERNAME=%s"
        api_qx = rawsql.get_list(sql, (username, username))  # 获取api权限
    return view_qx, api_qx


def check_privilege(session_key, path_id=None, path_name=None, check_type='view', api_type='I'):
    """
     检查接口权限或者视图权限
    :param session_key:
    :param path_id:
    :param path_name:
    :param check_type:
    :param api_type:
    :return:
    """
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    privileges = r.hget(session_key, "privileges")
    r.close()
    if not path_id:
        if path_name:
            if check_type == "api":
                sql = "select LINK_ID from API_LINKS where LINK=%s"
            else:
                sql = "select LINK_ID from MENU_LINKS where LINK=%s"
            data = RawSql().get_list(sql, [path_name])
            if data:
                path_id = data[0]
            else:
                warnings.warn("路径：" + path_name + "不存在于菜单表或者接口表中")
                return False
        else:
            warnings.warn('没有路径代码或者路径名称')
            return False
    if not privileges:  # 没有任何权限
        return False
    if check_type == "view":
        view_privileges = json.loads(privileges)['view_privileges']
        if str(path_id) in view_privileges or int(path_id) in view_privileges:
            return True
        return False
    if check_type == "api":
        api_privileges = json.loads(privileges)['api_privileges']
        if str(path_id) in api_privileges or int(path_id) in api_privileges:
            return True
        return False


def check_api_privilege(remote_ip=None, path=None, token=None):
    """
     检查公共接口权限
    :param token:
    :param path:
    :param remote_ip:
    :return:
    """
    sql = "select * from PUBLIC_API_AUTHED where LINK=%s"
    rawsql = RawSql()
    data = rawsql.get_json(sql, [path])
    if data:
        if remote_ip == '127.0.0.1':
            return True, {"CODE": "01", "RTN_MSG": " 本地接口调用"}
        data = json.loads(data)[0]
        if data['TOKEN'] != token:
            return False, {"CODE": "00", "RTN_MSG": "token不正确"}
        if data['IP'] != remote_ip:
            return False, {"CODE": "00", "RTN_MSG": "IP未授权"}
        if data['INVAILD_TIME']:
            timeArray = time.strptime(data['INVAILD_TIME'], "%Y-%m-%d %H:%M:%S")
            valid_time = time.mktime(timeArray)
            if time.time() > valid_time:
                return False, {"CODE": "00", "RTN_MSG": "该授权已经过期，过期时间：%s" % data['INVAILD_TIME']}
        return True, {"CODE": "01", "RTN_MSG": "认证成功"}
    else:
        return False, {"CODE": "00", "RTN_MSG": "访问路径不存在, 请联系管理员进行公共接口配置"}


def login_require(func):
    @wraps(func)
    def check(*args, **kwargs):
        req = args[0]
        session_id = req.COOKIES.get("_sessionid", None)
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        try:
            if not session_id or not r.hget(session_id, "login_time"):
                r.close()
                return redirect(reverse("login"))
            r.expire(session_id, 3600)
            r.close()
            return func(*args, **kwargs)
        except Exception as e:
            return JsonResponse({"RTN_MSG": 'login_require err:' + str(e), "RTN_CODE": "500"}, status=200,
                                json_dumps_params={"ensure_ascii": False})
    return check
