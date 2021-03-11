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
from odoo.tools import amount_to_text_en


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def set_amt_in_worlds(self):
        amount_in_words = amount_to_text_en.amount_to_text(self.amount_total, lang='en', currency=self.currency_id.name)
        amount_in_words += '\tOnly'
        self.amt_in_words = amount_in_words

    amt_in_words = fields.Char(compute='set_amt_in_worlds')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if not self.price_unit and self.product_id:
            self.price_unit = self.product_id.standard_price
        return res

    
    update_cost_price = fields.Boolean(string="Update Cost Price?", default= True, help="Select to update cost price of product after confirming invoice")
     

class Account_Invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def update_standard_price(self):
        self.ensure_one()
        view_id = self.env.ref('beauty_purchase.update_standard_price_wizard').id
        return {
            'name': _('Update Price'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'update.standard.price.wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'context': {'default_current_price': self.price_unit},
            'target': 'new',
        }







class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):

        product_obj = self.env['product.product']
        # call the super methd here
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            if invoice.type in ('in_invoice', 'in_refund'):
                for line in invoice.invoice_line_ids:
                    if line.product_id and line.price_unit:
                        pr_id = product_obj.browse(line.product_id.id)
                        pr_id.write({'standard_price': line.price_unit})

        #return self.write({'state':'open'})
        return res