import os
from configparser import ConfigParser
from utils.DB import *
import logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
config.read(os.path.join(BASE_DIR, "apigate", 'conf', 'api_conf.ini'), encoding='UTF-8')
db_path = config["DB_PATH"]["path"]


def create_table():
    """
    创建配置表
    字段：
    接口名： 255字符
    接口路径：url
    允许方式：GET POST ALL
    允许IP：
    目标数据库：TARGET_DB
    目标表或者视图：TARGET_TABLE_OR_VIEW
    执行SQL：EXECUTE_SQL
    :return:
    """
    try:
        db = DB(db_path)
        if not db.connection_sqlite3():
            warnings.warn("sqlite3数据库连接失败")
            return False
        sql = '''
            create table T_API_CONFIG(
                NAME nvarchar(255) not null primary key, -- comment '接口名称',
                URL varchar(255) unique , -- comment '部署地址',
                ALLOW_METHOD varchar(255) default 'GET', -- comment '允许方法GET POST ALL',
                ALLOW_IP varchar(255) default '*', -- comment '允许IP * 全部',
                TARGET_DB varchar(255) not null, -- comment '目标数据库',
                TARGET_TABLE_OR_VIEW varchar(255), -- comment '目标表或视图',
                EXECUTE_SQL varchar(3000), -- comment '自定义执行的SQL 优先级最高',
                RETURN_TARGET_TABLE_OR_VIEW varchar(3000) default '1' , -- comment '返回目标表或则视图信息',
                STATUS varchar(2) default '1', -- comment '启用状态',
                RETURN_FIELD varchar(2) default '0', -- comment '返回字段信息 如果是返回全表',
                RETURN_TOTAL varchar(2) default '0', -- comment '返回表记录数量',
                CREATE_TIME varchar(20), -- comment '创建时间',
                PER_PAGE varchar(20) default 'ALL', -- comment '每页记录条数',
                ALIAS_FIELDS varchar(1000), -- comment '字段别名',
                SORT varchar(1000), -- comment '排序',
                RETURN_FIELDS varchar(1000), -- comment '返回字段',
                INSERT_FIELDS varchar(1000), -- comment '插入字段',
                UPDATE_FIELDS varchar(1000), -- comment '修改字段',
                DELETE_FIELDS varchar(1000), -- comment '删除字段',
                DELETE_STATUS varchar(2), -- comment '删除状态',
                INSERT_STATUS varchar(2), -- comment '插入状态',
                UPDATE_STATUS varchar(2), -- comment '更新状态',
                `CONDITION` varchar(1000), -- comment '条件',
                CZLX varchar(2), -- comment '操作类型',
                CZSJ varchar(20) -- comment '操作时间'
            )
        '''
        db.execute(sql)
        sql = '''
            create table T_API_DATABASES(
                NAME nvarchar(255) not null primary key, -- comment '名称',
                TYPE varchar(255), -- comment '数据库类型',
                DB varchar(255), -- comment '数据库',
                IP varchar(255), -- comment '数据库IP',
                PORT varchar(255), -- comment '数据库端口',
                USERNAME varchar(255) not null, -- comment '用户名',
                PASSWORD varchar(255), -- comment '密码',
                CREATE_TIME varchar(20), -- comment '添加时间',
                STATUS varchar(2) default '1', -- comment '启用状态',
                CZLX varchar(2) default 'I', -- comment '操作类型',
                CZSJ varchar(20) -- comment '操作时间'
            )
        '''
        db.execute(sql)
        return True
    except Exception as e:
        print(str(e))
        return False


if __name__ == '__main__':
    if create_table():
        print("初始化数据库成功")
    else:
        print("初始化数据库失败")
