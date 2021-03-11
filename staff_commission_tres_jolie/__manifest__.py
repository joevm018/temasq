# -*- coding: utf-8 -*-

##############################################################################
#
#    Author: Al Kidhma Group
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Slab wise Staff Commission Tres Jolie',
    'version': '10.0',
    'category': 'Generic Modules/Others',
    'sequence': 2,
    'summary': 'Manage Reporting',
    'description': """
Staff Commission Reports
    """,
    'author': 'Al Kidhma Group',
    'depends': ['beauty_pos', 'beauty_soft', 'beauty_hr', 'hr_payroll', 'staff_referral'],
    'data': [
        'security/ir.model.access.csv',
        'data/salary_rule_staff_commission.xml',
        'views/pos_config.xml',
        'views/employee.xml',
        'views/hr_payslip.xml',
        'wizard/staff_commission.xml',
        'report/report_staff_commission.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
