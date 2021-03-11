from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class ProductPromotion(models.Model):
    _name = "product.promotion"

    name = fields.Char('Promotion Code', required=True)
    active = fields.Boolean(default=True)
    promotion_start_date = fields.Date('Valid From', required=True)
    promotion_end_date = fields.Date('Valid Until', required=True)
    compute_promo_valid = fields.Boolean('Promotion Compute active', compute='_get_promo_validity_update')
    promo_line_ids = fields.One2many('product.promotion.line', 'promotion_id', string='Lines')

    @api.multi
    # @api.depends('promotion_start_date', 'promotion_end_date')
    def _get_promo_validity_update(self):
        for promot in self:
            today_date = datetime.utcnow().date()
            if promot.promotion_start_date and promot.promotion_end_date:
                promotion_start_date = datetime.strptime(str(promot.promotion_start_date), '%Y-%m-%d').date()
                promotion_end_date = datetime.strptime(str(promot.promotion_end_date), '%Y-%m-%d').date()
                if promotion_start_date <= today_date <= promotion_end_date:
                    promot.active = True
                    promot.compute_promo_valid = True
                    promot.write({'active': True,'compute_promo_valid': True})
                else:
                    promot.active = False
                    promot.compute_promo_valid = False
                    promot.write({'active': False, 'compute_promo_valid': False})


class ProductPromotionLine(models.Model):
    _name = "product.promotion.line"

    promotion_id = fields.Many2one('product.promotion', string='Promotion')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    discount_percent = fields.Float(string='Discount(%)', default=0.0)

    @api.onchange('discount_percent')
    def change_discount_percent(self):
        if self.discount_percent>100:
            self.discount_percent = 0.0
            return {
                'warning': {'title': _('Warning'), 'message': _('Percentage cannot be greater than 100'), },
            }
