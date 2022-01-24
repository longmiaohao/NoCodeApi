from django.utils.deprecation import MiddlewareMixin
from utils.RawSql import *
from Privileges.privilege.privilege import *
import redis
import json


class ProcessRequest(MiddlewareMixin):
    def process_request(self, request):
        session_id = request.COOKIES.get("_sessionid", None)
        if session_id:
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            username = r.hget(session_id, "username")
            rolename = r.hget(session_id, "rolename")
            roleid = r.hget(session_id, "roleid")
            view_privileges, api_privileges = get_privileges(username)
            privileges = {"view_privileges": view_privileges, "api_privileges": api_privileges}
            r.hmset(session_id, {"privileges": json.dumps(privileges)})
            setattr(request, 'data', {'username': username, "rolename": rolename, "roleid": roleid, "privileges": privileges})

