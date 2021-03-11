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
    'name': 'Ssquared Consent Management',
    'version': '10.0',
    'category': 'Generic Modules/Others',
    'sequence': 2,
    'summary': 'Manage Reporting',
    'description': """
Ssquared Consent Management
    """,
    'author': 'Al Kidhma Group',
    'depends': ['beauty_pos', 'web_widget_digitized_signature'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'reports/reports.xml',
        'views/template.xml',
        'views/consent_form_view.xml',
        'views/customer.xml',
        'wizard/consent_facial.xml',
        'wizard/consent_hair_spa.xml',
        'wizard/consent_hair_color.xml',
        'wizard/consent_hair_treatment.xml',
        'wizard/consent_hammam.xml',
        'wizard/consent_massage.xml',
        'wizard/consent_lashes.xml',
        'wizard/consent_tips.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
