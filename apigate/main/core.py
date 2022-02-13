from django.conf import settings
from apigate.main.db.base.Constructor import insert_PreSQL_construct, select_template_PreSQL_construct, \
    update_PreSQL_construct, delete_PreSQL_construct, bind_builtin_values
from apigate.main.db.base.DBBehavor import connect_db, construct_get_table_fields_SQL
from apigate.main.db.base.ToolFunction import check_ip_valid, context_construct, check_call_method_valid, \
    query_field_check, parameters_vail, get_return_fields, condition_generate, sort_for_sql
from configparser import ConfigParser
from utils.DB import *
from django.http import JsonResponse
from utils.AES import *
from functools import wraps
import importlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
# # 传入读取文件的地址，encoding文件编码格式，中文必须
config.read(os.path.join(settings.BASE_DIR, "apigate", 'conf', 'api_conf.ini'), encoding='UTF-8')  # 当前工程下面 conf文件夹的script.ini
SECRET_KEY = config["SECRET_KEY"]["key"]
db_path = config["DB_PATH"]["path"]
debug = True


def filterDecorator(func):
    @wraps(func)
    def inner(*args, **kwargs):
        request = args[0]
        api_name = args[1].split('/')[0]
        module_name = 'apigate.filters.' + api_name  # 模块名的字符串
        __class = None
        try:
            __class = importlib.import_module(module_name)  # 导入的就是需要导入的那个metaclass
            filter_func = eval("__class.%s" % api_name)(request)
            request_process = filter_func.request(request)
            if request_process:
                return request_process
            response = func(*args, **kwargs)
            response = filter_func.response(request, response)
            return response
        except Exception as e:
            return func(*args, **kwargs)
    return inner


