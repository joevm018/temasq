from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    password = fields.Char(copy=False)
