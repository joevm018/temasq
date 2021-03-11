# -*- coding: utf-8 -*-
{
    'name': 'CASHIER TRANSACTION REPORT',
    'version': '10.0.1.0.0',
    'category': 'account',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
                'pos_daily_report',
                'discounts_in_pos',
                'discount_gift_card',
                ],
    'data': [
        'wizard/cashier_details.xml',
        'reports/reports.xml',
        'reports/report_cashier_transaction.xml',
        'reports/report_partner_details.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'sequence': 1,
    'application': True,
}
