# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields, tools, _


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    with_expiry = fields.Boolean("With expiry Date ?", related='product_id.with_expiry')
