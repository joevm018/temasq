from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class CommissionSlab(models.Model):
    _name = "target.slab"

    def default_commission_type(self):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.get_default(
            'pos.config.settings', "default_commission_type")
        return value and value or "fixed"

    achieved_from = fields.Integer('Achieved From(%)', required=True)
    achieved_to = fields.Integer('Achieved To(%)')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    commission_type = fields.Selection([
        ('fixed', 'Fixed'), ('percentage', 'Percentage')],
        string=_("Commission Type"),
        default=default_commission_type)
    commission = fields.Float('Commission(%)')
    commission_fixed = fields.Float(string=_("Commission(Fixed)"))

    @api.constrains('commission', 'achieved')
    def _check_commission(self):
        c_val = self.commission
        if c_val:
            if 0 > c_val or c_val > 100:
                raise ValidationError(_(
                    'Please enter Commission Percentage Properly !!!'))
