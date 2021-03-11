from odoo import api, fields, models, tools, _


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.multi
    def print_rosa_receipt(self):
        return self.env['report'].get_action(self.id, 'receipt_rosabella.report_pos_deposit_receipt')
