from django.http import JsonResponse
# from utils.RawSql import *
# from .Util_Methods import ParsePost, db_log, params_check
# from .PrivilegesWrapper import *
#
#
# @params_check(['role_name'])
# def create_role(request):
#     """
#     角色创建接口
#     :param request:
#     :return:
#     """
#     call_user = request.COOKIES.get('username', None)
#     post_data = ParsePost(request)
#     if 'role_name' not in post_data.keys():
#         return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "角色名称不可为空"}, status=200, safe=False,
#                             json_dumps_params={"ensure_ascii": False})
#     if role.create_role(post_data):
#         db_log('privilege', call_user, '新增角色%s成功' % post_data['role_name'], request.META["PATH_INFO"],
#                request.META["REMOTE_ADDR"])
#         return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "新增角色%s成功" % post_data['role_name']}, status=200, safe=False,
#                             json_dumps_params={"ensure_ascii": False})
#     db_log('privilege', call_user, '新增角色%s失败' % post_data['role_name'], request.META["PATH_INFO"],
#            request.META["REMOTE_ADDR"])
#     return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "新增角色%s失败" % post_data['role_name']}, status=200, safe=False,
#                         json_dumps_params={"ensure_ascii": False})
#
#
# @params_check(['role_name'])
# def del_role(request):
#     """
#     角色删除及其撤销用户该角色的权限
#     :param request:
#     :return:
#     """
#     call_user = request.COOKIES.get('username', None)
#     post_data = ParsePost(request)
#     if 'role_name' not in post_data.keys():
#         return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "角色名称不可为空"}, status=200, safe=False,
#                             json_dumps_params={"ensure_ascii": False})
#     if role.del_role(post_data['role_name']):
#         db_log('privilege', call_user, '删除角色%s成功' % post_data['role_name'], request.META["PATH_INFO"],
#                request.META["REMOTE_ADDR"])
#         return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "删除角色%s成功" % post_data['role_name']}, status=200, safe=False,
#                             json_dumps_params={"ensure_ascii": False})
#     db_log('privilege', call_user, '删除角色%s失败' % post_data['role_name'], request.META["PATH_INFO"],
#            request.META["REMOTE_ADDR"])
#     return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "删除角色%s失败" % post_data['role_name']}, status=200, safe=False,
#                         json_dumps_params={"ensure_ascii": False})
#
#
# @params_check(['role_id', 'role_name'])
# def update_role(request):
#     """
#     角色更新
#     :param request:
#     :return:
#     """
#     call_user = request.COOKIES.get('username', None)
#     post_data = ParsePost(request)
#     if 'role_name' not in post_data.keys() or 'role_id' not in post_data.keys():
#         return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "角色id或者名称不可为空"}, status=200, safe=False,
#                             json_dumps_params={"ensure_ascii": False})
#     if role.update_role(post_data['role_id'], post_data['role_name']):
#         db_log('privilege', call_user, '更新角色为%s成功' % post_data['role_name'], request.META["PATH_INFO"],
#                request.META["REMOTE_ADDR"])
#         return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "更新角色%s成功" % post_data['role_name']}, status=200, safe=False,
#                             json_dumps_params={"ensure_ascii": False})
#     db_log('privilege', call_user, '更新角色%s失败' % post_data['role'], request.META["PATH_INFO"],
#            request.META["REMOTE_ADDR"])
#     return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "更新角色%s失败" % post_data['role_name']}, status=200, safe=False,
#                         json_dumps_params={"ensure_ascii": False})
#
#
# @params_check(['username'])
# def get_user_roles(request):
#     """
#     获取某角色下的所有用户
#     :param request:
#     :return:
#     """
#     call_user = request.COOKIES.get('username', None)
#     post_data = ParsePost(request)
#     return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "获取成功", "DATA": role.get_user_roles((post_data['username']
#                                                                                            or call_user))}, status=200,
#                         safe=False, json_dumps_params={"ensure_ascii": False})
#
#
# @params_check(['role_name'])
# def get_role_users(request):
#     """
#     获取角色下的用户
#     :param request:
#     :return:
#     """
#     post_data = ParsePost(request)
#     return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "获取成功", "DATA": role.get_roles_user((post_data['role_name']))}, status=200,
#                         safe=False, json_dumps_params={"ensure_ascii": False})
#
#
# @params_check(['username', 'role_name'])
# def grant_role_to_user(request):
#     """
#     授权某用户某角色
#     :param request:
#     :return:
#     """
#     call_user = request.COOKIES.get('username', None)
#     post_data = ParsePost(request)
#     if role.grant_role_to_user(username=post_data['username'], create_user=call_user, role_id=post_data['role_id']):
#         db_log('privilege', call_user, '授权角色%s给%s成功' % (post_data['username'], post_data['role_name']),
#                request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
#         return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '授权角色%s给%s成功' % (post_data['username'], post_data['role_name'])},
#                             status=200, safe=False, json_dumps_params={"ensure_ascii": False})
#     db_log('privilege', call_user, '授权角色%s给%s失败' % (post_data['username'], post_data['role_name']),
#            request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
#     return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '授权角色%s给%s失败' % (post_data['username'], post_data['role_name'])},
#                         status=200, safe=False, json_dumps_params={"ensure_ascii": False})
#
#
# @params_check(['username', 'role_id', 'role_name'])
# def revoke_role_from_user(request):
#     """
#     撤销某用户某角色
#     :param request:
#     :return:
#     """
#     call_user = request.COOKIES.get('username', None)
#     post_data = ParsePost(request)
#     if role.revoke_role_from_user(username=post_data['username'], role_id=post_data['role_id']):
#         db_log('privilege', call_user, '撤销%s角色的%s成功' % (post_data['username'], post_data['role_name']),
#                request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
#         return JsonResponse({"RTN_CODE": "01", "RTN_MSG": '撤销%s角色的%s成功' % (post_data['username'], post_data['role_name'])},
#                             status=200, safe=False, json_dumps_params={"ensure_ascii": False})
#     db_log('privilege', call_user, '撤销%s角色的%s成功' % (post_data['username'], post_data['role_name']),
#            request.META["PATH_INFO"], request.META["REMOTE_ADDR"])
#     return JsonResponse({"RTN_CODE": "00", "RTN_MSG": '撤销%s角色的%s成功' % (post_data['username'], post_data['role_name'])},
#                         status=200, safe=False, json_dumps_params={"ensure_ascii": False})
#

def error(request, info):
    """
    错误消息反馈
    :param request:
    :param info:
    :return:
    """
    return JsonResponse(info, json_dumps_params={"ensure_ascii": False})
