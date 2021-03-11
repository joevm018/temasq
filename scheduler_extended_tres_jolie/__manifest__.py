# -*- coding: utf-8 -*-
{
    'name': "Calendar Scheduler Extended Tres Jolie",

    'summary': 'Calendar Scheduler View Extended',

    'sequence': 2,

    'description': """Extends the functionalities of calendar scheduler""",

    'author': "",
    'website': "",

    'category': 'Uncategorized',
    'version': '10.0.1.0.0',

    'depends': [
        'calendar_scheduler',
        'combo_packs_management'
    ],

    'data': [
        'views/templates.xml',
        'views/scheduler.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],

    'demo': [],
    'application': True,
}
