-- auto-generated definition
create table API_LINKS
(
    LINK_ID        int auto_increment comment '路径代码'
        primary key,
    NAME           varchar(20)   null comment '接口名称',
    LINK           varchar(40)   null comment '接口路径',
    OWNING_MENU_ID int           null comment '所属菜单ID',
    API_SOURCE     int default 0 null comment '接口类型 0配置接口 1非配置接口 ',
    I              int default 0 null comment ' 1 可写接口 0 不可写',
    D              int default 0 null,
    U              int default 0 null,
    S              int default 0 null
)
    comment ' 接口路径表';

-- auto-generated definition
create table MENU_LINKS
(
    LINK_ID        int default 0             not null comment '路径编号'
        primary key,
    NAME           varchar(255) charset utf8 null comment '路径中文名',
    LINK           varchar(255) charset utf8 null comment '路径地址',
    OWNING_MENU_ID int                       null comment '所属菜单',
    SIBLING_SORT   int                       null comment '同级排序',
    ICON_CLASS     varchar(255)              null comment '图标'
)
    comment '菜单路径表' charset = latin1;

-- auto-generated definition
create table ROLE
(
    ROLE_ID     int auto_increment comment '角色ID'
        primary key,
    NAME        varchar(20)                          not null comment '角色名称',
    CREATE_USER varchar(20)                          not null comment '创建人',
    CREATE_TIME datetime default current_timestamp() not null comment '创建时间',
    constraint ROLE_NAME_uindex
        unique (NAME)
)
    comment '角色表';

-- auto-generated definition
create table ROLE_API_PRIVILEGES
(
    ROLE_ID     int                                  null comment '角色ID',
    MENU_ID     int                                  null comment '所属菜单ID',
    API_ID      int                                  not null comment 'API编号',
    API_TYPE    char                                 not null comment 'api类型增I 改U 删D 查S',
    GRANT_USER  varchar(50)                          null,
    CREATE_TIME datetime default current_timestamp() null comment '创建时间'
)
    comment '角色API权限';

-- auto-generated definition
create table ROLE_MENU_PRIVILEGES
(
    ROLE_ID     int                                  not null comment '角色ID',
    MENU_ID     int                                  not null comment '菜单编号',
    GRANT_USER  varchar(50)                          null comment '创建用户',
    CREATE_TIME datetime default current_timestamp() not null
)
    comment '角色菜单权限';

-- auto-generated definition
create table SYSLOG
(
    TYPE      varchar(10) default 'api'               not null comment '接口1或者视图0',
    USERNAME  varchar(50)                             not null comment '用户名',
    PATH      varchar(100)                            null comment '访问路径',
    OPERATION varchar(10)                             not null comment '操作',
    IP        varchar(16)                             not null comment 'IP地址',
    DATE      datetime    default current_timestamp() null
)
    comment '系统日志';

-- auto-generated definition
create table USER_API_PRIVILEGES
(
    USERNAME    varchar(100)                         not null comment '角色ID',
    MENU_ID     int                                  null,
    API_ID      int                                  not null comment 'API编号',
    API_TYPE    char                                 not null comment 'api类型增I 改U 删D 查S',
    GRANT_USER  varchar(50)                          null comment '授权用户',
    CREATE_TIME datetime default current_timestamp() null
)
    comment '用户API权限表';

-- auto-generated definition
create table USER_MENU_PRIVILEGES
(
    USERNAME    varchar(100)                         not null,
    MENU_ID     int                                  not null comment '菜单编号',
    CREATE_TIME datetime default current_timestamp() null,
    GRANT_USER  varchar(50)                          null comment '授权用户'
)
    comment '用户菜单权限表';

-- auto-generated definition
create table USER_ROLE
(
    USERNAME    varchar(100)                         not null comment '用户名',
    ROLE_ID     int                                  not null comment '角色ID',
    CREATE_USER varchar(50)                          null comment '创建用户',
    CREATE_TIME datetime default current_timestamp() not null
)
    comment '用户角色';

-- auto-generated definition
create table USERS
(
    USERNAME    varchar(20)                          not null comment '身份认证号',
    PASSWORD    varchar(128)                         not null comment '密码',
    NAME        varchar(20) charset utf8             not null comment '姓名',
    DEPARTMENT  varchar(20) charset utf8             null comment '单位名称',
    CREATE_TIME datetime default current_timestamp() null comment '添加时间',
    CREATE_USER varchar(50)                          null comment '创建用户',
    IS_ACTIVE   char     default '1'                 not null comment '是否启用 1 启用 0禁用',
    constraint T_MJ_YH_SFRZH_uindex
        unique (USERNAME)
)
    comment '用户表' charset = latin1;

alter table USERS
    add primary key (USERNAME);



