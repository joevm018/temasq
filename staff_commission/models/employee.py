from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    commission_ids = fields.One2many('commission.slab', 'employee_id', 'Commission details')
