# -*- coding: utf-8 -*-
{
    'name': 'POS Loyalty',
    'version': '10.0.1.0.0',
    'category': 'Point of Sale',
    'license': 'AGPL-3',
     'author': 'Al Kidhma Group',
    'website': "",
    'depends': ['point_of_sale', 'beauty_pos'],

    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/reward_wizard_view.xml',
        'views/loyalty_program_view.xml',
        'views/loyalty_reward_view.xml',
        'views/loyalty_rule_view.xml',
        'views/pos_config_view.xml',
        'views/pos_order_view.xml',
        'views/res_partner_view.xml',
        'views/order_report_template.xml',
        'views/product.xml',
        'report/loyalty_report_template.xml',
        'report/loyalty_report.xml',
    ],

    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/custom_pos.xml',
    ],

    'installable': True,
}
