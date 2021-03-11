# -*- coding: utf-8 -*-
{
    'name': "POS Dashboard",
    'version': '1.0.1',
    'category': 'Point Of Sale',
    'sequence': 21,
    'author': "Al Kidhma Group",
    'website': "http://www.alkidhmagroup.com",

    'summary': """
        Customized dashboard for point of sale
        """,

    'description': """
POS Dashboard
===========================

This is customized dashboard for point of sale.
It is compatible with all PC tablets and the iPad.
It will gives you an at-a-glance overview of the pos sales
    """,

    'depends': ['point_of_sale'],
    'data': [
        'views/pos_deshboard.xml',
        'views/pos_order_view.xml',
        'views/pos_config_view.xml',
    ]
}
