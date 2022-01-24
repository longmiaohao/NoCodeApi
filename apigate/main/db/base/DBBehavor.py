from utils.DB import *


def connect_db(username, password, host, db, port, db_type='MYSQL'):
    """
    数据库连接
    :return:
    """
    db = DB(username, password, host, db, port)
    dbtype = {"MYSQL": db.connection_mysql, 'ORACLE': db.connection_oracle, 'SQLSERVER': db.connection_sqlserver}
    if db_type.upper() not in dbtype.keys():
        print("不支持数据库类型")
        db.err = "不支持数据库类型"
        return db
    if not dbtype.get(db_type)():
        print("数据库连接失败: %s" % db.err)
        return db
    return db


def construct_get_table_fields_SQL(db_name, table, db_type="Mysql"):
    """
    返回获取表字段的SQL
    :return:
    """
    sql_construct = {
        "MYSQL": "select c.COLUMN_NAME ,c.COLUMN_TYPE ,c.COLUMN_COMMENT from information_schema.COLUMNS c ," \
                 "information_schema.TABLES t where c.TABLE_NAME = t.TABLE_NAME and t.TABLE_SCHEMA = '%s'" \
                 " and t.TABLE_NAME='%s'" % (db_name, table),
        "ORACLE": "select t1.COLUMN_NAME, t1.DATA_TYPE, t2.COMMENTS from user_tab_columns t1 LEFT JOIN " \
                  "user_col_comments t2 on t1.COLUMN_name=t2.COLUMN_NAME and t1.Table_Name=t2.Table_Name where " \
                  "t1.table_name='%s' order by t1.column_name" % table,
        "SQLSERVER": '''
              SELECT top 1 [COLUMN_NAME] = [Columns].name ,
                      [COLUMN_COMMENT] = [Properties].value,
                      [COLUMN_TYPE] = [Types].name
              FROM    sys.tables AS [Tables]
                      INNER JOIN sys.columns AS [Columns] ON [Tables].object_id = [Columns].object_id
                      INNER JOIN sys.types AS [Types] ON [Columns].system_type_id = [Types].system_type_id
                                                         AND is_user_defined = 0
                                                         AND [Types].name <> 'sysname'
                      LEFT OUTER JOIN sys.extended_properties AS [Properties] ON [Properties].major_id = [Tables].object_id
                                                                            AND [Properties].minor_id = [Columns].column_id
                                                                            AND [Properties].name = 'MS_Description'
              WHERE   [Tables].name ='%s' -- and [Columns].name = '字段名'
              ORDER BY [Columns].column_id''' % table
    }
    if db_type.upper() not in sql_construct.keys():
        print("不支持的数据库类型")
        return '*'
    return sql_construct[db_type.upper()]
