from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class UpdateStandardPrice(models.TransientModel):
    _name = 'update.standard.price.wizard'
    _description = 'Update Standard Price'



    price_unit = fields.Float(string='Unit Price')
    current_price = fields.Float(string='Current Price',readonly = 1)


    @api.multi
    def update_price(self):

        invoice_line_obj = self.env['account.invoice.line'].browse(self.env.context.get('active_id', False))
        invoice_line_obj.write({
        						'price_unit' : self.price_unit
        						})

        pruchase_line_obj = invoice_line_obj.purchase_line_id
        pruchase_line_obj.write({
        							'price_unit':self.price_unit
        						})

