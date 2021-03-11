# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def print_journal(self):
        return self.env['report'].get_action(self.id, 'print_journal_entry.report_journal_entry')
