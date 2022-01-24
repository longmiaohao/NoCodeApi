from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import random
import string
import logging
import os
import time
from utils.AES import Aes
from django.conf import settings
from Privileges.privilege.privilege import *
from django.conf import settings

# 自定义日志文件
logger = logging.getLogger(__name__)
login_log_path = os.path.join(settings.BASE_DIR, "log")
if not os.path.exists(login_log_path):
    os.mkdir(login_log_path)
fh = logging.FileHandler(os.path.join(login_log_path, 'login.log'), encoding="utf-8")     # 当前工程下面 log文件夹的开交换机端口日志.log
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel('INFO')


def login_db_log(username, operation, ip):
    """
    数据库日志记录
    :return:
    """
    try:
        log_table = settings.LOG_TABLE
    except:
        raise Exception("没有在settings里面设置LOG_TABLE指定日志表，字段：TYPE, USERNAME, OPERATION, IP，DATE")
    sql = "insert into %s (TYPE, USERNAME, OPERATION, PATH, IP, DATE) values('%s', '%s', '%s', '%s', '%s', %s)" \
          % (log_table, 'login', username, operation, reverse('login'), ip, 'NOW()')
    rawsql = RawSql()
    rawsql.execute(sql)


def login_view(request, return_template):
    """
    登录
    :param request:
    :param return_template:
    :return:
    """
    next_url = request.GET.get("next_url", '/qtmj/')
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    if request.method == "POST":
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        code = request.POST.get("valid_code", '').lower()     # 用户验证码
        login_failed = r.get('login_' + username)
        if login_failed:
            if int(login_failed) == 5:
                return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该账户已被禁用, 一小时后自动解禁"}, safe=False,
                                    json_dumps_params={"ensure_ascii": False})
        if not username or not password:
            code, code_image = valid_code()  # 生成验证码
            r.set(username + "_valid_code", code)
            return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "用户名或者密码不可为空", "VALID_CODE": code_image}, safe=False,
                                json_dumps_params={"ensure_ascii": False})
        sql = "select USERNAME, PASSWORD, NAME, IS_ACTIVE from USERS where USERNAME=%s"
        rawsql = RawSql()
        data = rawsql.get_list(sql, [username])
        username_code = r.get(username + '_valid_code')
        if username_code:        # 应该有验证码传入
            if not code:        # 该输入验证码 没有输入
                code, code_image = valid_code()  # 生成验证码
                r.set(username + "_valid_code", code)
                return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "请输入验证码", "VALID_CODE": code_image}, safe=False,
                                    json_dumps_params={"ensure_ascii": False})
            elif username_code != code:     # 查到验证码 且验证码没有过期
                code, code_image = valid_code()  # 生成验证码
                r.set(username + "_valid_code", code)
                return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "验证码错误", "VALID_CODE": code_image}, safe=False,
                                    json_dumps_params={"ensure_ascii": False})
        if not data:
            login_failed = int(login_failed) if login_failed else 0
            r.set('login_' + username, 1 + int(login_failed))
            if login_failed == 4:
                r.expire('login_' + username, 3600)
                return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该账户已被禁用, 一小时后自动解禁"}, safe=False,
                                    json_dumps_params={"ensure_ascii": False})
            code, code_image = valid_code()      # 生成验证码
            r.set(username + "_valid_code", code)
            return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "用户名或者密码错误, 剩余%s次机会" % (5 - int(login_failed) - 1),
                                 "VALID_CODE": code_image}, safe=False, json_dumps_params={"ensure_ascii": False})
        aes = Aes(32, settings.AES_KEY)
        if username != data[0] or aes.encrypt(password) != data[1]:
            logger.warning("%s 登录失败, 密码错误" % username)
            login_db_log(username, '登录失败, 密码错误', request.META['REMOTE_ADDR'])
            login_failed = int(login_failed) if login_failed else 0
            r.set('login_' + username, 1 + int(login_failed))
            if login_failed == 4:
                r.expire('login_' + username, 3600)
                return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该账户已被禁用, 一小时后自动解禁"}, safe=False,
                                    json_dumps_params={"ensure_ascii": False})
            code, code_image = valid_code()  # 生成验证码
            r.set(username + "_valid_code", code)
            return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "用户名或者密码错误, 剩余%s次机会" % (5 - int(login_failed) - 1),
                                 "VALID_CODE": code_image}, safe=False, json_dumps_params={"ensure_ascii": False})
        if data[3] == '0':
            return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "该账户已被禁用"}, safe=False,
                                json_dumps_params={"ensure_ascii": False})
        logger.info("%s 登录成功" % username)
        r.delete('login_' + username)
        r.delete(username + "_valid_code")
        login_db_log(username, '登录成功', request.META['REMOTE_ADDR'])
        response = JsonResponse({"RTN_CODE": "01", "RTN_MSG": "登录成功", "NEXT_URL": next_url}, safe=False,
                                json_dumps_params={"ensure_ascii": False})
        session_value = ""
        for i in range(0, int(128)):    # 生成sessionid
            session_value += "".join(random.sample(string.ascii_letters + string.digits, 8))
        response.set_cookie("_sessionid", session_value, httponly=True)
        response.set_cookie("username", username)
        try:
            view_privileges, api_privileges = get_privileges(username)
            sql = "select t1.ROLE_ID, t2.NAME from USER_ROLE t1, ROLE t2 where t1.ROLE_ID=t2.ROLE_ID and t1.USERNAME=%s"
            role_info = rawsql.get_list(sql, [username])
            r.hmset(session_value, {"login_time": time.time(),
                                    "username": username,
                                    "name": data[2],
                                    "roleid": role_info[0],
                                    "rolename": role_info[1],
                                    "privileges": json.dumps({"view_privileges": view_privileges,
                                                             "api_privileges": api_privileges})})
            r.expire(session_value, 3600)
            r.close()
        except Exception as e:
            return JsonResponse({"RTN_CODE": "500", "RTN_MSG": " 登录错误：" + str(e)}, safe=False,
                                json_dumps_params={"ensure_ascii": False})
        return response
    sessionid = request.COOKIES.get("_sessionid", None)
    if sessionid:
        # r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        if r.hget(sessionid, 'username') == request.COOKIES.get('username', '-1'):
            r.close()
            if next_url:
                return redirect(next_url)
            else:
                return redirect(reverse('index'))
        r.close()
    return render(request, return_template)


