# -*- coding: utf-8 -*-
{
    'name': 'POS Session Privilege',
    'version': '10.0',
    'category': 'Point of Sale',
    'sequence': 2,
    'summary': 'Manage Salon Session Privilege',
    'description': """
    """,
    'author': 'Al Kidhma Group',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_config.xml',
        'security/config_security.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
