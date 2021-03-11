# -*- coding: utf-8 -*-

##############################################################################
#
#    Author: Al Kidhma Group Qatar
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
    'name': 'Multi Session Management',
    'version': '10.0',
    'category': 'Calendar',
    'sequence': 2,
    'summary': 'Manage Gym Processing',
    'description': """
Advanced Gym Management
==========================

This application enables you Gym processing 
    """,
    'author': 'Al Kidhma Group',
    'depends': ['calendar', 'hr'],
    'data': [
        'views/calendar_event.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