def logout_view(request, return_path):
    """
    注销登录
    :param request:
    :param return_path:
    :return:
    """
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    username = request.COOKIES.get("username", None)
    r.delete(request.COOKIES.get("_sessionid", None))
    logger.info("%s 注销登录" % username)
    return redirect(reverse(return_path))


def login_check(request):
    """
    登录状态检测
    :param request:
    :return:
    """
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    _sessionid = request.COOKIES.get("_sessionid", 'anonymous')
    username = request.COOKIES.get("username", 'anonymous')
    if r.hget(_sessionid, 'username') == username:
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "valid"}, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "invalid"}, safe=False,
                        json_dumps_params={"ensure_ascii": False})


def valid_code():
    """
    生成二维码
    :return:
    """
    import random
    import base64
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from django.conf import settings
    import os
    buffered = BytesIO()
    width, height, font_size, font_num = 100, 50, 20, 4
    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    image = Image.new(mode='RGB', size=(width, height), color=bg_color)
    draw = ImageDraw.Draw(image, mode='RGB')
    font = ImageFont.truetype(os.path.join(settings.BASE_DIR, 'Privileges', 'login', 'fonts', 'default.ttf'), font_size)
    verify = str()
    for i in range(font_num):
        x = random.randint(i * (width / font_num), (i + 1) * (width / font_num) - font_size)
        y = random.randint(0, height - font_size)
        char = random.choice([chr(alpha) for alpha in range(65, 91)] + [str(num) for num in range(10)])
        verify += char
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.text((x, y), char, fill=color, font=font)
    image.save(buffered, format="JPEG")
    bs64encode = str(base64.b64encode(buffered.getvalue()), 'utf-8')
    # return JsonResponse({"RTN_CODE": "01", "DATA": str(bs64encode, 'utf-8')}, status=200)
    return verify.lower(), bs64encode


def refresh_valid_code(request):
    """
    刷新验证码
    :return:
    """
    username = request.POST.get("username", None)
    if not username:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数不完整"}, status=200)
    code, code_image = valid_code()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.set(username + "_valid_code", code)
    r.close()
    return JsonResponse({"RTN_CODE": "01", "DATA": code_image}, status=200)


