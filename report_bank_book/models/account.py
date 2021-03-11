from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_bank = fields.Boolean("Is Bank Account")