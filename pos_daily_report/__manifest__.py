# -*- coding: utf-8 -*-
{
    'name': 'POS DAILY REPORT',
    'version': '10.0.1.0.0',
    'category': 'account',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
                'beauty_pos',
                ],
    'data': [
        'views/order.xml',
        'views/res_company.xml',
        'wizard/partner_details.xml',
        'reports/reports.xml',
        'reports/report_partner_details.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
