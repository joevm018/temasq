from odoo import api, fields, models, tools, _
from datetime import datetime


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    change_order_date = fields.Boolean(default=True, string='Change Order date')
    new_order_date = fields.Datetime(default=fields.Datetime.now, string='Order date')

    @api.multi
    def check(self):
        self.ensure_one()
        res = super(PosMakePayment, self).check()
        if not self.is_advance:
            order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
            if self.change_order_date:
                order.write({'date_order': self.new_order_date})
        return res
