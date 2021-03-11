# -*- coding: utf-8 -*-
{
    'name': "beauty_soft",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Al Kidhma Group",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','sale', 'stock', 'web_tree_image', 'point_of_sale', 'mail'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'views/res_config_view.xml',
        'views/views.xml',
        'views/menu.xml',
        'views/staff.xml',
        'views/item_master.xml',
        'views/sales_order.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}