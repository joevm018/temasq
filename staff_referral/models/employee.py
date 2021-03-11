from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    referral_percent = fields.Float('Referral Target')
