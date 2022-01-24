import os
from utils.RawSql import *
import time
import redis
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DoorController.settings')

rawsql = RawSql()
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=1, decode_responses=True)
r = redis.StrictRedis(connection_pool=pool)
r0 = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True, db=0)


def clear_task(current_task_id, delete_task=True):
    """
    清除当前任务的结果和信息
    :param delete_task:
    :param current_task_id:
    :return:
    """
    r.delete('celery-task-meta-' + current_task_id)
    if delete_task:
        rawsql.execute("DELETE FROM T_SYNC_TASKS where TASK_ID=%s", [current_task_id])


def task_fail_count_add(current_task_id):
    """
    任务失败次数加1
    :param current_task_id:
    :return:
    """
    return rawsql.execute("update T_SYNC_TASKS set TASK_FAIL_COUNTS = TASK_FAIL_COUNTS + 1 where TASK_ID=%s",
                      [current_task_id])


def process_sj_online_status(current_task_id, current_task_info, current_celery_result):
    """
    盛举门禁在线状况回调函数
    :param current_task_id:
    :param current_task_info:
    :param current_celery_result:
    :return:
    """
    msid = current_task_info['EXTRA_DATA']['MSID']
    if current_celery_result['RTN_CODE'] == '01':
        sql = "update T_MJ_MSXX set ZXZT=1, SCZXSJ=%s where ID=%s"
        rawsql.execute(sql, [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), msid])
    else:
        sql = "update T_MJ_MSXX set ZXZT=0 where ID=%s"
        rawsql.execute(sql, [msid])
    clear_task(current_task_id)


def process_qt_lock_recorder(current_task_id, current_task_info, current_celery_result):
    """
    淇泰门禁记录回调函数
    :param current_task_id:
    :param current_task_info:
    :param current_celery_result:
    :return:
    """
    msip = current_task_info['EXTRA_DATA']['IP']
    if current_celery_result['RTN_CODE'] == '01':
        for var in current_celery_result['DATA']:
            sql = "select * from T_MJ_MSSQ t1, T_MJ_MSXX t2 where t1.MS_ID=t2.ID and t1.SFRZH=" \
                  "(select SFRZH from T_MJ_YHLB where CARD_ID=%s) and t2.IP=%s"
            if rawsql.get_list(sql, [var['CARDNUM'], msip]):
                sql = "insert into T_MJ_KMJL(IP, CARD_ID, STATUS, TIME, TYPE, USERNAME) values(%s, %s ,%s, %s," \
                      "%s, (select SFRZH from T_MJ_YHLB where CARD_ID=%s))"
                rawsql.execute(sql, [msip, var['CARDNUM'], 1, var['TIME'], 1, var['CARDNUM']])
    else:
        print(current_celery_result)
    clear_task(current_task_id)


def process_qt_grant_privileges(current_task_id, current_task_info, current_celery_result):
    """
    处理授权结果
    :param current_task_id:
    :param current_task_info:
    :param current_celery_result:
    :return:
    """
    msid = current_task_info['EXTRA_DATA']['MS_ID']
    # card_id = current_task_info['EXTRA_DATA']['CARD_ID']
    sfrzh = current_task_info['EXTRA_DATA']['SFRZH']
    # stime = current_task_info['EXTRA_DATA']['STIME']
    # etime = current_task_info['EXTRA_DATA']['ETIME']
    op_tag = current_task_info['TASK_GROUP_ID']
    if current_celery_result['RTN_CODE'] == '01':
        sql = 'update T_MJ_MSSQ set SQZT=1, SQSJ=NOW() where MS_ID=%s and SFRZH=%s '
        rawsql.execute(sql, [msid, sfrzh])  # 授权入库
        if current_task_info['TASK_RETRY_COUNTS'] == 0:
            count = r0.get(op_tag + '_success')
            if count:
                r0.set(op_tag + "_success", int(count) + 1)
            else:
                r0.set(op_tag + "_success", 1)
            r0.expire(op_tag + "_success", 3600)
        clear_task(current_task_id)
    else:
        task_fail_count_add(current_task_id)        # 失败次数+1
        if current_task_info['TASK_RETRY_COUNTS'] == 0:
            count = r0.get(op_tag + '_failed')
            if count:
                r0.set(op_tag + "_failed", int(count) + 1)
            else:
                r0.set(op_tag + "_failed", 1)
            r0.expire(op_tag + "_failed", 3600)
        print(current_celery_result)
        clear_task(current_task_id, False)


