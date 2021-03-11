from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class ApplyPromotionWizard(models.TransientModel):
    _name = "apply.promotion.wizard"

    promotion_ids = fields.Many2many('product.promotion', string='Promotion', required=True)

    @api.multi
    def action_confirm(self):
        order = False
        active_id = self.env.context.get('active_id')
        if active_id:
            now_applied_promotion = False
            order = self.env['pos.order'].browse(active_id)
            for each_promotion in self.promotion_ids:
                for each_prom_line in  each_promotion.promo_line_ids:
                    for ord_line in order.lines:
                        # not_is_order_line_promotion = not ord_line.is_order_line_promotion
                        # if not_is_order_line_promotion:
                        if ord_line.product_id.id == each_prom_line.product_id.id:
                            if ord_line.price_unit:
                                now_applied_promotion = True
                                ord_line.write({
                                    'is_order_line_promotion': True,
                                    'discount': each_prom_line.discount_percent,
                                    'promotion_id': each_promotion.id,
                                    'promotion_line_id': each_prom_line.id,
                                })
                            else:
                                ord_line.write({
                                    'is_order_line_promotion': False,
                                    'discount': 0,
                                    'promotion_id': False,
                                    'promotion_line_id': False,
                                })
                            if order.test_paid():
                                order.action_pos_order_paid()
                                order.cashier_name = self.env.user.id
            # if not now_applied_promotion:
            #     raise UserError('No promotion to apply for this order')
