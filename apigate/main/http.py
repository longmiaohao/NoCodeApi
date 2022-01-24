from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from utils.DB import *
from utils.AES import *
import time
from configparser import ConfigParser
from Privileges.PrivilegesWrapper import *
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config = ConfigParser()
config.read(os.path.join(BASE_DIR, "apigate", 'conf', 'api_conf.ini'), encoding='UTF-8')
SECRET_KEY = config["SECRET_KEY"]["key"]
db_path = config["DB_PATH"]["path"]


def base(request):
    """
     默认首页
    :param request:
    :return:
    """
    # create_table()
    page = "home.html"
    base = 1
    return render(request, "base.html", locals())


def ApiConfig(request):
    """
    接口配置主页 新增，修改配置接口
    :param request:
    :return:
    """
    db = DB(db_path)
    db.connection_sqlite3()
    if request.method == "POST":
        name = request.POST.get("name", None)
        if not name:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "名称不可为空"}, None)
        path = request.POST.get("path")
        if not path:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "路径不可为空"})
        allow_method = request.POST.get("allow_method")
        allow_ip = request.POST.get("allow_ip")
        db_name = request.POST.get("db")
        data_table = request.POST.get("data_table")
        sql = request.POST.get("sql", None)
        return_table = request.POST.get("return_table")
        per_page = request.POST.get("per_page")
        return_field_comment = request.POST.get("return_field_comment")
        return_total = request.POST.get("return_total")
        optype = request.POST.get("optype")
        insert_status = request.POST.get("insert_status")
        delete_status = request.POST.get("delete_status")
        update_status = request.POST.get("update_status")
        sort = request.POST.get("sort", None)
        if not db_name:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "需要选择连接数据库"})
        if not sql and not data_table:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "需要选择连接数据表"})
        # sql校验
        if sql and not re.search(r'\{\w*\}', sql):  # 提取SQL里的模版变量:
            db_info_sql = "select username, password, ip, db, port, type from T_API_DATABASES where name = '%s'" % db_name
            info = json.loads(db.get_json(db_info_sql))[0]
            test_db = DB(info["USERNAME"], Aes.decrypt(info["PASSWORD"], SECRET_KEY), info["IP"], info["DB"], info["PORT"])
            if info["TYPE"] == "Mysql":
                test_db.connection_mysql()
                test_db.get_json("select * from (%s) self_define_table" % sql.replace("&quto", "'"))
                test_db.close()
                if test_db.err:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "SQL检查不通过: %s" % test_db.err})
            elif info["TYPE"] == "Oracle":
                pass
            elif info["TYPE"] == "Sqlserver":
                pass
        try:
            if sort:
                json.loads(sort)
                sort = sort.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "排序JSON校验不通过"})
        condition = request.POST.get("condition")
        try:
            if condition:
                json.loads(condition)
                condition = condition.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "条件JSON校验不通过"})
        alias_fields = request.POST.get("alias_fields")
        try:
            if alias_fields:
                json.loads(alias_fields)
                alias_fields = alias_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "字段别名JSON校验不通过"})

        insert_fields = request.POST.get("insert_fields")
        try:
            if insert_fields:
                json.loads(insert_fields)
                insert_fields = insert_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "插入字段JSON校验不通过"})

        delete_fields = request.POST.get("delete_fields")
        try:
            if delete_fields:
                json.loads(delete_fields)
                delete_fields = delete_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "删除字段JSON校验不通过"})
        update_fields = request.POST.get("update_fields")
        try:
            if update_fields:
                json.loads(update_fields)
                update_fields = update_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "更新字段JSON校验不通过"})
        return_fields = request.POST.get("return_fields")
        try:
            if return_fields:
                json.loads(return_fields)
                return_fields = return_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "返回字段JSON校验不通过"})
        if sql:
            return_table = "0"
            return_field_comment = "0"
        status = request.POST.get("status")
        if optype == "add":
            sql = "insert into T_API_CONFIG(NAME, URL, ALLOW_METHOD, ALLOW_IP, TARGET_DB, TARGET_TABLE_OR_VIEW, " \
                  "EXECUTE_SQL, RETURN_TARGET_TABLE_OR_VIEW, STATUS, RETURN_FIELD, CREATE_TIME, PER_PAGE, SORT, " \
                  "CONDITION, ALIAS_FIELDS, INSERT_STATUS, UPDATE_STATUS, DELETE_STATUS, INSERT_FIELDS, UPDATE_FIELDS," \
                  " DELETE_FIELDS, RETURN_FIELDS, RETURN_TOTAL) " \
                  "values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                  (name, path, allow_method, allow_ip, db_name, data_table, sql, return_table, status, return_field_comment,
                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), per_page, sort, condition, alias_fields,
                   insert_status, update_status, delete_status, insert_fields, update_fields, delete_fields, return_fields, return_total)
            msg = "配置成功"
        else:
            sql = "update T_API_CONFIG set URL='%s', ALLOW_METHOD='%s', ALLOW_IP='%s', TARGET_DB='%s'," \
                  " TARGET_TABLE_OR_VIEW='%s', EXECUTE_SQL='%s', RETURN_TARGET_TABLE_OR_VIEW='%s', STATUS='%s', " \
                  "RETURN_FIELD='%s', CZLX='U', CZSJ='%s', PER_PAGE='%s', SORT='%s', CONDITION='%s', ALIAS_FIELDS='%s'," \
                  "INSERT_STATUS='%s', DELETE_STATUS='%s', UPDATE_STATUS='%s', INSERT_FIELDS='%s', DELETE_FIELDS='%s'," \
                  " UPDATE_FIELDS='%s', RETURN_FIELDS='%s', RETURN_TOTAL='%s'  where NAME='%s'" % \
                  (path, allow_method, allow_ip, db_name, data_table, sql, return_table, status, return_field_comment,
                  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), per_page, sort, condition, alias_fields,
                   insert_status, delete_status, update_status, insert_fields, delete_fields, update_fields,
                   return_fields, return_total, name)
            msg = "修改成功"
        if db.execute(sql):
            return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg})
        else:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": db.err})
    database_list = db.get_json("select name, db from T_API_DATABASES")
    if database_list:
        database_list = json.loads(database_list)
    else:
        database_list = []
    page = "ApiConfig.html"
    jiekou = 1
    return render(request, "base.html", locals())