def process_qt_revoke_privileges(current_task_id, current_task_info, current_celery_result):
    """
    处理撤销授权结果
    :param current_task_id:
    :param current_task_info:
    :param current_celery_result:
    :return:
    """
    msid = current_task_info['EXTRA_DATA']['MS_ID']
    # card_id = current_task_info['EXTRA_DATA']['CARD_ID']
    sfrzh = current_task_info['EXTRA_DATA']['SFRZH']
    # stime = current_task_info['EXTRA_DATA']['STIME']
    # etime = current_task_info['EXTRA_DATA']['ETIME']
    op_tag = current_task_info['TASK_GROUP_ID']
    if current_celery_result['RTN_CODE'] == '01':
        sql = 'DELETE FROM T_MJ_MSSQ WHERE MS_ID=%s and SFRZH=%s '
        rawsql.execute(sql, [msid, sfrzh])  # 授权入库
        if current_task_info['TASK_RETRY_COUNTS'] == 0:
            count = r0.get(op_tag + '_success')
            if count:
                r0.set(op_tag + "_success", int(count) + 1)
            else:
                r0.set(op_tag + "_success", 1)
        clear_task(current_task_id)
    else:
        task_fail_count_add(current_task_id)        # 失败次数+1
        if current_task_info['TASK_RETRY_COUNTS'] == 0:
            count = r0.get(op_tag + '_failed')
            if count:
                r0.set(op_tag + "_failed", int(count) + 1)
            else:
                r0.set(op_tag + "_failed", 1)
            print(current_celery_result)
        clear_task(current_task_id, False)


def process_sj_grant_privileges(current_task_id, current_task_info, current_celery_result):
    """
    处理授权结果
    :param current_task_id:
    :param current_task_info:
    :param current_celery_result:
    :return:
    """
    msid = current_task_info['EXTRA_DATA']['MS_ID']
    # card_id = current_task_info['EXTRA_DATA']['CARD_ID']
    sfrzh = current_task_info['EXTRA_DATA']['SFRZH']
    # stime = current_task_info['EXTRA_DATA']['STIME']
    # etime = current_task_info['EXTRA_DATA']['ETIME']
    op_tag = current_task_info['TASK_GROUP_ID']
    if current_celery_result['RTN_CODE'] == '01':
        sql = 'update T_MJ_MSSQ set SQZT=1, SQSJ=NOW() where MS_ID in (SELECT ID FROM T_MJ_MSXX WHERE IP=(SELECT IP FROM T_MJ_MSXX where ID=%s)) and SFRZH=%s '
        rawsql.execute(sql, [msid, sfrzh])  # 授权入库
        if current_task_info['TASK_RETRY_COUNTS'] == 0:
            count = r0.get(op_tag + '_success')
            if count:
                r0.set(op_tag + "_success", int(count) + 1)
            else:
                r0.set(op_tag + "_success", 1)
            r0.expire(op_tag + "_success", 3600)
        clear_task(current_task_id)
    else:
        if current_task_info['TASK_RETRY_COUNTS'] == 0:
            count = r0.get(op_tag + '_failed')
            if count:
                r0.set(op_tag + "_failed", int(count) + 1)
            else:
                r0.set(op_tag + "_failed", 1)
            r0.expire(op_tag + "_failed", 3600)
            print(current_celery_result)
        clear_task(current_task_id, False)


def process_sj_revoke_privileges(current_task_id, current_task_info, current_celery_result):
    """
    处理撤销授权结果
    :param current_task_id:
    :param current_task_info:
    :param current_celery_result:
    :return:
    """
    msid = current_task_info['EXTRA_DATA']['MS_ID']
    # card_id = current_task_info['EXTRA_DATA']['CARD_ID']
    sfrzh = current_task_info['EXTRA_DATA']['SFRZH']
    # stime = current_task_info['EXTRA_DATA']['STIME']
    # etime = current_task_info['EXTRA_DATA']['ETIME']
    op_tag = current_task_info['TASK_GROUP_ID']
    if current_celery_result['RTN_CODE'] == '01':
        sql = 'DELETE FROM T_MJ_MSSQ WHERE MS_ID in (%s) and SFRZH=%s '
        rawsql.execute(sql, [msid, sfrzh])  # 授权入库
        if current_task_info['TASK_RETRY_COUNTS'] == 0:
            count = r0.get(op_tag + '_success')
            if count:
                r0.set(op_tag + "_success", int(count) + 1)
            else:
                r0.set(op_tag + "_success", 1)
        clear_task(current_task_id)
    else:
        if current_task_info['TASK_RETRY_COUNTS'] == 0:
            count = r0.get(op_tag + '_failed')
            if count:
                r0.set(op_tag + "_failed", int(count) + 1)
            else:
                r0.set(op_tag + "_failed", 1)
            print(current_celery_result)
        clear_task(current_task_id, False)
