# -*- coding: utf-8 -*-
{
    'name': "Tmasq Receipt Print",

    'summary': """
        
        """,

    'description': """
        
    """,

    'author': "Al Khidma System",
    'website': "http://www.alkhidmasystems.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','beauty_pos'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}