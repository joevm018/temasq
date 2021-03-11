# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_pay_later = fields.Boolean()
