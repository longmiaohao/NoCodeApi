from utils.RawSql import *


def create_role(role_name=None, create_user=None, db='default'):
    """
    创建角色
    :param role_name:
    :param create_user:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    sql = "insert into ROLE(NAME, CREATE_USER) VALUES (%s, %s)"
    if rawsql.execute(sql, (role_name, create_user)):
        return True
    else:
        import warnings
        warnings.warn(rawsql.err_msg)
        return False


def del_role(role_name=None, db='default'):
    """
    删除角色并删除撤销拥有该角色的用户权限
    :param role_name:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    sql = "delete from ROLE where name=%s"
    if rawsql.execute(sql, [role_name]):
        sql = "delete from ROLE_MENU_PRIVILEGES where ROLE_ID=(select ROLE_ID from ROLE where NAME=%s)"
        rawsql.execute(sql, [role_name])
        sql = "delete from ROLE_API_PRIVILEGES where ROLE_ID=(select ROLE_ID from ROLE where NAME=%s)"
        rawsql.execute(sql, [role_name])
        return True
    else:
        import warnings
        warnings.warn(rawsql.err_msg)
        return False


def update_role(role_id=None, role_name=None, db='default'):
    """
    更新角色
    :param role_name:
    :param role_id:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    sql = "update ROLE set NAME='%s' where role_id=%s"
    if rawsql.execute(sql, (role_name, role_id)):
        return True
    else:
        import warnings
        warnings.warn(rawsql.err_msg)
        return False


def get_roles_user(role_name=None, db='default'):
    """
    获取某角色下所有用户
    :param role_name:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    sql = "select distinct username from USER_ROLE where ROLE_ID in " \
          "(select ROLE_ID from ROLE where NAME = %s)"
    import json
    return json.loads(rawsql.get_json(sql, [role_name]))


def get_user_roles(username=None, db='default'):
    """
    获取用户所有角色
    :param username:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    sql = "select ROLE_ID, NAME from ROLE where ROLE_ID in (select role_id from USER_ROLE where username=%s)"
    import json
    data = rawsql.get_json(sql, [username])
    if data:
        data = json.loads(data)
    else:
        data = []
    return data


def grant_role_to_user(username=None, create_user=None, role_id=None, db='default'):
    """
    授权用户角色
    :param username:
    :param create_user:
    :param role_id:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    sql = "insert into USER_ROLE(USERNAME, ROLE_ID, CREATE_USER) VALUES (%s, %s, %s)"
    if rawsql.execute(sql, (username, role_id, create_user)):
        return True
    else:
        import warnings
        warnings.warn(rawsql.err_msg)
        return False


def revoke_role_from_user(username=None, role_id=None, db='default'):
    """
    撤销用户角色
    :param username:
    :param role_id:
    :param db:
    :return:
    """
    rawsql = RawSql(db)
    sql = "delete from USER_ROLE where ROLE_ID=%s and USERNAME=%s"
    if rawsql.execute(sql, (role_id, username)):
        return True
    else:
        import warnings
        warnings.warn(rawsql.err_msg)
        return False
