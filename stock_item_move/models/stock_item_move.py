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
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.osv import osv, orm
from odoo import SUPERUSER_ID, workflow, models, fields

class StockPicking(models.Model):
    _inherit = "stock.picking"


    staff_id = fields.Many2one('hr.employee', string='Staff')
    is_internal_transfer = fields.Boolean('IS Internal Transfer',defaut = False, compute='_compute_is_internal_transfer',store = True)

    @api.depends('picking_type_id')
    def _compute_is_internal_transfer(self):
        for move in self:
            if move.picking_type_id.id == 5:
                move.is_internal_transfer = True