@filterDecorator
def index(request, path):
    """
    使用sqlite3数据库
    接口访问控制：IP限制， token限制，方法限制, 入参控制
    分页：page：页码， 放在GET里
    :param request:
    :param path:
    :return:
    """
    c = context_construct(request, path)
    if c['err']:
        return JsonResponse({"RTN_CODE": '00', "RTN_MSG": c['err']},
                            json_dumps_params={'ensure_ascii': False})  # 上下文错误
    db_config = c['config']
    # 获取接口组装参数
    if not db_config:
        return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "该接口未启用或不存在"}, json_dumps_params={'ensure_ascii': False})  # 接口不存在
    # 检查IP合法性
    if not check_ip_valid(c['ip'], db_config['ALLOW_IP'].split(',')):
        return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "IP限制, 禁止访问"}, json_dumps_params={'ensure_ascii': False})  # IP限制
    # 检查调用方法合法性
    if not check_call_method_valid(c['method'], db_config['ALLOW_METHOD'].split(',')):
        return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "调用方法限制, 禁止访问"}, json_dumps_params={'ensure_ascii': False})  # 调用方法限制
    # 数据库连接参数
    db_type = db_config['TYPE']                                             # 数据库类型
    host = db_config['IP']                                                  # 数据库IP
    port = db_config['PORT']                                                # 数据库端口
    username = db_config['USERNAME']                                        # 数据库用户名
    password = Aes.decrypt(db_config['PASSWORD'], SECRET_KEY)               # 数据库AES后的密码
    db_name = db_config['DB']                                                    # 数据库
    # 接口配置参数
    target_table_or_view = db_config['TARGET_TABLE_OR_VIEW']                # 接口的默认数据表或视图 如果没有自定义SQL则取该表数据
    execute_sql = db_config['EXECUTE_SQL'].replace("&quto", "'")            # 接口自定义SQL
    return_target_table_or_view = db_config['RETURN_TARGET_TABLE_OR_VIEW']  # 是否返回目标表数据 如果有自定义SQL 则为否
    if_return_field_info = db_config['RETURN_FIELD']                        # 是否返回数据库字段信息
    return_fields = db_config['RETURN_FIELDS']                              # 返回字段列表
    return_total = db_config['RETURN_TOTAL']                                # 返回记录数量
    per_page = db_config['PER_PAGE']                                        # 默认每页返回的数据个数
    sort = db_config['SORT']                                                # 排序内容 {"FIELD": "ASC"} 用于只返回表数据
    user_sort = c['sort']                                                   # 用户自定义排序 参数要符合表搜索参数定义
    condition = db_config['CONDITION']                                      # 自定义条件字段
    db_status = int(db_config['DB_STATUS'])
    if not db_status:
        return JsonResponse({"RNT_CODE": '00', "RTN_MSG": "数据源被禁用"}, status=200)  # 截止
    # 判断接口是否可以增删改操作
    if c["op"] and c["op"] not in ["INSERT", "UPDATE", "DELETE"]:           # 增删改操作
        return JsonResponse({"RNT_CODE": '00', "RTN_MSG": "404 No Found"}, status=404)  # 截止
    if c["op"] == "INSERT":  # 检测操作合理性
        if c["config"]['INSERT_STATUS'] == '0':
            return JsonResponse({"RNT_CODE": '00', "RTN_MSG": "该接口不支持新增操作"},
                                json_dumps_params={'ensure_ascii': False})
    elif c["op"] == "DELETE":
        if c["config"]['DELETE_STATUS'] == '0':
            return JsonResponse({"RNT_CODE": '00', "RTN_MSG": "该接口不支持删除操作"},
                                json_dumps_params={'ensure_ascii': False})
    elif c["op"] == "UPDATE":
        if c["config"]['UPDATE_STATUS'] == '0':
            return JsonResponse({"RNT_CODE": '00', "RTN_MSG": "该接口不支持修改操作"},
                                json_dumps_params={'ensure_ascii': False})
    alias_fields = db_config['ALIAS_FIELDS']                                # 自定义查询字段别名 {"ALIAS_FIELD": "FIELD"}
    condition_fields = db_config['CONDITION']                               # 自定义搜索条件集合
    if user_sort:
        illegal_condition_field = query_field_check(user_sort, condition_fields, alias_fields)
        if illegal_condition_field:                                         # 返回非法排序字段
            return JsonResponse({"RNT_CODE": '00', "RTN_MSG": "名为:%s的排序字段不被允许" % ','.join(illegal_condition_field)},
                                json_dumps_params={'ensure_ascii': False})
    if condition and not c['op']:                                           # 查询才对条件进行检查
        illegal_condition_field = query_field_check(c['parameters'], condition_fields, alias_fields)
        if illegal_condition_field:                                         # 返回非法查询字段
            return JsonResponse({"RNT_CODE": '00', "RTN_MSG": "名为:%s的字段不被允许" % ','.join(illegal_condition_field)},
                                json_dumps_params={'ensure_ascii': False})
    res_data = {}
    # 用户名 密码 主机 数据库 端口 数据库类型(MYSQL, ORACLE, SQLSERVER)
    db = connect_db(username, password, host, db_name, port, db_type.upper())
    if db.err:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "数据库%s连接失败, %s" % (db_name, db.err)},
                            json_dumps_params={'ensure_ascii': False})
    pre_sql = ""
    pre_sql_values = []
    total_pre_sql = ""
    total_pre_sql_values = []
    msg = ""
    if c['op']:  # 增删改操作判定 查询操作c[op]为空
        # 入参合法性验证
        if c['op'] == "INSERT":                                             # 插入SQL拼接
            if not db_config['INSERT_FIELDS']:                              # 没有定义插入字段 则全部字段都可以插入
                sql = construct_get_table_fields_SQL(db_name, target_table_or_view, db_type)
                table_fields = json.loads(db.get_json(sql))
                for var in table_fields:
                    db_config['INSERT_FIELDS'][var["COLUMN_NAME"]] = ""
            check, err_msg = parameters_vail(c['parameters'], db_config['INSERT_FIELDS'], alias_fields)
            if not check:  # 参数校验
                return JsonResponse({"RTN_CODE": '00', "RTN_MSG": err_msg}, json_dumps_params={'ensure_ascii': False})
            pre_sql, pre_sql_values = insert_PreSQL_construct(c['parameters'], alias_fields, target_table_or_view)
            msg = "新增成功"
        if c['op'] == "DELETE":      # 删除SQL拼接
            if not db_config['DELETE_FIELDS']:
                return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "该接口不支持任何条件的删除"},
                                    json_dumps_params={'ensure_ascii': False})
            check, err_msg = parameters_vail(c['parameters'], db_config['DELETE_FIELDS'], alias_fields)
            if not check:  # 参数校验
                return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "删除操作含有非法字段, %s" % err_msg},
                                    json_dumps_params={'ensure_ascii': False})
            pre_sql, pre_sql_values = delete_PreSQL_construct(c['parameters'], db_config['DELETE_FIELDS'], alias_fields,
                                                              target_table_or_view)
            msg = "删除成功"
        if c['op'] == "UPDATE":
            if not db_config['UPDATE_FIELDS']['UPDATE_FIELDS']:                               # 没有定义编辑字段
                return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "该接口不支持任何字段的修改，请检查接口配置"},
                                    json_dumps_params={'ensure_ascii': False})
            if not db_config['UPDATE_FIELDS']["CONDITION_FIELDS"]:
                return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "接口条件字段未定义，请检查接口配置"},
                                    json_dumps_params={'ensure_ascii': False})
            check, err_msg = parameters_vail(c['parameters'], dict(db_config['UPDATE_FIELDS']["UPDATE_FIELDS"],
                                                                   **db_config['UPDATE_FIELDS']["CONDITION_FIELDS"]),
                                             alias_fields)
            if not check:
                return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "含有非法编辑字段: %s" % err_msg},
                                    json_dumps_params={'ensure_ascii': False})
            pre_sql, pre_sql_values = update_PreSQL_construct(c['parameters'],
                                                              db_config['UPDATE_FIELDS']['UPDATE_FIELDS'],
                                                              db_config['UPDATE_FIELDS']["CONDITION_FIELDS"],
                                                              alias_fields, target_table_or_view)
            msg = "更新成功"
        # 执行数据库增删改操作
        if db.execute(pre_sql.replace("'%'", "'%%'"), pre_sql_values):
            return JsonResponse({"RTN_CODE": '01', "RTN_MSG": msg},
                                json_dumps_params={'ensure_ascii': False})
        else:
            if debug:
                err_msg = db.err
            else:
                err_msg = "内部服务器错误, 新增操作失败"
            return JsonResponse({"RTN_CODE": '00', "RTN_MSG": err_msg},
                                json_dumps_params={'ensure_ascii': False})
    else:
        if c['config']['PER_PAGE'] != 'ALL' and c['config']['PER_PAGE'] != '*':
            if c["page"]:
                if c['limit']:
                    c['limit'] = c['limit']
                else:
                    c['limit'] = c['config']['PER_PAGE']
                c['offset'] = (int(c['page']) - 1) * int(c['limit'])
            elif (c['offset'] and not c['limit']) or (not c['offset'] and c['limit']) or (
                    not c['offset'] or not c['limit']):
                return JsonResponse({"RTN_CODE": '00', "RTN_MSG": "分页参数不完整: 正确格式limit=10&offset=0或者page=1或者page=1"
                                                                  "&limit=10"}, json_dumps_params={'ensure_ascii': False})
        #  按表查询模块
        return_fields = get_return_fields(return_fields)
        if execute_sql:                 # 返回自定义sql数据
            if condition:      # 带条件的查询
                # select * from table where FIELD1={DEFINE_FIELD1} and FIELD2={DEFINE_FIELD2}
                # 替换模版变量
                pre_sql, err_msg = bind_builtin_values(execute_sql, c['builtin_values'])
                if err_msg:
                    return JsonResponse({"RTN_CODE": '00', "RTN_MSG": err_msg}, json_dumps_params={'ensure_ascii': False})
                pre_sql, pre_sql_values = select_template_PreSQL_construct(pre_sql, c['parameters'], condition_fields, alias_fields)
                if not pre_sql:      # 如果presql返回的False 则存在模版匹配不到的字段
                    return JsonResponse({"RTN_CODE": '00', "RTN_MSG": pre_sql_values},
                                        json_dumps_params={'ensure_ascii': False})
                if not pre_sql_values:
                    generate_condition, pre_sql_values = condition_generate(c['parameters'], condition_fields, alias_fields)
                    if generate_condition:
                        pre_sql = "select * from ( %s ) t_wrap where %s" % (pre_sql, generate_condition)
                    else:
                        pre_sql = "select * from ( %s ) t_wrap " % pre_sql
                if re.match(r'^DELETE|^UPDATE|^INSERT', pre_sql.upper()):
                    msgs = {"DELETE": "删除成功", "UPDATE": "更新成功", "INSERT": "新增成功"}
                    if db.execute(pre_sql, pre_sql_values):
                        return JsonResponse({"RTN_CODE": '01', "RTN_MSG": msgs[pre_sql.upper()[:6]]},
                                            json_dumps_params={'ensure_ascii': False})
                    else:
                        if debug:
                            err_msg = db.err
                        else:
                            err_msg = "内部服务器错误"
                        return JsonResponse({"RTN_CODE": '00', "RTN_MSG": err_msg},
                                            json_dumps_params={'ensure_ascii': False})
                total_pre_sql = pre_sql
                total_pre_sql_values = pre_sql_values.copy()
                sql, value = sort_for_sql(sort, user_sort)
                if value:
                    pre_sql += sql
                    pre_sql_values += value
                if per_page != 'ALL':  # 分页接口
                    pre_sql += ' LIMIT %s OFFSET %s'
                    pre_sql_values.extend([int(c['limit']), int(c['offset'])])
            data = db.get_json(pre_sql, pre_sql_values)
            res_data["DATA"] = json.loads(data) if data else []         # 返回None
            if db.err:
                res_data["ERROR_MSG"] = db.err
        elif return_target_table_or_view == '1':                        # 返回表数据
            pre_sql = "SELECT %s FROM %s" % (return_fields, target_table_or_view)
            if condition:
                sql, value = condition_generate(c['parameters'], condition, alias_fields)
                if value:
                    pre_sql += " WHERE " + sql
                    pre_sql_values += value
            total_pre_sql = pre_sql
            total_pre_sql_values = pre_sql_values.copy()
            sql, value = sort_for_sql(sort, user_sort)
            if value:
                pre_sql += sql
                pre_sql_values += value
            if per_page != 'ALL':        # 分页接口
                pre_sql += ' LIMIT %s OFFSET %s'
                pre_sql_values.extend([int(c['limit']), int(c['offset'])])
            data = db.get_json(pre_sql.replace("'%'", "'%%'"), pre_sql_values)     # 返回目标表
            res_data["DATA"] = json.loads(data) if data else []
            if db.err:
                if debug:
                    err_msg = db.err
                else:
                    err_msg = '接口内部错误'
                return JsonResponse({"RTN_CODE": "00", "RTN_MSG": err_msg}, json_dumps_params={'ensure_ascii': False})
        else:
            return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "接口没有数据"}, json_dumps_params={'ensure_ascii': False})
        if if_return_field_info == '1':  # 返回字段信息控制
            sql = construct_get_table_fields_SQL(db_name, target_table_or_view, db_type)
            # sql = "select c.COLUMN_NAME ,c.COLUMN_TYPE ,c.COLUMN_COMMENT from " \
            #       "information_schema.COLUMNS c ,information_schema.TABLES t where c.TABLE_NAME = t.TABLE_NAME" \
            #       " and t.TABLE_SCHEMA = '%s' and t.TABLE_NAME='%s'" % (db, target_table_or_view)
            filed_comment = db.get_json(sql)  # 字段数据
            if filed_comment:
                filed_comment = json.loads(filed_comment)
                res_data["FIELDS"] = filed_comment
            else:
                res_data["FIELDS"] = []
        if return_total == '1':
            total_pre_sql = "select count(*) TOTAL from (%s) t_total" % total_pre_sql
            total = db.get_list(total_pre_sql.replace("'%'", "'%%'"), parameters=total_pre_sql_values)  # 返回总数
            res_data["TOTAL"] = total[0] if total else 0
    res_data["RTN_CODE"] = '01'
    res_data["RTN_MSG"] = "查询成功"
    return JsonResponse(res_data, json_dumps_params={'ensure_ascii': False})
