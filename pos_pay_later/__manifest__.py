{
    'name': 'POS Pay Later',
    'version': '11.0.1.0.0',
    'summary': 'POS Pay Later',
    'description': """
       
        \n      
            """,
    'category': 'Point of Sale',
    'sequence': 1,
    'author': 'Al Kidhma Group',
    'website': '',
    'depends': ['base', 'account_accountant', 'point_of_sale', 'pos_daily_report', 'pos_staff'],
    'data': [
        # 'data/expense_data.xml',
        'views/pos_order.xml',
        'views/journal.xml',
        # 'wizard/profit_report_wizard.xml',
        # 'reports/reports.xml',
        # 'reports/report_profit_pos.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
