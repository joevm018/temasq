from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class PosOrder(models.Model):
    _inherit = "pos.order"

    make_advance_visible = fields.Boolean(string="Show for Advance", compute='_make_advance_visible')

    @api.depends('statement_ids')
    def _make_advance_visible(self):
        for order in self:
            advance = any([pay_lines.is_advance for pay_lines in order.statement_ids])
            if advance:
                order.make_advance_visible = True
            else:
                order.make_advance_visible = False

    @api.multi
    def print_deposit_receipt(self):
        return self.env['report'].get_action(self.id, 'deposit_receipt_zaza.report_pos_deposit_receipt')\

    @api.multi
    def print_deposit_receipt_small(self):
        return self.env['report'].get_action(self.id, 'deposit_receipt_zaza.report_pos_deposit_receipt_small')