# -*- coding: utf-8 -*-
from odoo import models, fields


class SupplierCost(models.Model):
    _name = 'supplier.cost'

    product_id = fields.Many2one('product.product', 'Product')
    name = fields.Many2one('res.partner', 'Supplier', domain=[('supplier', '=', True)], required=True)
    cost = fields.Float('Cost')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        index=True, ondelete='cascade', oldname='product_id')


class ProductProduct(models.Model):
    _inherit = 'product.template'

    supplier_ids = fields.One2many('supplier.cost', 'product_tmpl_id', string='Suppliers')
