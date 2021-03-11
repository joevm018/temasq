# -*- coding: utf-8 -*-
{
    'name': "Calendar Scheduler",

    'summary': 'Calendar Scheduler View',

    'sequence': 2,

    'description': """ """,

    'author': "",
    'website': "",

    'category': 'Uncategorized',
    'version': '10.0.1.0.0',

    'depends': [
        'web',
        'base',
        'web_calendar',
        'beauty_pos',
        'beauty_soft',
        'customer_dob',
    ],

    'data': [
        'views/res_config_settings_views.xml',
        'views/pos_order.xml',
        'views/calendar.xml',
        'views/saloon_scheduler.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],

    'demo': [],
    'application': True,
}