def delete(request):
    name = request.GET.get("name", None)
    del_type = request.GET.get("del_type", None)
    if not name or not del_type:
        name = request.POST.get("name", None)
        del_type = request.POST.get("del_type", None)
    if not name or not del_type:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数不完整"},
                            safe=False, json_dumps_params={"ensure_ascii": False})
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    sql = ""
    if del_type == 'api':
        sql = "delete from T_API_CONFIG where name='%s'" % name
    if del_type == 'db':
        sql = "delete from T_API_DATABASES where name='%s'" % name
    if sqlite3_db.execute(sql):
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "删除成功"},
                            safe=False, json_dumps_params={"ensure_ascii": False})
    else:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "删除失败"},
                            safe=False, json_dumps_params={"ensure_ascii": False})


def ApiList(request):
    """
    获取配置接口列表 有name的时候为单一查询，用于修改
    :param request:
    :return:
    """
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    name = request.GET.get("name")
    if name:
        sql = "select a.NAME, a.URL, a.ALLOW_METHOD, a.ALLOW_IP, a.TARGET_DB, a.TARGET_TABLE_OR_VIEW, "\
            "a.EXECUTE_SQL, a.RETURN_TARGET_TABLE_OR_VIEW, a.STATUS, a.RETURN_FIELD, a.CREATE_TIME,"\
            "a.PER_PAGE, a.TARGET_DB TARGET_DB_NAME, a.CONDITION, a.SORT, a.ALIAS_FIELDS, a.RETURN_FIELDS,"\
            "a.INSERT_STATUS, a.DELETE_STATUS, a.UPDATE_STATUS, a.INSERT_FIELDS, a.DELETE_FIELDS, a.UPDATE_FIELDS,"\
            "a.RETURN_TOTAL, b.DB TARGET_DB from T_API_CONFIG a, "\
            "T_API_DATABASES b where a.TARGET_DB=b.NAME and a.NAME='%s'" % name
        db_list = sqlite3_db.get_json(sql)
    else:
        sql = "select NAME, URL, ALLOW_METHOD, ALLOW_IP, TARGET_DB, TARGET_TABLE_OR_VIEW, "\
              "EXECUTE_SQL, RETURN_TARGET_TABLE_OR_VIEW, STATUS, RETURN_FIELD, CREATE_TIME,"\
              "PER_PAGE,RETURN_FIELDS, RETURN_TOTAL from T_API_CONFIG"
        db_list = sqlite3_db.get_json(sql)
    if db_list:
        db_list = json.loads(db_list.replace('\\\\', '\\').replace('""""', '"{}"'))
    else:
        db_list = []
    if sqlite3_db.err:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": sqlite3_db.err})
    else:
        return JsonResponse({"RTN_CODE": 1, "RTN_MSG": "查询成功", "DATA": db_list})


