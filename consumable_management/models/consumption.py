# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp


class ConsumptionRecord(models.Model):
    _name = "consumption.record"
    _description = "Consumption Record"

    name = fields.Char('Name', default='NEW')
    product_id = fields.Many2one('product.product', 'Product', domain="[('type', '=', 'consu')]", required=True,
                                 readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Template', required=True, readonly=True)
    product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count',
                                           readonly=True)
    new_quantity = fields.Float('Quantity', default=1,
                                digits=dp.get_precision('Product Unit of Measure'), required=True, readonly=True,
                                help='This quantity is expressed in the Default Unit of Measure of the product.')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
                             domain="[('product_id','=',product_id)]", readonly=True)
    location_id = fields.Many2one('stock.location', 'Location', required=True,
                                  domain="[('usage', '=', 'internal')]", readonly=True)
    barcode = fields.Char(
        'Barcode', copy=False, oldname='ean13',
        help="International Article Number used for product identification.", readonly=True)
    staff_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    user_id = fields.Many2one('res.users', 'Responsible Person', readonly=True)
    inventory_id = fields.Many2one('stock.inventory', 'Inventory', readonly=True)
    note = fields.Text('Notes')
    date = fields.Date("Date", default=fields.Date.context_today)


