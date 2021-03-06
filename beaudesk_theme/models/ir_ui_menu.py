# -*- coding: utf-8 -*-

import base64
import operator
import re
import threading

import odoo
from odoo import api, tools
from odoo.http import request
from odoo.tools.safe_eval import safe_eval as eval
from odoo.tools.translate import _

MENU_ITEM_SEPARATOR = "/"

from odoo import api, fields, models, tools


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    menu_icon_class = fields.Char("Icon Class")
    customize_show = fields.Boolean("Customize Show")

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):
        """ Loads all menu items (all applications and their sub-menus).

        :return: the menu root
        :rtype: dict('children': menu_nodes)
        """
        fields = ['name', 'sequence', 'parent_id', 'action',
                  'web_icon', 'web_icon_data', 'menu_icon_class']
        menu_root_ids = self.get_user_roots()
        menu_roots = menu_root_ids.read(fields) if menu_root_ids else []
        menu_root = {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': menu_roots,
            'all_menu_ids': menu_root_ids.ids,
        }
        if not menu_roots:
            return menu_root

        # menus are loaded fully unlike a regular tree view, cause there are a
        # limited number of items (752 when all 6.1 addons are installed)
        menus = self.search([('id', 'child_of', menu_root_ids.ids)])
        menu_items = menus.read(fields)

        # adds roots at the end of the sequence, so that they will overwrite
        # equivalent menu items from full menu read when put into id:item
        # mapping, resulting in children being correctly set on the roots.
        menu_items.extend(menu_roots)
        menu_root['all_menu_ids'] = menus.ids

        # make a tree using parent_id
        menu_items_map = {
            menu_item["id"]: menu_item for menu_item in menu_items}
        for menu_item in menu_items:
            parent = menu_item['parent_id'] and menu_item['parent_id'][0]
            if parent in menu_items_map:
                menu_items_map[parent].setdefault(
                    'children', []).append(menu_item)

        # sort by sequence a tree using parent_id
        for menu_item in menu_items:
            menu_item.setdefault('children', []).sort(
                key=operator.itemgetter('sequence'))

        return menu_root
