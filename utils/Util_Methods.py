import re
import json
import urllib
from functools import wraps
import redis
from django.shortcuts import redirect, reverse
import requests


def request_data(request):
    """
    将请求的参数转换成字典
    :param request:
    :return:
    """
    parameters = dict(zip(request.GET.keys(), request.GET.values()))  # GET数据
    if not parameters:
        content_type = request.META.get("CONTENT_TYPE")
        if request.body:
            if re.search(r'json', content_type, re.I):
                parameters = json.loads(str(request.body, encoding='utf-8'))
            else:
                k = [urllib.parse.unquote_plus(x.split('=')[0]) for x in str(request.body, encoding="utf-8").split('&')]
                v = [urllib.parse.unquote_plus(x.split('=')[1]) for x in str(request.body, encoding="utf-8").split('&')]
                parameters = dict(zip(k, v))
            return parameters       # POST
    return parameters               # GET


def login_require(func):
    @wraps(func)
    def check(*args, **kwargs):
        req = args[0]
        session_id = req.COOKIES.get("_sessionid", None)
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        if not session_id or not r.hget(session_id, "login_time"):
            return redirect(reverse("login"))
        r.expire(session_id, 3600)
        return func(*args, **kwargs)
    return check


def carry_cookie(request):
    """
    带cookie访问带request
    :param request:
    :return:
    """
    coo = requests.cookies.RequestsCookieJar()
    # 第二步，设置cookies参数，coo.set('key', 'value')
    coo.set('_sessionid', request.COOKIES.get("_sessionid"))
    coo.set('username', request.COOKIES.get("username"))
    # 第三步，引入seeeion()，并update
    sess = requests.session()
    sess.cookies.update(coo)
    return sess


def call_api(url, parameters, timeout=10):
    """
    接口调用
    :param url:
    :param parameters:
    :param timeout:
    :return:
    """
    try:
        res = requests.post(url, json=parameters, timeout=timeout)
        if res.status_code == 200:
            res = json.loads(res.text)
            return res
    except Exception as e:
        return {"RTN_CODE": "00", "RTN_MSG": "中台接口调用出错, %s" % str(e)}
