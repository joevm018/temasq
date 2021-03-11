# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'TimelineView',
    'category': 'Hidden',
    'description':"""
Odoo Web Calendar view.
==========================

""",
    'author': 'Anitha Varad',
    'version': '2.0',
    'depends': ['web'],
  'qweb': [
        'static/src/xml/web_timeline_mod.xml',
    ],
    'data': [
        'views/web_timeline_template.xml',
    ],
    'auto_install': False
}
