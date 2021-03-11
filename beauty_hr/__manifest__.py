# -*- coding: utf-8 -*-
{
    'name': "Beauty HR",
    'summary': """Beauty HR""",
    'description': """""",
    'author': "Al Kidhma Group",
    'website': "",
    'category': '',
    'version': '0.1',
    'depends': ['base', 'hr', 'web_notify', 'beauty_soft'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'report/employee_list_report.xml',
        'wizard/report_employee.xml',
        'views/hr_employee.xml',
    ],
    'demo': [],
    'sequence': 1,
}
