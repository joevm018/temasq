# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _


class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"
    _description = "Change Product Quantity"

    with_expiry = fields.Boolean("With expiry Date ?", compute='set_with_expiry')

    @api.depends('product_tmpl_id')
    def set_with_expiry(self):
        for pdt in self:
            if pdt.product_tmpl_id:
                if pdt.product_tmpl_id.with_expiry:
                    pdt.with_expiry = True
                else:
                    pdt.with_expiry = False
