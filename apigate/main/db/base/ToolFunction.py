import requests
import json
import urllib
import re
import os
from configparser import ConfigParser
from django.conf import settings
from utils.DB import *
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
# # 传入读取文件的地址，encoding文件编码格式，中文必须
config.read(os.path.join(settings.BASE_DIR, "apigate", 'conf', 'api_conf.ini'), encoding='UTF-8')
SECRET_KEY = config["SECRET_KEY"]["key"]
db_path = config["DB_PATH"]["path"]


def quote_generate(quote_num):
    """
    生成预处理字符串 %%s,%%s,%%s
    :param quote_num:
    :return:
    """
    return ','.join(['%s' for i in range(quote_num)])


def filed_generate(fields, alias_fields, op_type='I'):
    """
    生成字段
    :param op_type:
    :param alias_fields:
    :param fields:
    :return:
    """
    if op_type == 'I':
        return ','.join([alias_fields[field.upper()] if field.upper() in alias_fields.keys() else field.upper() for field in fields])
    elif op_type == 'U':
        return ','.join(['%s=%%s' % field.upper() for field in fields])


def condition_generate(parameters=None, condition=None, alias_field=None):
    """
    条件生成器 WHERE FILED1=? AND FILED2=?, [VALUES1,...]
    :return:
    """
    if alias_field is None:
        alias_field = {}
    if condition is None:
        condition = {}
    if parameters is None:
        parameters = {}
    if not alias_field:
        alias_field = {}
    condition_dict = {"GT": " %s > %%s ", "GT-NUMBER": " %s > %%s ", "LT": " %s < %%s ", "LT-NUMBER": " %s < %%s ",
                      "LE": "%s <= %%s ", "LE-NUMBER": "%s <= %%s ", "GE": " %s >= %%s ", "GE-NUMBER": " %s >= %%s ",
                      "EQ-NUMBER": " %s = %%s ", "EQ-CHAR": " %s = %%s ", "BETWEEN": " %s > %%s and %s < %%s ",
                      "EQ": " %s = %%s ", "LIKE": " (%s like CONCAT('%%', %%s) or %s like CONCAT(%%s, '%%')) ",
                      "NE": " %s != %%s ", "NE-NUMBER": " %s != %%s ",
                      "NOT LIKE": " (%s not like '%%%%s' and %s not like CONCAT(%%s, '%%'))", "IN": "%s in (%s) ",
                      "NOT IN": " %s not in (%s) "}  # 条件转义字典 默认比较是数字 等于是字符
    condition_list = []
    values = []
    for k in parameters.keys():  # 遍历入参数
        data_type = ""  # 数据类型
        if parameters[k]:  # 没有值则不进行条件拼接
            if k.upper() in condition.keys():
                if "TYPE" in condition[k.upper()].keys():       # 获取是否匹配了类型 支持正则定义
                    data_type = '-' + condition[k.upper()]["type"]
            else:
                if "TYPE" in condition[alias_field[k.upper()]].keys():       # 获取是否匹配了类型 支持正则定义
                    data_type = '-' + condition[k.upper()]["type"]
            if k.upper() in alias_field.keys():     # 别名字段里面
                value = parameters[k]
                k = alias_field[k.upper()]
                condition_key = condition[k]["OP" + data_type]
            else:
                value = parameters[k]
                k = k.upper()
                condition_key = condition[k]["OP" + data_type]
            if condition[k]["OP" + data_type] == "BETWEEN":
                condition_list.append(condition_dict[condition_key] % (k, k))
                values.extend(value.split(','))
            elif condition_key == "LIKE" or condition_key == "NOT LIKE":
                condition_list.append(condition_dict[condition_key] % (k, k))
                values.extend([value, value])
            elif condition_key == "IN" or condition_key == "NOT IN":
                value = parameters[k].split(',')
                condition_list.append(
                    condition_dict[condition_key] % (k, quote_generate(len(value))))   # 生成 FIELD in (?,...)
                values.extend(value)
            else:
                condition_list.append(condition_dict[condition_key] % k)  # 生成 FIELD in (?,...)
                values.append(value)
    if condition_list:
        return r' AND '.join(condition_list), values
    return '', []


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
    return parameters  # GET


