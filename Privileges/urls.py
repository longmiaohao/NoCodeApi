"""PrivilegesUtils URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from Privileges.api import userApi
from Privileges.api import roleApi
from Privileges.api import MenuAndApiPrivileges

# 角色接口路由
urlpatterns = [
    url(r"create_role$", roleApi.create_role, name="create_role"),       # 创建角色
    url(r"update_role$", roleApi.update_role, name="update_role"),       # 更新角色
    url(r"del_role$", roleApi.del_role, name="del_role"),             # 删除角色
    url(r"get_user_roles$", roleApi.get_user_roles, name="get_user_roles"),   # 获取用户下所有角色
    url(r"get_role_users$", roleApi.get_role_users, name="get_role_users"),   # 获取角色下所有用户
    url(r"grant_role_to_user$", roleApi.grant_role_to_user, name="grant_role_to_user"),    # 授权用户角色
    url(r"revoke_role_from_user$", roleApi.revoke_role_from_user, name="revoke_role_from_user"),   # 撤销用户角色
]
# 用户接口路由
urlpatterns += [
    url(r"create_user$", userApi.create_user, name="create_user"),       # 创建用户
    url(r"update_user$", userApi.update_user, name="update_user"),       # 更新用户
    url(r"del_user$", userApi.del_user, name="del_user"),             # 删除用户
    url(r"activeuser$", userApi.active_user, name="active_user"),             # 激活用户
    url(r"deactivateuser$", userApi.deactivate_user, name="deactivate_user"),             # 禁用用户
]

# 角色菜单及其API授权接口
urlpatterns += [
    url(r"grant_role_menu$", MenuAndApiPrivileges.grant_role_menu, name="grant_role_menu"),         # 授权角色菜单权限
    url(r"revoke_role_menu$", MenuAndApiPrivileges.revoke_role_menu, name="revoke_role_menu"),      # 撤销角色菜单权限
    url(r"grant_role_api", MenuAndApiPrivileges.grant_role_api, name="grant_role_api"),             # 授权角色api权限
    url(r"revoke_role_api$", MenuAndApiPrivileges.revoke_role_api, name="revoke_role_api"),         # 撤销角色API权限
]

# 用户菜单及其API授权接口

urlpatterns += [
    url(r"grant_user_menu$", MenuAndApiPrivileges.grant_user_menu, name="grant_user_menu"),         # 授权用户菜单权限
    url(r"revoke_user_menu$", MenuAndApiPrivileges.revoke_user_menu, name="revoke_user_menu"),      # 撤销用户菜单权限
    url(r"grant_user_api$", MenuAndApiPrivileges.grant_user_api, name="grant_user_api"),            # 授权用户api权限
    url(r"revoke_user_api$", MenuAndApiPrivileges.revoke_user_api, name="revoke_user_api"),         # 撤销用户api权限
]