# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class StockMove(models.Model):
    _inherit = "stock.move"

    consumed = fields.Boolean('Is Consumed')


class TrackConsumableWizard(models.TransientModel):
    _name = "track.consumable.wizard"
    _description = "Change Product Quantity"

    product_id = fields.Many2one('product.product', 'Product', domain="[('type', '=', 'consu')]", required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Template', required=True)
    with_expiry = fields.Boolean("With expiry Date ?", compute='set_with_expiry')
    product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count')
    new_quantity = fields.Float(
        'Quantity', default=1,
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        help='This quantity is expressed in the Default Unit of Measure of the product.')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', domain="[('product_id','=',product_id)]")
    location_id = fields.Many2one('stock.location', 'Location', required=True, domain="[('usage', '=', 'internal')]")
    barcode = fields.Char(
        'Barcode', copy=False, oldname='ean13',
        help="International Article Number used for product identification.")
    staff_id = fields.Many2one('hr.employee', string='Employee')
    note = fields.Text('Notes')
    date = fields.Date("Date", default=fields.Date.context_today)

    @api.model
    def default_get(self, fields):
        res = super(TrackConsumableWizard, self).default_get(fields)
        if 'location_id' in fields and not res.get('location_id'):
            res['location_id'] = self.env.ref('stock.stock_location_stock').id
        return res

    @api.onchange('location_id', 'product_id')
    def onchange_location_id(self):
        if self.location_id and self.product_id:
            availability = self.product_id.with_context(compute_child=False)._product_available()
            self.new_quantity = availability[self.product_id.id]['qty_available']

    @api.onchange('barcode')
    def onchange_barcode(self):
        if self.barcode:
            search_pdt = self.env['product.product'].search([('barcode', '=', self.barcode)], limit=1)
            if search_pdt:
                self.product_id = search_pdt.id
            else:
                self.product_id = False
        else:
            self.product_id = False

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_tmpl_id = self.onchange_product_id_dict(self.product_id.id)['product_tmpl_id']

    @api.depends('product_tmpl_id')
    def set_with_expiry(self):
        for pdt in self:
            if pdt.product_tmpl_id:
                if pdt.product_tmpl_id.with_expiry:
                    pdt.with_expiry = True
                else:
                    pdt.with_expiry = False

    @api.multi
    def _prepare_inventory_line(self):
        product = self.product_id.with_context(location=self.location_id.id, lot_id=self.lot_id.id)
        dom = [('product_id', '=', product.id),
               ('location_id.usage', '=', 'internal')]
        if self.lot_id:
            dom.append(('lot_id', '=', self.lot_id.id))
        else:
            dom.append(('lot_id', '=', False))
        quant_obj = self.env['stock.quant'].search(dom)
        pdt_qty = 0
        for quant in quant_obj:
            if self.location_id == quant.location_id:
                pdt_qty += quant.qty
        th_qty = product.qty_available
        qty = 0
        if self.new_quantity:
            qty = self.new_quantity
        if pdt_qty < qty:
            raise UserError(_('Quantity on hand is %s units only. ') % pdt_qty)
        res = {
            'product_qty': pdt_qty - qty,
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'theoretical_qty': th_qty,
            'prod_lot_id': self.lot_id.id,
        }

        return res

    def onchange_product_id_dict(self, product_id):
        return {
            'product_tmpl_id': self.env['product.product'].browse(product_id).product_tmpl_id.id,
        }

    @api.multi
    def change_product_qty(self):
        """ Changes the Product Quantity by making a Physical Inventory. """
        Inventory = self.env['stock.inventory']
        consumption_obj = self.env['consumption.record']
        for wizard in self:
            product = wizard.product_id.with_context(location=wizard.location_id.id, lot_id=wizard.lot_id.id)
            line_data = wizard._prepare_inventory_line()

            if wizard.product_id.id and wizard.lot_id.id:
                inventory_filter = 'none'
            elif wizard.product_id.id:
                inventory_filter = 'product'
            else:
                inventory_filter = 'none'

            date_obj = datetime.strptime(wizard.date, DATE_FORMAT)
            date = date_obj.strftime("%Y-%m-%d 00:00:00")
            inventory = Inventory.create({
                'name': _('INV: %s') % tools.ustr(wizard.product_id.name),
                'filter': inventory_filter,
                'product_id': wizard.product_id.id,
                'location_id': wizard.location_id.id,
                'lot_id': wizard.lot_id.id,
                'date': date,
                'line_ids': [(0, 0, line_data)],
            })
            inventory.action_done()
            for i in inventory.move_ids:
                i.consumed = True
            consumption_obj.create({
                'name': self.env['ir.sequence'].next_by_code('consumption.record'),
                'product_id': wizard.product_id.id,
                'product_tmpl_id': wizard.product_tmpl_id.id,
                'product_variant_count': wizard.product_variant_count,
                'new_quantity': wizard.new_quantity,
                'lot_id': wizard.lot_id.id,
                'location_id': wizard.location_id.id,
                'barcode': wizard.barcode,
                'staff_id': wizard.staff_id.id,
                'user_id': self.env.uid,
                'note': wizard.note,
                'date': wizard.date,
                'inventory_id': inventory.id
            })
        return {'type': 'ir.actions.act_window_close'}
