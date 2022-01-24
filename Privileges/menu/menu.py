from Privileges.login.login import *
import json
__all__ = ['get_category_tree']


def recursion_sub_menu(target_menu, menus):
    result_menus = []
    for menu in menus:
        tmp_menus = []
        if target_menu["SUB_MENU_LINK_ID"] == menu["OWNING_MENU_ID"]:        # 如果该链接下还有链接
            sub_menu = recursion_sub_menu(menu, menus)
            menu["MENU"] = menu["SUB_MENU"]
            menu["MENU_LINK_ID"] = menu["SUB_MENU_LINK_ID"]
            menu["LINK"] = menu["SUB_LINK"]
            del menu["SUB_LINK"]
            del menu["SUB_MENU"]
            del menu["SUB_MENU_LINK_ID"]
            menu["children"] = sub_menu
            tmp_menus.append(menu)
            result_menus.append(tmp_menus)
    return result_menus      # 查询下一个菜单下是否还有链接


def recursion_root_menu(menus, sub_menu_and_menu_relative):
    return_menus = []
    for menu in menus:      # 顶层菜单
        tmp_menus = []
        for sub_menu in sub_menu_and_menu_relative:         # 扫描菜单下所有子菜单及其子菜单的子菜单
            if menu["MENU_LINK_ID"] == sub_menu["OWNING_MENU_ID"]:       # 子菜单的父ID和主菜单ID相同   第一层
                sub_menu['children'] = recursion_sub_menu(sub_menu, sub_menu_and_menu_relative)     # 递归查询子菜单
                sub_menu["MENU"] = sub_menu["SUB_MENU"]
                sub_menu["MENU_LINK_ID"] = sub_menu["SUB_MENU_LINK_ID"]
                sub_menu["LINK"] = sub_menu["SUB_LINK"]
                del sub_menu["SUB_LINK"]
                del sub_menu["SUB_MENU"]
                del sub_menu["SUB_MENU_LINK_ID"]
                tmp_menus.append(sub_menu)
        menu["children"] = tmp_menus
        return_menus.append(menu)
    return return_menus


def get_category_tree(request):
    """
        生成菜单目录树
        :return:
    """
    username = request.COOKIES.get("username")
    rawsql = RawSql()   # 默认数据库
    sql = ""
    if username == "admin":
        sql = "select LINK_ID MENU_ID from MENU_LINKS"
    else:
        sql = "select MENU_ID from ROLE_MENU_PRIVILEGES where ROLE_ID in (select ROLE_ID from  USERS t1, USER_ROLE t2" \
              " where t1.USERNAME=t2.USERNAME and t1.username='%s') union select MENU_ID from USER_MENU_PRIVILEGES " \
              "where USERNAME='%s'" % (username, username)
    auth_menus = rawsql.get_list(sql)  # 获取视图权限
    if not auth_menus:
        return ""
    sql = "select NAME MENU, LINK_ID MENU_LINK_ID, SIBLING_SORT , LINK, ICON_CLASS, OWNING_MENU_ID from " \
          "MENU_LINKS where LINK_ID in  (select OWNING_MENU_ID from MENU_LINKS where LINK_ID in (%s)) and" \
          " OWNING_MENU_ID = 0" % ','.join(['%s' for var in range(len(auth_menus))])
    menus = rawsql.get_json(sql, auth_menus)
    menus = json.loads(menus) if menus else []             # 获取用户授权系统菜单
    sql = "select MENU, MENU_LINK_ID, LINK, SUB_MENU, SUB_LINK, SUB_MENU_LINK_ID, ICON_CLASS, OWNING_MENU_ID," \
          " SUB_MAIN_MENU_SIBLING_SORT MENU_SIBLING_SORT from (select NAME MENU, LINK, LINK_ID MENU_LINK_ID, " \
          "SIBLING_SORT MENU_SIBLING_SORT from MENU_LINKS) MAIN_MENUS ,(select NAME SUB_MENU, LINK SUB_LINK,  LINK_ID "\
          "SUB_MENU_LINK_ID, SIBLING_SORT SUB_MAIN_MENU_SIBLING_SORT, ICON_CLASS, OWNING_MENU_ID from MENU_LINKS "\
          "where OWNING_MENU_ID !=0) SUB_MENUS where MAIN_MENUS.MENU_LINK_ID=SUB_MENUS.OWNING_MENU_ID and" \
          " SUB_MENUS.SUB_MENU_LINK_ID in (%s) order by MAIN_MENUS.MENU_SIBLING_SORT, MAIN_MENUS.MENU," \
          "SUB_MENUS.SUB_MAIN_MENU_SIBLING_SORT, SUB_MENUS.SUB_MENU" % ','.join(['%s' for var in range(len(auth_menus))])
    sub_menu_and_menu_relative = rawsql.get_json(sql, auth_menus)    # 获取授权路径和菜单对应关系
    sub_menu_and_menu_relative = json.loads(sub_menu_and_menu_relative) if sub_menu_and_menu_relative else []
    menus_tree = []
    for menu in menus:
        tmp_menus = []
        for sub_menu in sub_menu_and_menu_relative:
            if menu["MENU_LINK_ID"] == sub_menu["OWNING_MENU_ID"]:  # 子菜单的父ID和主菜单ID相同   第一层
                sub_menu["MENU"] = sub_menu["SUB_MENU"]
                sub_menu["MENU_LINK_ID"] = sub_menu["SUB_MENU_LINK_ID"]
                sub_menu["LINK"] = sub_menu["SUB_LINK"]
                del sub_menu["SUB_LINK"]
                del sub_menu["SUB_MENU"]
                del sub_menu["SUB_MENU_LINK_ID"]
                tmp_menus.append(sub_menu)
        menu["children"] = recursion_root_menu(tmp_menus, sub_menu_and_menu_relative)
        menus_tree.append(menu)
    return menus_tree
