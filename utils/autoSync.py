from DB import *


def get_data_source(username, password, ip, port, db, db_type='mysql', sql="", key_position=0, trans=False):
    """
    同步远端数据库数据源 远端数据源和本地数据源头字段保持一直
    db_type:1 mysql, 2:oracle, 3: sqlserver
    :return:
    """
    db = DB(username, password, ip, port, db)
    dbtype = {"mysql": db.connection_mysql, 'oracle': db.connection_oracle, 'mssql': db.connection_sqlserver}
    if db_type not in dbtype.keys():
        print("不支持数据库类型")
        return False
    if not dbtype.get(db_type)():
        print("数据库连接失败: %s" % db.err)
        return False
    if not sql:
        print("SQL不可为空")
        return False
    data = db.get_list(sql, result_type='col')
    result = {}
    if data:
        for var in data:
            if trans:
                var = list(var)
                var[2] = str(get_real_card(var[2])) # 卡格式转换
            result[var[key_position]] = var     # {'key1': [], 'key2': []}
    return result

def get_real_card(card):
    """
    卡号转化
    :param card:
    :return:
    """
    card_str = hex(int(card))[2:]
    card = card_str[6:8] + card_str[4:6] + card_str[2:4] + card_str[0:2]
    return int(card, 16)

def get_sync_remote_data_source_by_api():
    """
    同步远端api数据源 远端数据源和本地数据源头字段保持一直
    :return:
    """
    pass

def process_compare(remote_data, local_data):
    """
    执行数据源比较
    :return:
    """
    db = DB('root', 'Shuang00', '127.0.0.1', 'DoorController', 3306)
    if not db.connection_mysql():
        print("数据库连接失败:%s" % db.err)
        return
    for remote_var_key in remote_data.keys():
        if remote_var_key not in local_data.keys():    # 不在本地 新增
            insert(db, remote_data[remote_var_key])
        else:
            if remote_data[remote_var_key][2] != local_data[remote_var_key][2]:   # 卡号不一致 更新
                update(db, remote_data[remote_var_key])
                del local_data[remote_var_key]  # 释放空间

def update(db, data):
    """
    更新旧记录
    :return:
    """
    sql = "UPDATE T_MJ_YHLB set CARD_ID='%s' where SFRZH='%s'" % (data[2], data[1])
    if not db.execute(sql):
        print(sql, db.err)


def inset(db, data):
    """
    插入新记录
    :return:
    """
    sql = "INSERT INTO T_MJ_YHLB(XM, SFRZH, CARD_ID, SSDW) VALUES('%s', '%s', '%s', '001004')" % (data[0], data[1], data[2])
    if not db.execute(sql):
        print(sql, db.err)


if __name__ == '__main__':
    """
    同步处理
    :return:
    """
    sql = "select b.smt_name XM,a.smt_showcardno SFRZH, a.smt_cardserial CARD_ID, b.SMT_DEPTCODE from smart_card a,smart_personnel b where a.smt_personnelid=b.smt_personnelid and a.smt_endcode=0 and b.SMT_DEPTCODE='001004010' and a.smt_showcardno='%s'" % '2018213786'
    remote_data_source = get_data_source('smartxf', 'Smartv39xf', '192.168.205.7', 'smartmid', '1521', 'oracle', sql, 1, True)    # 获取远端数据源
    sql = "select XM, SFRZH, CARD_ID, SSDW from T_MJ_YHLB where SFRZH='2018213786'"
    local_data_source = get_data_source('root', 'Shuang00', '127.0.0.1', 'DoorController', '3306', 'mysql', sql, 1)    # 获取本地数据源
    process_compare(remote_data_source, local_data_source)from DB import *


