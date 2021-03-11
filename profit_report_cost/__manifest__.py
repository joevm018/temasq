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
    'name': 'Cost in Profit Report Rosabella',
    'version': '10.0',
    'category': 'Products',
    'sequence': 2,
    'summary': 'Profit Report',
    'description': """Profit Report""",
    'author': 'Al Kidhma Group',
    'depends': ['beauty_pos', 'pos_expense'],
    'data': [
        'report/report_profit.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
