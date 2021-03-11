from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_cash = fields.Boolean("Is Cash Account")