def get_data_source(username, password, ip, port, db, db_type='mysql', sql="", key_position=0, trans=False):
    """
    同步远端数据库数据源 远端数据源和本地数据源头字段保持一直
    db_type:1 mysql, 2:oracle, 3: sqlserver
    :return:
    """
    db = DB(username, password, ip, port, db)
    dbtype = {"mysql": db.connection_mysql, 'oracle': db.connection_oracle, 'mssql': db.connection_sqlserver}
    if db_type not in dbtype.keys():
        print("不支持数据库类型")
        return False
    if not dbtype.get(db_type)():
        print("数据库连接失败: %s" % db.err)
        return False
    if not sql:
        print("SQL不可为空")
        return False
    data = db.get_list(sql, result_type='col')
    result = {}
    if data:
        for var in data:
            if trans:
                var = list(var)
                var[2] = str(get_real_card(var[2])) # 卡格式转换
            result[var[key_position]] = var     # {'key1': [], 'key2': []}
    return result

def get_real_card(card):
    """
    卡号转化
    :param card:
    :return:
    """
    card_str = hex(int(card))[2:]
    card = card_str[6:8] + card_str[4:6] + card_str[2:4] + card_str[0:2]
    return int(card, 16)

def get_sync_remote_data_source_by_api():
    """
    同步远端api数据源 远端数据源和本地数据源头字段保持一直
    :return:
    """
    pass

def process_compare(remote_data, local_data):
    """
    执行数据源比较
    :return:
    """
    db = DB('root', 'Shuang00', '127.0.0.1', 'DoorController', 3306)
    if not db.connection_mysql():
        print("数据库连接失败:%s" % db.err)
        return
    for remote_var_key in remote_data.keys():
        if remote_var_key not in local_data.keys():    # 不在本地 新增
            insert(db, remote_data[remote_var_key])
        else:
            if remote_data[remote_var_key][2] != local_data[remote_var_key][2]:   # 卡号不一致 更新
                update(db, remote_data[remote_var_key])
                del local_data[remote_var_key]  # 释放空间

def update(db, data):
    """
    更新旧记录
    :return:
    """
    sql = "UPDATE T_MJ_YHLB set CARD_ID='%s' where SFRZH='%s'" % (data[2], data[1])
    if not db.execute(sql):
        print(sql, db.err)


def inset(db, data):
    """
    插入新记录
    :return:
    """
    sql = "INSERT INTO T_MJ_YHLB(XM, SFRZH, CARD_ID, SSDW) VALUES('%s', '%s', '%s', '001004')" % (data[0], data[1], data[2])
    if not db.execute(sql):
        print(sql, db.err)


def delete(db, data):
    """
    删除记录
    :return:
    """
    sql = "INSERT INTO T_MJ_DEL_YHLB (SELECT SFRZH, XM, CARD_ID, SSDW, TJSJ, 'NOW()', 'D' FROM T_MJ_YHLB where SFRZH='%s')" % (data[1])
    if not db.execute(sql):
        print(sql, db.err)
        return
    sql = "DELETE FROM T_MJ_YHLB where SFRZH='%s')" % (data[1])
    if not db.execute(sql):
        print(sql, db.err)


if __name__ == '__main__':
    """
    同步处理
    :return:
    """
    sql = "select b.smt_name XM,a.smt_showcardno SFRZH, a.smt_cardserial CARD_ID, b.SMT_DEPTCODE from smart_card a,smart_personnel b where a.smt_personnelid=b.smt_personnelid and a.smt_endcode=0 and b.SMT_DEPTCODE='001004010' and a.smt_showcardno='%s'" % '2018213786'
    remote_data_source = get_data_source('smartxf', 'Smartv39xf', '192.168.205.7', 'smartmid', '1521', 'oracle', sql, 1, True)    # 获取远端数据源
    sql = "select XM, SFRZH, CARD_ID, SSDW from T_MJ_YHLB where SFRZH='2018213786'"
    local_data_source = get_data_source('root', 'Shuang00', '127.0.0.1', 'DoorController', '3306', 'mysql', sql, 1)    # 获取本地数据源
    process_compare(remote_data_source, local_data_source)