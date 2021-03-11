{
    'name': 'POS Receipt print organique',
    'version': '11.0.1.0.0',
    'summary': 'POS Receipt print',
    'description': """
       
        \n      
            """,
    'category': 'Point of Sale',
    'sequence': 1,
    'author': 'Al Kidhma Group',
    'website': '',
    'depends': [ 'pos_staff', 'beauty_pos'],
    'data': [
        'reports/receipt_order_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'qweb': ['static/src/xml/report_receipt.xml'],
}
