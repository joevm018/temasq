# -*- coding: utf-8 -*-

{
    'name': 'Point of Sale Discounts',
    'version': '9.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Discounts in the Point of Sale(Fixed and Percentage) ',
    'author': 'Al Kidhma Group',
    'company': 'Al Kidhma Group',
    'images': [],
    'website': '',
    'depends': ['base', 'point_of_sale', 'account', 'report', 'account_accountant', 'beauty_pos', 'pos_daily_report'],
    'data': [
        'templates.xml',
        'views/account_invoice_view_pos.xml',
        'views/pos_view.xml',
    ],
    'qweb': [
        'static/src/xml/discount.xml'
        ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}

