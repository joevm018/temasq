# -*- coding: utf-8 -*-

{
    'name': 'Discount Restricted',
    'version': '9.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Discounts for service only',
    'author': 'Al Kidhma Group',
    'company': 'Al Kidhma Group',
    'images': [],
    'website': '',
    'depends': ['beauty_pos', 'discounts_in_pos'],
    'data': [
        'views/pos_order.xml',
    ],
    'qweb': [
        'static/src/xml/discount.xml'
        ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}

