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


class PrivilegesWrapper(object):
    """
    带登录认证的权限装饰器
    """

    def __init__(self, check_type="view", api_type=None, op_str=None, path_name=None, path_id=None, logger_file=None,
                 log2db=True, log2file=False, log_level='INFO', redirect_name='login'):
        self.__path_id = path_id
        self.__path_name = path_name
        self.__check_type = check_type
        self.__api_type = api_type
        self.__op_str = op_str
        self.__log_level = log_level
        self.__log2db = log2db
        self.__log2file = log2file
        self.__logger_file = logger_file
        self.__username = ""
        self.__redirect_name = redirect_name
        self.__ip = ""
        self.__req_path = ""
        self.__r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def __call__(self, func):

        @wraps(func)
        def run(*args, **kwargs):
            # redis里面读取用户名和权限 session
            request = args[0]  # 第一个参数为request
            session_id = request.COOKIES.get("_sessionid", None)
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            try:
                if not session_id:  # 用户未登录或者登录失
                    if self.__redirect_name:
                        return redirect(reverse(self.__redirect_name))
                elif not r.hget(session_id, "login_time"):
                    if self.__redirect_name:
                        return redirect(reverse(self.__redirect_name))
                    return views.error(request, {"RTN_MSG": "登录过期，请重新登录", "RTN_CODE": "403"})
            except:
                return views.error(request, {"RTN_MSG": "redis未启动", "RTN_CODE": "500"})
            username = self.__r.hget(session_id, 'username')
            self.__username = username
            self.__r.expire(session_id, 3600)
            self.__ip = request.META["REMOTE_ADDR"]
            self.__req_path = request.META["PATH_INFO"]
            api_type = self.__api_type
            if self.__check_type == 'api' and not self.__api_type:  # 没有传入接口类型的配置接口自动获取信息
                sql = 'select LINK_ID from API_LINKS where LINK=%s'
                data = RawSql().get_list(sql, [request.META['PATH_INFO']])
                if not data:
                    self.__path_id = -1
                    print(request.META['PATH_INFO'] + ' 不在接口表里')
                else:
                    self.__path_id = data[0]
                path_info = request.META['PATH_INFO']
                if path_info.split('/')[:-1] == 'delete':
                    api_type = 'D'
                elif path_info.split('/')[:-1] == 'update':
                    api_type = 'U'
                elif path_info.split('/')[:-1] == 'insert':
                    api_type = 'I'
                else:
                    api_type = 'S'
            # 权限检查
            self.__op_str = ""
            self.__op_str = '访问' if self.__check_type == 'view' else api_type
            if self.__op_str:  # 自定义日志内容
                self.__op_str = self.__op_str
            if not privilege.check_privilege(session_id, path_id=self.__path_id, path_name=(self.__path_name or
                                                                                            request.META["PATH_INFO"]),
                                             check_type=self.__check_type, api_type=api_type):
                if self.__log2file:
                    msg = "%s从%s非法%s访问路径:%s" % (username, request.META["REMOTE_ADDR"],
                                                request.method, request.META["PATH_INFO"])
                    if self.__check_type == "view":
                        filename = "illegal_view_access.log"
                    else:
                        filename = "illegal_api_access.log"
                        msg = "%s 非法调用 %s 执行 %s 操作" % (self.__username,
                                                       (self.__path_name or self.__path_id), self.__api_type)
                    create_log_fh(filename=filename, level="WARN").warning(msg)
                if self.__log2db:
                    self.__op_str = "非法访问"
                    self.db_log()
                return views.error(request, {"RTN_MSG": "无权限访问", "RTN_CODE": "403"})  # 没有权限跳转
            # 日志记录
            self.operation_log(request)
            return func(*args, **kwargs)
        return run

    def operation_log(self, req):
        """
        操作日志
        :param req:
        :return:
        """
        if self.__log2file and (self.__op_str or self.__check_type == 'api'):  # 写文件
            fh = create_log_fh(self.__logger_file, self.__log_level)
            self.file_log(fh)
        if self.__log2db:   # 写数据库
            self.db_log()

    def file_log(self, log_fh):
        """
        文件日志记录
        :return:
        """
        if self.__log_level == "INFO":
            if self.__op_str:
                log_fh.info(self.__op_str)
            else:
                if self.__check_type == "api":
                    log_fh.info("%s 调用 %s 执行 %s 操作" % (self.__username,
                                                       (self.__path_name or self.__path_id), self.__api_type))
        elif self.__log_level == "WARN":
            if self.__op_str:
                log_fh.warning(self.__op_str)
            else:
                if self.__check_type == "api":
                    log_fh.warning("%s 调用 %s 执行 %s 操作" % (self.__username,
                                                          (self.__path_name or self.__path_id), self.__api_type))
        elif self.__log_level == "DEBUG":
            if self.__op_str:
                log_fh.debug(self.__op_str)
            else:
                if self.__check_type == "api":
                    log_fh.debug("%s 调用 %s 执行 %s 操作" % (self.__username,
                                                        (self.__path_name or self.__path_id), self.__api_type))
        elif self.__log_level == "CRITICAL":
            if self.__op_str:
                log_fh.critical(self.__op_str)
            else:
                if self.__check_type == "api":
                    log_fh.critical("%s 调用 %s 执行 %s 操作" % (self.__username,
                                                           (self.__path_name or self.__path_id), self.__api_type))

    def db_log(self):
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
        if not rawsql.execute(sql, [self.__check_type, self.__username, self.__op_str, self.__req_path, self.__ip]):
            raise Exception(rawsql.err_msg)
