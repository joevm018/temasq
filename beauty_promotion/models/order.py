from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    is_order_line_promotion = fields.Boolean(string='Applied Promotion', readonly=True)
    promotion_line_id = fields.Many2one('product.promotion.line', string='Applied Promotion line', readonly=True)
    promotion_id = fields.Many2one('product.promotion', string='Applied Promotion', readonly=True)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.multi
    def apply_promotion(self):
        return {
            'name': _('Apply promotion'),
            'view_id': self.env.ref('beauty_promotion.view_apply_promotion_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'apply.promotion.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }