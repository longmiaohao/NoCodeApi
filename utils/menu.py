from Privileges.menu.menu import *
__all__ = ['get_menu_tree']


def recursion_menu_tree(menus, selected_menu='', current_menu=''):
    """
    递归菜单树 自定义样式
    :param menus:
    :param selected_menu:
    :param current_menu:
    :return:
    """
    category_tree = ''
    flag = True
    for menu in menus:
        active = ''
        if menu["children"]:        # 有子节点
            if menu['MENU'] == selected_menu:
                active = 'active selected'
            category_tree += '''
                                 <li class="%s">
                                     <a href="%s">
                                         <i class="%s"></i>
                                         <span class="menu-item">%s</span>
                                          <span class ='down-arrow'></span>                                                                             
                                     </a>
                             ''' % (active, menu["LINK"], menu["ICON_CLASS"], menu['MENU'])
            category_tree += recursion_menu_tree(menu["children"], selected_menu, current_menu)
            category_tree += '</ul>'
            category_tree += '</li>'
        else:
            active = ''
            if menu['MENU'] == current_menu:
                active = 'current'
            if flag:
                if menu['MENU'] == current_menu:
                    flag = False
                    active = 'current'
                    category_tree = category_tree + "<ul class='collapse in'>"
                else:
                    flag = False
                    category_tree = category_tree + "<ul class='collapse'>"
            category_tree += '''
                            <li>
                                <a href='%s' class='%s'>%s</a>
                            </li>
                ''' % (menu["LINK"], active, menu['MENU'])
    return category_tree


def get_menu_tree(request, selected="", current=""):
    """
        生成菜单目录树
        :return:
    """
    if selected and selected != "主页":
        pre_html = '''
                    <li class="">
                        <a href="/qtmj/qtmj/">
                            <i class="icon-chart-alt"></i>
                            <span class="menu-item">主页</span>
                        </a>
                    </li>
        '''
    else:
        pre_html = '''
                    <li class="active selected">
                        <a href="/qtmj/qtmj/">
                            <i class="icon-chart-alt"></i>
                            <span class="menu-item">主页</span>
                        </a>
                    </li>
        '''
    menus_tree = get_category_tree(request)
    html = pre_html + recursion_menu_tree(menus_tree, selected, current)
    return html
