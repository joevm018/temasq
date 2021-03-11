# -*- coding: utf-8 -*-
{
    'name': 'Logo Center Receipt',
    'version': '10.0.1.0.0',
    'category': 'account',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': 'Al Kidhma Group',
    'depends': [
                'beauty_pos',
                'pos_staff',
                ],
    'data': [
        'reports/report_bill.xml',
    ],
    'qweb': ['static/src/xml/report_receipt.xml'],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
