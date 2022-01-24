import logging
import os
import redis
from functools import wraps
from django.conf import settings
from Privileges.privilege import privilege
from Privileges import views
from utils.RawSql import *
from django.shortcuts import redirect, reverse


def create_log_fh(filename, level='INFO'):
    """
    自定义日志文件
    :param filename:
    :param level:
    :return:
    """
    if not filename:
        filename = "default.log"
    # 存在日志文件名称则进行日志记录 默认INFO级别
    logger = logging.getLogger(__name__)
    log_file = os.path.join(settings.BASE_DIR, "log")
    if not os.path.exists(log_file):
        os.makedirs(log_file)
    fh = logging.FileHandler(os.path.join(log_file, filename), encoding="utf-8")
    fh.setLevel(logging.INFO)  # 设置日志等级
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(level)
    return logger


def db_log(call_type='api', remote_ip=None, op_str=None, req_path=None):
    """
    数据库日志记录
    :return:+
    """
    try:
        log_table = settings.LOG_TABLE
    except:
        raise Exception("没有在settings里面设置LOG_TABLE指定日志表，字段：TYPE, USERNAME, OPERATION, IP，DATE")
    sql = "insert into " + log_table + " (TYPE, USERNAME, OPERATION, PATH, IP) values(%s, %s, %s, %s, %s)"
    rawsql = RawSql()
    if not rawsql.execute(sql, [call_type, remote_ip, op_str, req_path, remote_ip]):
        raise Exception(rawsql.err_msg)


class APIPrivilegesWrapper(object):
    """
    带登录认证的权限装饰器
    """

    def __init__(self, logger_file=None, log2db=True, log2file=False, log_level='INFO'):
        self.__log_level = log_level
        self.__log2db = log2db
        self.__log2file = log2file
        self.__logger_file = logger_file
        self.__ip = ""
        self.__req_path = ""

    def __call__(self, func):

        @wraps(func)
        def run(*args, **kwargs):
            request = args[0]  # 第一个参数为request
            self.__ip = request.META["REMOTE_ADDR"]
            self.__req_path = request.META["PATH_INFO"]
            token = request.META.get("HTTP_TOKEN", None)
            status, msg = privilege.check_api_privilege(self.__ip, path=request.META["PATH_INFO"], token=token)
            if not status:
                if not status and self.__log2file:
                    create_log_fh(filename=filename, level="WARN").warning("非法调用:" + msg['RTN_MSG'])
                if not status and self.__log2db:
                    db_log(remote_ip=self.__ip, op_str="非法调用:" + msg['RTN_MSG'], req_path=self.__req_path)
                return views.error(request, msg)  # 没有权限跳转
            # 日志记录
            db_log(remote_ip=self.__ip, op_str="调用成功", req_path=self.__req_path)
            return func(*args, **kwargs)
        return run
