{
    'name': 'Expense Managament',
    'version': '11.0.1.0.0',
    'summary': 'POS Expense Managament',
    'description': """
       
        \n      
            """,
    'category': 'Accounting',
    'author': 'Al Kidhma Group',
    'website': '',
    'depends': ['base', 'account', 'account_accountant','account_voucher','pos_staff'],
    'data': [

        'data/expense_data.xml',
        'views/expense_views.xml',
        'wizard/profit_report_wizard.xml',
        'reports/reports.xml',
        'reports/report_profit_pos.xml',


    ],
    'installable': True,
    'auto_install': False,
}
