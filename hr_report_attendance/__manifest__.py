# -*- coding: utf-8 -*-
{
    'name': 'HR Attendance Report',
    'version': '10.0.1.0.0',
    'summary': 'HR Management',
    'description': """        
        """,
    'category': 'Human Resources',
    'author': 'Al Kidhma Group',
    'website': "",
    'company': '',
    'depends': [
                'hr',
                'web_notify',
                'hr_attendance',
                'beauty_soft',
                'hr_zk_attendance',
                ],
    'data': [
        'views/hr_attendance.xml',
        'reports/reports.xml',
        'reports/report_attendance.xml',
        'wizard/report_attendance.xml',
        'data/cron.xml',
        'models/hr_config_settings.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
