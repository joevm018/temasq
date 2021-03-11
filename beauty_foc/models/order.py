from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class PosOrder(models.Model):
    _inherit = "pos.order"

    is_order_foc = fields.Boolean(string='Is FOC')

    @api.multi
    def action_set_to_paid(self):
        # if not self.is_order_foc:
        #     raise UserError('You can only set FOC Orders to Paid without any Payment')
        if self.state != 'draft':
            raise UserError('Only Draft appointments can set to Paid')
        self.state = 'paid'
        self.cashier_name = self.env.user.id
        self.action_pos_order_paid()

    @api.onchange('is_order_foc')
    def onchange_is_order_foc(self):
        for order in self:
            if order.is_order_foc:
                order.discount_percent = 100
            else:
                order.discount_percent = 0


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    is_order_line_foc = fields.Boolean(string='Is FOC')

    @api.onchange('is_order_line_foc')
    def onchange_is_order_line_foc(self):
        for order in self:
            if order.is_order_line_foc:
                order.discount = 100
            else:
                order.discount = 0
