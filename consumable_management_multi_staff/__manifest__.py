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
    'name': 'Consumables Management Multi Staff Tres Joliee',
    'version': '10.0',
    'category': 'Point of Sale',
    'sequence': 2,
    'summary': 'Manage Salon Processing',
    'description': """
Advanced Consumables Management
==========================

This application enables you salon processing 
    """,
    'author': 'Al Kidhma Group',
    'depends': ['consumable_management'],
    'data': [
        'views/consumption.xml',
        'views/track_consumable_wizard.xml',
        'report/consumption_report_template.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
