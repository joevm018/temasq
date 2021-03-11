# -*- coding: utf-8 -*-
{
    'name': "pos_staff Lumiere",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Al Kidhma Group",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale', 'pos_daily_report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/staff_pos_view.xml',
        'views/report_saledetails.xml',
        'views/pos_details.xml',
        'views/daily_report.xml',
        'views/monthly_report.xml',
    ],
    'depends':['point_of_sale','product'],
    'qweb': ['static/src/xml/pos_staff.xml'],
}