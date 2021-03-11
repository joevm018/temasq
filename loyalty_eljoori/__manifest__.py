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
    'name': "Loyalty El Joori",
    'summary': """
        Loyalty El Joori""",
    'author': "Al Kidhma Group",
    'company': 'Al Kidhma Group',
    'website': 'http://www.alkidhmagroup.com',
    'version': '0.1',
    'depends': ['loyalty_in_pos'],
    # always loaded
    'data': [
        'views/res_partner.xml',
        'views/pos_order.xml',
        'views/order_report_template.xml',
        'wizard/loyalty_purchase.xml',
        'wizard/reward_wizard.xml',
        'wizard/swipe_card.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
