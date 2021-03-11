from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    @api.multi
    def type_cash(self):
        cash = self.session_id.config_id.journal_ids.filtered(lambda journal: journal.type == 'cash')
        if cash:
            self.journal_id = cash[0]
        if not cash:
            raise UserError('Please define Cash journal')
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def type_card(self):
        card = self.session_id.config_id.journal_ids.filtered(
            lambda journal: journal.type == 'bank' and not journal.is_pay_later)
        if card:
            self.journal_id = card[0]
        if not card:
            raise UserError('Please define Card journal')
        return {
            "type": "ir.actions.do_nothing",
        }
