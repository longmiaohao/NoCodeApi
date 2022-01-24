from utils.RawSql import *


def create_user(userinfo=None, db='default'):
    """
    创建用户
    :return:
    """
    if not userinfo:
        raise Exception("请参考USERS表结构传入dict参数")
    rawsql = RawSql(db)
    sql = 'insert into USERS(%s) VALUES(%s)' % (','.join(userinfo.keys()), str(list(userinfo.values()))[1:-1])
    if rawsql.execute(sql):
        return True
    else:
        import warnings
        warnings.warn(rawsql.err_msg)
        return False


def del_user(data=None, db='default'):
    """
    删除用户
    :param data:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    if not data:
        raise Exception("请参考USERS表结构传入dict参数")
    condition = ""
    for key in data.keys():
        condition += "%s='%s' and " % (key, data[key])
    sql = "delete from USERS where " + condition[:-4]
    if rawsql.execute(sql):
        sql = "delete from USER_ROLE where USERNAME='%s'" % data["username"]
        rawsql.execute(sql)
        sql = "delete from USER_API_PRIVILEGES where USERNAME='%s'" % data["username"]
        rawsql.execute(sql)
        sql = "delete from USER_MENU_PRIVILEGES where USERNAME='%s'" % data["username"]
        rawsql.execute(sql)
        return True
    else:
        import warnings
        warnings.warn(rawsql.err_msg)
        return False


def update_user(data=None, db='default'):
    """
    更新用户
    :param data:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    if not data:
        raise Exception("请参考USERS表结构传入dict参数 {'data': {'username': '', 'password': ''}, 'condition': {'username': ''}}")
    key_value = ''
    condition = ''
    for key in data['data'].keys():
        if data['data'][key]:
            key_value += "%s='%s'," % (key, data['data'][key])
    for key in data['condition']:
        condition += "%s='%s'," % (key, data['condition'][key])
    sql = "update USERS set %s where %s" % (key_value[:-1], condition[:-1])
    if rawsql.execute(sql):
        return True
    else:
        import warnings
        warnings.warn(rawsql.err_msg)
        return False


def get_user(data=None, db='default'):
    """
    获取用户
    :param data:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    if not data:
        raise Exception("请参考USERS表结构传入dict参数 {'username': '', 'password': ''}")
    condition = ''
    for key in data.keys():
        for value in data.values():
            condition += "%s='%s'" % (key, value)
    sql = "delete from USERS where " + condition
    import json
    return json.loads(rawsql.get_json(sql))[0]


def active_user(username=None, db='default'):
    """
    激活用户
    :param username:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    if not username:
        raise Exception("没有用户名")
    sql = "update USERS set IS_ACTIVE='1' where USERNAME=%s"
    return rawsql.execute(sql, [username])


def deactivate_user(username=None, db='default'):
    """
    禁用用户
    :param username:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    if not username:
        raise Exception("没有用户名")
    sql = "update USERS set IS_ACTIVE='0' where USERNAME=%s"
    return rawsql.execute(sql, [username])

