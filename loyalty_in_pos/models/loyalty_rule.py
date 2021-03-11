# -*- coding: utf-8 -*-
from odoo import fields, models


class LoyaltyRule(models.Model):
    _name = 'loyalty.rule'

    name = fields.Char(string='Rule Name', size=32, index=True, required=True)
    type = fields.Selection(selection=[('product', 'Product'),
                                       ('category', 'Category')],
                            string='Type', required=True, default='product',
                            help='The concept this rule applies to')
    cumulative = fields.Boolean(help='The points from this rule will be added '
                                     'to points won from other rules with '
                                     'the same concept')
    pp_product = fields.Float(string='Points per product',
                              help='Amount of points earned per product')
    pp_currency = fields.Float(string='Points per currency',
                               help='Amount of points earned per currency')
    loyalty_program_id = fields.Many2one(comodel_name='loyalty.program',
                                         string='Loyalty Program',
                                         help='The Loyalty Program this rule '
                                              'belongs to')
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Target Product',
                                 help='The product affected by this rule')
    category_id = fields.Many2one(comodel_name='pos.category',
                                  string='Target Category',
                                  help='The category affected by this rule')
