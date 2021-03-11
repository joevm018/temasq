from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def unlink(self):
        for product in self:
            if self.env.ref('discount_gift_card.product_product_discount_gift_card').id == product.id:
                raise UserError(_("You cannot delete Discount Gift Card ."))
        res = super(ProductProduct, self).unlink()
        return res


