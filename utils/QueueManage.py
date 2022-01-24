from celery import shared_task
from DoorController import celery_app
import os
import re


def new_start_command(queue_name):
    """
    重建启动命令
    :param queue_name:
    :return:
    """
    command_file = "/Users/lh/PycharmProjects/DoorController/celery_remote_task/start.sh"
    master_queue = ['127_0_0_1', 'REMOTE_GATEWAY_STATUS', 'LOCK_DEVICE_STATUS',
                    'REVOKE_TASK_QUEUE', 'GRANT_TASK_QUEUE', 'AUTO_QUEUE', 'AUTO_PROCESS_QUEUE']
    for queue in queue_name:
        master_queue.append(queue)
    master_queue = ','.join(master_queue)
    command = "/Library/Frameworks/Python.framework/Versions/3.6/bin/celery -A celery_remote_task worker -l error -n main -B -Q %s" % master_queue
    with open(command_file, 'w+') as f:
        f.writelines(command)
        f.close()


def create_queue_and_task(queue):
    """
    创建任务和队列
    :param queue:
    :return:
    """
    i = celery_app.control.inspect()
    tasks = [var.split('.')[-1] for var in list(i.registered_tasks().values())[0]]
    if queue not in tasks:
        task_dir = "/Users/lh/PycharmProjects/DoorController/celery_remote_task/dynamic/dytask"
        task_filename = os.path.join(task_dir, "task_" + queue + '.py')
        task_file = os.path.join(task_dir, task_filename)
        lock_queue_file = "/Users/lh/PycharmProjects/DoorController/celery_remote_task/lock_queue.py"
        if not os.path.exists(task_file):  # 检测文件是否存在
            code = """from celery_remote_task.tools.sington import Singleton
from celery_remote_task.tools.fastsington import Fastsingleton


@celery_app.task(queue='%s')
def from_queue_%s(**kwargs):
    return standard_process_request(kwargs)""" % (queue, queue)
            with open(task_filename, 'w+') as f:
                f.write(code)
                f.close()
        if not os.path.exists(lock_queue_file):  # 检测队列文件是否存在
            with open(lock_queue_file, 'w+') as f:
                code = """from kombu import Queue, Exchange

lock_task_queue = (
    Queue("%s", Exchange("%s"), routing_key="%s"),
)
                    """ % (queue, queue, queue)
                f.write(code)
                f.close()
        else:
            from celery_remote_task.lock_queue import lock_task_queue
            new_queue = []
            queue_name = []
            if lock_task_queue:
                for var in lock_task_queue:
                    ip = re.search(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(_((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}',
                                   str(var)).group(0)
                    if ip != queue:
                        var = '    Queue("%s", Exchange("%s"), routing_key="%s")' % (ip, ip, ip)
                        new_queue.append(var)
                        queue_name.append(ip)
            new_queue.append('    Queue("%s", Exchange("%s"), routing_key="%s")' % (queue, queue, queue))
            queue_name.append(queue)
            with open(lock_queue_file, 'w+') as f:
                code = """from kombu import Queue, Exchange

lock_task_queue = (
"""
                for var in new_queue:
                    code += var + ',\r\n'
                code += '\r\n)'
                f.write(code)
                f.close()
            new_start_command(queue_name)  # 重建新启动命令
            import_task(queue_name)     # 新建任务导入
    else:
        print(queue + "已经存在")


def delete_queue_and_task(queue):
    """
    删除任务和队列
    :param queue:
    :return:
    """
    i = celery_app.control.inspect()
    tasks = [var.split('.')[-1] for var in list(i.registered_tasks().values())[0]]
    if queue in tasks:
        task_dir = "/Users/lh/PycharmProjects/DoorController/celery_remote_task/dynamic/dytask"
        task_filename = os.path.join(task_dir, "task_" + queue + '.py')
        task_file = os.path.join(task_dir, task_filename)
        lock_queue_file = "/Users/lh/PycharmProjects/DoorController/celery_remote_task/lock_queue.py"
        if os.path.exists(task_file):  # 检测文件是否存在
            os.remove(task_file)
        from celery_remote_task.lock_queue import lock_task_queue
        new_queue = []
        queue_name = []
        if lock_task_queue:
            for var in lock_task_queue:
                ip = re.search(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(_((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}',
                               str(var)).group(0)
                if ip != queue:
                    var = '    Queue("%s", Exchange("%s"), routing_key="%s")' % (ip, ip, ip)
                    new_queue.append(var)
                    queue_name.append(ip)
        with open(lock_queue_file, 'w+') as f:
            code = """from kombu import Queue, Exchange

lock_task_queue = (
"""
            for var in new_queue:
                code += var + ',\r\n'
            code += '\r\n)'
            f.write(code)
            f.close()
            new_start_command(queue_name)  # 重建新启动命令
            import_task(queue_name)        # 新建任务导入
    else:
        print(queue + "不存在")


def import_task(queue_name):
    """
    新增任务导入
    :param queue_name:
    :return:
    """
    import_task_file = "/Users/lh/PycharmProjects/DoorController/celery_remote_task/dynamic/tasks.py"
    with open(import_task_file, 'w+') as f:
        task = ""
        for queue in queue_name:
            task += "from .dytask.task_%s import *\n\r" % queue
        f.write(task)

