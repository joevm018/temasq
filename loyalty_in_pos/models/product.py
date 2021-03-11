# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductTemlate(models.Model):
    _inherit = 'product.template'

    rule_ids = fields.One2many('loyalty.rule', 'product_id', 'Loyalty Rule')
