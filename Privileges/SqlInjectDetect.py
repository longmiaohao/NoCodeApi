from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
from django.http import JsonResponse
import re
import time
import os
import logging
import redis
from urllib.parse import unquote
from django.conf import settings

# 自定义日志文件
logger = logging.getLogger(__name__)
fh = logging.FileHandler(os.path.join(settings.BASE_DIR, "log", 'SqlInjectionDetected.log'), encoding="utf-8")     # 当前工程下面 log文件夹的开交换机端口日志.log
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel('WARNING')


class SqlInjectDetect(MiddlewareMixin):
    """
    settings里面的OpRecorder的True 可以控制是否记录
    """
    __msg = ''
    
    def process_request(self, request):
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        if r.get('sqlinject_' + request.META['REMOTE_ADDR']):
            return JsonResponse({"RTN_CODE": "403", "RTN_MSG": "有SQL注入行为，禁止访问，请一小时后重试"}, status=200)
        sql_inject_check = True
        try:
            sql_inject_check = settings.SQL_INJECT_CHECK
        except:
            pass
        if not sql_inject_check:        # 不做SQL注入检查
            return
        check_data = ""
        try:
            if not request.FILES:
                if request.method == "POST":
                    check_data = request.body.decode('utf8')
                if request.method == "GET":
                    for var in request.GET:
                        check_data += '%s=%s&' % (var, request.GET.get(var))
        except:
            self.__msg = '{"RTN_CODE": "02", "DATA": [], "RTN_MSG": "未知异常参数数据解析失败!"})'
            logger.error("ip: " + request.META["REMOTE_ADDR"] + "    time:" +
                         time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "     params:" + check_data + '\n')
            return HttpResponse(status=400, content=self.__msg)
        check_data = unquote(check_data).replace('+', ' ')
        check_result = re.search(r'[\',\"]?\s *((or)|(union)|(and))+\s*[\',\"]?\w+[\',\"]?\s*=\s*[\',\"]?\w+\s*(--)?', check_data, re.I)
        if check_result:
            data = "ip:" + request.META["REMOTE_ADDR"] + "  time:" \
                   + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) \
                   + "  params:" + check_data + "  inject:" + check_result.group(0)
            logger.warning(data)
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            if r.get('sqlinject_' + request.META['REMOTE_ADDR']):
                r.expire('sqlinject_' + request.META['REMOTE_ADDR'], 60)
            else:
                r.set('sqlinject_' + request.META['REMOTE_ADDR'], '1')
                r.expire('sqlinject_' + request.META['REMOTE_ADDR'], 60)
            self.__msg = '{"RTN_CODE": "03", "DATA": [], "RTN_MSG": "发现sql注入, 已记录"})'
            return HttpResponse(status=400, content=self.__msg)
        check_result = re.search(r'[\',\"]?\s*[\',\"]?((delete)|(union)|(update)|(drop)|(truncate)|(create)|(select))+\s*\*?\s+[\',\"]?', check_data, re.I)
        if check_result:
            data = "ip:" + request.META["REMOTE_ADDR"] + "  time:"\
                   + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())\
                   + "  params:" + check_data + "  inject:" + check_result.group(0)
            logger.warning(data)
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            if r.get('sqlinject_' + request.META['REMOTE_ADDR']):
                r.expire('sqlinject_' + request.META['REMOTE_ADDR'], 60)
            else:
                r.set('sqlinject_' + request.META['REMOTE_ADDR'], '1')
                r.expire('sqlinject_' + request.META['REMOTE_ADDR'], 60)
            self.__msg = '{"RTN_CODE": "03", "DATA": [], "RTN_MSG": "发现sql注入, 已记录"})'
            return HttpResponse(status=400, content=self.__msg)
