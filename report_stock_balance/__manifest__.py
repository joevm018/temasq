# -*- coding: utf-8 -*-
{
    'name': 'Inventory Stock Report/ Cost Report',
    'version': '10.0.1.0.0',
    'category': 'account',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
                'beauty_pos',
                ],
    'data': [
        'wizard/stock_balance.xml',
        'reports/reports.xml',
        'reports/report_stock_balance.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'sequence': 1,
    'application': True,
}
