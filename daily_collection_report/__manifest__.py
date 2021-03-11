# -*- coding: utf-8 -*-
{
    'name': 'DAILY COLLECTION REPORT',
    'version': '10.0.1.0.0',
    'category': 'account',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
                'beauty_pos',
                'pos_daily_report',
                'discounts_in_pos',
                'beauty_foc',
                ],
    'data': [
        'wizard/daily_collection_wizard.xml',
        'reports/reports.xml',
        'reports/report_daily_collection.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
