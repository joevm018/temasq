# -*- coding: utf-8 -*-

{
    'name': 'VIP Treatment in POS Tres Jolie',
    'version': '9.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'VIP Treatment in the Point of Sale(Percentage) ',
    'author': 'Al Kidhma Group',
    'company': 'Al Kidhma Group',
    'images': [],
    'website': '',
    'depends': ['discounts_in_pos', 'pos_daily_report', 'pos_staff'],
    'data': [
        'templates.xml',
        'views/pos_view.xml',
        # 'reports/order_report_template.xml',
        'reports/report_partner_details.xml',
        'reports/report_saledetails.xml',
        'reports/monthly_report.xml',
    ],
    'qweb': [
        'static/src/xml/vip_treatment.xml'
        ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}

