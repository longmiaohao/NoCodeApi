import json
import urllib
from utils.RawSql import *
from functools import wraps
from django.http import JsonResponse
import time


def ParsePost(request):
    """
    解析POST参数 JSON form body里面有数据返回Dict 没有返回空Dict
    :param request:
    :return:
    """
    content_type = request.META.get("CONTENT_TYPE")
    if request.body:
        if re.search(r'json', content_type, re.I):
            return json.loads(str(request.body, encoding='utf-8'))
        else:
            k = [urllib.parse.unquote(x.split('=')[0]) for x in str(request.body, encoding="utf-8").split('&')]
            v = [urllib.parse.unquote(x.split('=')[1]) for x in str(request.body, encoding="utf-8").split('&')]
            return dict(zip(k, v))
    else:
        return {}


def db_log(check_type='', username='', operation='', req_path='', ip=''):
    """
    数据库日志记录
    :return:
    """
    from django.conf import settings
    try:
        log_table = settings.LOG_TABLE
    except:
        raise Exception("没有在settings里面设置LOG_TABLE指定日志表，字段：TYPE, USERNAME, OPERATION, IP，DATE")
    sql = "insert into " + log_table + "(TYPE, USERNAME, OPERATION, PATH, IP, DATE) values(%s, %s, %s, %s, %s, %s)"
    rawsql = RawSql()
    rawsql.execute(sql, [check_type, username, operation, req_path, ip, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())])


def params_check(params_list):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            request_data = ParsePost(request)
            for key_field in params_list:
                if key_field not in request_data.keys():
                    return JsonResponse({"RTN_MSG": "没有%s参数" % key_field, "RTN_CODE": "400"}, status=200,
                                        json_dumps_params={"ensure_ascii": False})
            return func(request, *args, **kwargs)
        return inner
    return decorator