def GetTablesByDB(request):
    """
    通过数据库查询表
    :param request:
    :return:
    """
    name = request.POST.get("name")
    if not name:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "无参数"})
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    data = sqlite3_db.get_json("select * from T_API_DATABASES where name='%s'" % name)
    if data:
        data = json.loads(data)[0]
        username = data["USERNAME"]
        password = Aes.decrypt(data["PASSWORD"], SECRET_KEY)
        host = data["IP"]
        port = data["PORT"]
        db_name = data["DB"]
        db_type = data["TYPE"]
        db = DB(username, password, host, db_name, port)
        sql = ""
        if db_type == "Mysql":
            sql = "select TABLE_NAME, TABLE_COMMENT from information_schema.tables where TABLE_SCHEMA='%s'" % db_name
            if not db.connection_mysql():
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库连接失败"})
        elif db_type == "Oracle":
            sql = "select TABLE_NAME, COMMENTS TABLE_COMMENT from user_tab_comments"
            if not db.connection_oracle():
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库连接失败"})
        elif db_type == "Sqlserver":
            sql = "select t1.name TABLE_NAME, t2.VALUE TABLE_COMMENT from (select name, id from sysobjects where " \
                  "xtype = 'u' and name != 'sysdiagrams') t1 LEFT JOIN " \
                  "(select value, major_id from sys.extended_properties ex_p where ex_p.minor_id=0)" \
                  " t2 on t1.id=t2.major_id"
            if not db.connection_sqlserver():
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库连接失败"})
        data = db.get_json(sql)
        if data:
            data = json.loads(data)
        else:
            data = []
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "查询成功", "DATA": data})
    else:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库没有配置"})


@require_http_methods(["POST"])
def TestConnection(request):
    """
    数据库连接测试
    :param request:
    :return:
    """
    db_type = request.POST.get("type")
    ip = request.POST.get("ip")
    port = request.POST.get("port")
    username = request.POST.get("username")
    password = request.POST.get("password")
    db = request.POST.get("db")
    db = DB(username, password, ip, db, port)
    flag = False
    if db_type == "Oracle":
        if db.connection_oracle():
            flag = True
    elif db_type == "Mysql":
        if db.connection_mysql():
            flag = True
    elif db_type == "Sqlserver":
        if db.connection_sqlserver():
            flag = True
    db.close()
    if flag:
        return JsonResponse({"RTN_CODE": 1, "RTN_MSG": "连接成功"})
    else:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": db.err})


def DatabaseList(request):
    """
    获取数据库列表 有name的时候为单一查询，用于修改
    :param request:
    :return:
    """
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    name = request.GET.get("name")
    if name:
        db_list = sqlite3_db.get_json("select NAME, type, DB, IP, PORT, USERNAME, STATUS"
                                      " from T_API_DATABASES WHERE NAME='%s'" % name)
    else:
        db_list = sqlite3_db.get_json("select NAME, type, DB, IP||':'||PORT as IP_PORT, USERNAME, CREATE_TIME, STATUS"
                                      " from T_API_DATABASES")
    if db_list:
        db_list = json.loads(db_list)
    else:
        db_list = []
    return JsonResponse({"RTN_CODE": 1, "RTN_MSG": "查询成功", "DATA": db_list})


@require_http_methods(["POST"])
def ChangeStatus(request):
    """
    更改数据库使用激活状态
    :param request:
    :return:
    """
    optype = request.POST.get("type")
    status = request.POST.get("status")
    name = request.POST.get("name")
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    sql = ""
    if optype == "database_qyzt":
        sql = "update T_API_DATABASES set status='%s' where name='%s'" % (status, name)
    elif optype == "api_qyzt":
        sql = "update T_API_CONFIG set status='%s' where name='%s'" % (status, name)
    elif optype == "return_field":
        sql = "update T_API_CONFIG set return_field='%s' where name='%s'" % (status, name)
    elif optype == "return_target_table_or_view":
        sql = "update T_API_CONFIG set return_target_table_or_view='%s' where name='%s'" % (status, name)
    if sqlite3_db.execute(sql):
        return JsonResponse({"RTN_CODE": 1, "RTN_MSG": "修改状态成功"})
    if sqlite3_db.execute(sql):
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": sqlite3_db.err})


def DatabaseManagement(request):
    """
    数据库管理首页 数据库新增，修改接口
    :param request:
    :return:
    """
    if request.method == "POST":
        name = request.POST.get("name")
        if not name:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "名称不可为空"})
        db_type = request.POST.get("type")
        ip = request.POST.get("ip")
        port = request.POST.get("port")
        username = request.POST.get("username")
        password = request.POST.get("password")
        password = Aes(32, SECRET_KEY).encrypt(password)
        db = request.POST.get("db")
        optype = request.POST.get("optype")
        status = request.POST.get("status")
        sqlite3_db = DB(db_path)
        sqlite3_db.connection_sqlite3()
        if optype == "add":
            sql = "insert into T_API_DATABASES(NAME, TYPE, DB, IP, PORT, USERNAME, PASSWORD, CREATE_TIME, STATUS)" \
                  "values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
                  % (
                  name, db_type, db, ip, port, username, password, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  status)
            msg = "新增成功"
        else:
            sql = "update T_API_DATABASES set TYPE='%s', DB='%s', IP='%s', PORT='%s', USERNAME='%s', PASSWORD='%s', STATUS='%s'," \
                  " CZLX='U', CZSJ='%s' where NAME='%s'" % (db_type, db, ip, port, username, password, status,
                                                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), name)
            msg = "修改成功"
        if sqlite3_db.execute(sql):
            return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg})
        else:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": sqlite3_db.err})
    page = "DatabaseManagement.html"
    database = 1
    return render(request, "base.html", locals())
