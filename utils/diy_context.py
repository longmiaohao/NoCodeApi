from django.templatetags.static import static
from django.conf import settings
from django.utils.translation import ugettext as _
from utils.RawSql import *
import json
import redis


def get_name(request):
    session_id = request.COOKIES.get('_sessionid')
    if session_id:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        name = r.hget(session_id, "name")
        if not name:
            name = '匿名用户'
        context = {"name": name, "username": request.COOKIES.get('username')}
        return context
    return {}

