from apigate.main.db.base.ToolFunction import filed_generate, quote_generate, condition_generate
import re


def insert_PreSQL_construct(parameters=None, alias_fields=None, table=None):
    """
    插入预处理SQL构造 INSERT INTO TABLE(FIELD1, ...) VALUES(VALUES1,...)
    :param table:
    :param parameters:
    :param alias_fields:
    :return: PreSQL, Values
    """
    if not table:
        print("表不能为空")
        return
    if alias_fields is None:
        alias_fields = []
    if parameters is None:
        parameters = {}
    return "INSERT INTO %s(%s) VALUES (%s)" % (table, filed_generate(parameters.keys(), alias_fields),
                                               quote_generate(len(parameters.values()))), tuple(parameters.values())


def delete_PreSQL_construct(parameters=None, delete_fields=None, alias_fields=None, table=None):
    """
    构造删除预处理函数 DELETE FROM TABLE where FIELD1=? AND ...., [VALUE1,...]
    :param delete_fields:
    :param parameters:
    :param alias_fields:
    :param table:
    :return:
    """
    if alias_fields is None:
        alias_fields = []
    if parameters is None:
        parameters = {}
    condition_parameters = {}
    for k in parameters.keys():
        value = parameters[k]
        if k.upper() in alias_fields.keys():
            value = parameters[k.upper()]
            k = alias_fields[k.upper()]
        condition_parameters[k] = value
    condition_str, condition_values = condition_generate(condition_parameters, delete_fields, alias_fields)
    return "DELETE FROM %s WHERE %s " % (table, condition_str), condition_values


def update_PreSQL_construct(parameters, update_fields, condition_fields, alias_fields, table):
    """
    更新预处理语句构造器 UPDATE TABLE SET FIELD1=?, FIELD2=?... WHERE FIELD3=?,...
    :param parameters:
    :param update_fields:
    :param condition_fields:
    :param alias_fields:
    :param table:
    :return:
    """
    condition_list = []
    field_list = []
    condition_values = []
    update_values = []
    condition_parameters = {}
    for k in parameters.keys():                 # 构造更新参数
        value = parameters[k]
        if k.upper() in alias_fields.keys():    # 别名转换
            value = parameters[k.upper()]
            k = alias_fields[k.upper()]
        else:
            k = k.upper()
        if k in update_fields.keys():           # 更新域
            field_list.append(k)
            update_values.append(value)
        else:                                   # 条件域
            condition_list.append(k)
            condition_values.append(value)
            condition_parameters[k] = value
    condition_str, condition_values = condition_generate(condition_parameters, condition_fields, {})
    if condition_str == '':
        return '', '缺少条件字段: %s' % str(condition_fields.keys())
    return "UPDATE %s SET %s WHERE %s" % (table, filed_generate(field_list, {}, op_type='U'), condition_str), tuple(update_values + condition_values)


def select_template_PreSQL_construct(presql, post_parameters, condition_fields, alias_fields):
    """
    查询预处理语句构造器
    :param presql:
    :param post_parameters:
    :param condition_fields:
    :param alias_fields:
    :return:
    """
    def lower_to_capital(dict_info):
        new_dict = {}
        for i, j in dict_info.items():
            new_dict[i.upper()] = j
        return new_dict
    template_value = re.findall(r'\{\w*\}', presql)      # 提取SQL里的模版变量
    check_fields = list(condition_fields.keys()) + list(alias_fields.keys())
    values = []
    post_parameters = lower_to_capital(post_parameters)
    if template_value:
        for t in template_value:
            field = re.search(r'\w{1,}', t).group(0)   # 获取模版里面的字段名称
            if field not in post_parameters.keys():
                return False, "模版变量" + t + "找不到绑定参数"
            if field in check_fields:           # 模版里面的名称要于条件或者别名字段里的名字一致 方便绑定参数
                if re.search(r'\(\s*\{%s\}\s*\)' % field, presql):
                    multi_values = post_parameters[field].split(',')
                    values.extend(multi_values)
                    presql = presql.replace('{' + field + '}', quote_generate(len(multi_values)))
                else:
                    presql = presql.replace('{' + field + '}', '%s')    # 替换{FIELD}为%s, 同时保存对应的value
                    values.append(post_parameters[field])
            else:
                return False, '字段：%s匹配不到参数' % field
        return presql, values
    else:
        return presql, []


def bind_builtin_values(presql, builtin_value):
    """
     绑定内部变量 内部变量格式{{NAME}}, 内部变量存在于c['builtin_value'], {{NAME}}对应值c['builtin_value']['NAME']
    :return:
    """
    template_value = re.findall(r'\{\{\w*\}\}', presql)      # 提取SQL里的模版变量
    if template_value:
        for t in template_value:
            field = re.search(r'\w{1,}', t).group(0)   # 获取模版里面的字段名称
            if field not in builtin_value.keys():
                return False, "找不到内置变量：" + t
            else:           # 模版里面的名称要于条件或者别名字段里的名字一致 方便绑定参数
                presql = presql.replace('{{' + field + '}}', "'%s'" % builtin_value[field])    # 替换{FIELD}为内置变量值
        return presql, None
    else:
        return presql, None