def except_keys(post_parameters, keys):
    """
    排除用户参数
    :return:
    """
    for var in keys:
        if var in post_parameters.keys():
            post_parameters.pop(var)
    return post_parameters


def get_config(path):
    """
    获取接口配置信息
    :return:
    """
    sql = "select a.URL, a.ALLOW_METHOD, a.ALLOW_IP,a.TARGET_TABLE_OR_VIEW, a.EXECUTE_SQL, a.PER_PAGE, " \
          "a.RETURN_TARGET_TABLE_OR_VIEW, a.STATUS API_STATUS, a.RETURN_FIELD, a.SORT, a.CONDITION, a.ALIAS_FIELDS," \
          "a.INSERT_STATUS, a.DELETE_STATUS, a.UPDATE_STATUS, a.INSERT_FIELDS, a.DELETE_FIELDS, a.UPDATE_FIELDS," \
          "a.RETURN_FIELDS,a.RETURN_TOTAL, b.TYPE, b.DB, b.IP," \
          "b.PORT, b.USERNAME, b.PASSWORD, b.STATUS DB_STATUS from T_API_CONFIG a, T_API_DATABASES b where a.STATUS='1'" \
          " and a.TARGET_DB=b.NAME and a.url='%s'" % path
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    config_data = sqlite3_db.get_json(sql)
    if config_data:
        config_data = json.loads(config_data.replace("\\\\", "\\"))[0]
        config_data['INSERT_FIELDS'] = json.loads(config_data['INSERT_FIELDS']) if config_data['INSERT_FIELDS'] else {}
        config_data['DELETE_FIELDS'] = json.loads(config_data['DELETE_FIELDS']) if config_data['DELETE_FIELDS'] else {}
        config_data['UPDATE_FIELDS'] = json.loads(config_data['UPDATE_FIELDS']) if config_data['UPDATE_FIELDS'] else {}
        config_data['ALIAS_FIELDS'] = json.loads(config_data['ALIAS_FIELDS']) if config_data['ALIAS_FIELDS'] else {}
        config_data['CONDITION'] = json.loads(config_data['CONDITION']) if config_data['CONDITION'] else {}
        config_data['SORT'] = json.loads(config_data['SORT']) if config_data['SORT'] else {}
        config_data["RETURN_FIELDS"] = json.loads(config_data["RETURN_FIELDS"]) if config_data["RETURN_FIELDS"] else {}
        config_data['PAGE_KEY'] = 'PAGE'
    return config_data


def check_ip_valid(ip, white_list=None):
    """
    检查访问ip合法性
    :param ip:
    :param white_list:
    :return:
    """
    if white_list is None:
        white_list = []
    if '*' in white_list:
        return True
    if ip in white_list:
        return True
    return False


def check_call_method_valid(user_call_method, white_list=None):
    """
    检查访问ip合法性
    :param user_call_method:['POST', 'GET'], '*' or 'ALL'
    :param white_list:
    :return:
    """
    if white_list is None:
        white_list = []
    if 'ALL' in white_list or '*' in white_list:
        return True
    elif user_call_method == white_list:
        return True
    elif user_call_method in white_list:
        return True
    return False


