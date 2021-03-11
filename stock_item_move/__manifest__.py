# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################


{
    'name': 'Stock item Moves',
    'version': '1.0',
    'category': 'Stock',
    'summary': 'Stock item Moves',
    'description': """
	Stock item Moves
    
	""",
    'author': ' Al Kidhma Group',
    'website': '',
    'depends': [  'base', 'web','stock','point_of_sale',
        'beauty_soft','product_expiry_alert','beauty_pos'
    ],
    'data': [
        'views/stock_item_move_view.xml',
        'report/itemmove_report_template.xml',
    ],
    'demo': [
    ],
    'test': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
