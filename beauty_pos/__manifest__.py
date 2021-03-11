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
    'name': 'Salon Management',
    'version': '10.0',
    'category': 'Point of Sale',
    'sequence': 2,
    'summary': 'Manage Salon Processing',
    'description': """
Advanced Salon Management
==========================

This application enables you salon processing 
    """,
    'author': 'Al Kidhma Group',
    'depends': ['account', 'account_accountant', 'point_of_sale',
                'beauty_soft', 'pos_edit', 'web_timeline', 'web_notify', 'purchase', 'stock', 'mail', 'resource'],
    'data': [
        'security/access_group.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'wizard/change_orderdate_wizard.xml',
        'views/user_security.xml',
        'views/calendar_templates.xml',
        'views/order.xml',
        'views/purchase_order.xml',
        'views/product.xml',
        # 'views/staffwise_scheduler.xml',
        'views/payment.xml',
        'views/lot_view.xml',
        'views/product_label.xml',
        'reports/order_report_template.xml',
        'reports/appointment_report.xml',
        'reports/appointment_report_template.xml',
        'wizard/appointment_report_wizard.xml',
        'reports/checkin_report_template.xml',
        'reports/checkin_report.xml',
        'wizard/customer_checkin_report.xml',
        'reports/order_report.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