def context_construct(request, path, context=None):
    """
    上下文生成函数
    :param context:
    :param request:
    :param path:
    :return:
    """
    if context is None:
        context = {}
    path = path.split('/')
    context["op"] = ''
    context["path"] = path[0]
    if len(path) > 1:
        context["op"] = path[1].upper()
    context["method"] = request.method
    context["ip"] = request.META["REMOTE_ADDR"]             # 访问IP
    context["page"] = request.GET.get("page", None)         # 页码分页
    context["offset"] = request.GET.get("offset", None)     # 偏移分页
    context["limit"] = request.GET.get("limit", None)       # 限制返回条数
    if request.method == 'POST':
        context["offset"] = request.POST.get("offset", '0')
        context["limit"] = request.POST.get("limit", '0')
    context["parameters"] = request_data(request)           # 数据转字典
    context['sort'] = {}                                    # 用户自定义排序 格式sort=field1_asc:field2_desc...
    context['err'] = ""
    if request.GET.get("sort", ''):
        for field_sort in request.GET.get("sort", '').split(':'):
            try:
                field, sort = field_sort.split('_')
                if sort.upper() != 'ASC' and sort.upper() != 'DESC':
                    context['err'] = "参数%s的排序参数不合法: 应该为%s_ASC或%s_DESC" % (field, field, field)
                    return context
                context['sort'][field] = sort
            except:
                context['err'] = "排序参数不规范: 正确格式sort=field1_asc:field2_desc..."
                return context
    except_key = ["csrfmiddlewaretoken", "offset", "page", "limit", "sort"]     # 过滤参数
    for var in except_key:
        if var in context["parameters"].keys():
            context["parameters"].pop(var)
    context["config"] = get_config(context["path"])     # 接口配置
    context['builtin_values'] = {}                      # 上下文变量
    return context


def query_field_check(post_parameters, condition_parameters, alias_parameters):
    """
    查询字段合法性检查
    :param alias_parameters:
    :param condition_parameters:
    :param post_parameters:
    :return:
    """
    illegal_condition_field = []       # 非法请求入参条件
    for k in post_parameters.keys():
        k = k.upper()
        if k not in condition_parameters.keys() and k not in alias_parameters.keys():
            illegal_condition_field.append(k.upper())
    return illegal_condition_field


def parameters_vail(parameters, condition_rules, alias_field):
    """
    参数校验 用于增删改
    :param condition_rules:
    :param parameters:
    :param alias_field:
    :return:
    """
    if not condition_rules:
        condition_rules = {}
    for k in parameters.keys():
        k = k.upper()
        if k not in condition_rules.keys():           # 不在条件里面
            if k not in alias_field.keys():           # 不在别名里面
                return False,  '不允许参数:%s' % k.upper()
            elif k in alias_field.keys() and alias_field[k] not in condition_rules.keys():  # 在别名里面 但是不在条件规则里面
                return False, '参数:%s找不到关联数据库字段，请检查接口配置' % k.upper()
        elif condition_rules[k] != "":                # 规则判断
            if "RE" in condition_rules[k].keys():     # 自定义正则
                if not re.match(condition_rules[k]['RE'], parameters[k]):     # 正则校验参数合法性
                    return False, ""
            else:
                if "TYPE" in condition_rules[k].keys():   # 自定义数据类型 否则不检查
                    if condition_rules[k]["TYPE"] == "NUMBER":
                        re.match(r'\d*', parameters[k])  # 正则校验参数合法性
                    else:
                        return False, ""
    return True, ""


def get_return_fields(fields):
    """
    返回自定义字段信息，FIELD1, FIELD2,... ['FIELD1', 'FIELD2']
    :param fields:
    :return:
    """
    if fields:
        return ','.join(fields)
    else:
        return " * "


def sort_for_sql(config_sort, user_sort):
    """
    将JSON的排序转换成SQL排序
    :param config_sort:
    :param user_sort:
    :return:
    """
    sort_key = []
    if user_sort:       # 用户排序为主
        config_sort = user_sort
    sort_str = " order by "
    for k, v in config_sort.items():
        sort_str += "%s " + v.upper() + ","
        sort_key.append(k)
    if len(sort_key):
        return sort_str[:-1], sort_key
    else:
        return '', []

