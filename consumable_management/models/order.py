# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools, _
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _force_picking_done(self, picking):
        """Force picking in order to be set as done."""
        self.ensure_one()
        contains_tracked_products = any([(product_id.tracking != 'none') for product_id in self.lines.mapped('product_id')])

        # do not reserve for tracked products, the user will have manually specified the serial/lot numbers
        if contains_tracked_products:
            picking.action_confirm()
        else:
            picking.action_assign()

        picking.force_assign()
        self.set_pack_operation_lot(picking)
        # if not contains_tracked_products:
        picking.action_done()

    # def action_pos_order_paid
    def create_picking(self):
        for current_order in self:
            for order in current_order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                if not order.lot_id:
                    product_id = order.product_id
                    if product_id and product_id.type != 'service' and product_id.tracking != 'none' \
                            and product_id.with_expiry == True:
                        available_lots = self.env['stock.production.lot'].search([('product_id','=', product_id.id)])
                        if not available_lots:
                            new_lot = self.env['stock.production.lot'].create({
                                'product_id': product_id.id,
                                'product_qty': order.qty,
                            })
                            order.lot_id = new_lot.id
                        else:
                            qty_less_slot_greater_qty = False
                            qty_less_slot_near_expiry_lot = False
                            near_expiry = False
                            near_expiry_lot = False
                            false_near_expiry_lot = False
                            for avail_lot in available_lots:
                                if avail_lot.life_date and order.qty <= avail_lot.product_qty:
                                    near_expiry = avail_lot.life_date
                                    near_expiry_lot = avail_lot
                                    break
                                if avail_lot.life_date and order.qty > avail_lot.product_qty:
                                    qty_less_slot_greater_qty = avail_lot.product_qty
                                    qty_less_slot_near_expiry_lot = avail_lot
                                    break
                                if not avail_lot.life_date and order.qty <= avail_lot.product_qty:
                                    false_near_expiry_lot = avail_lot
                            for avail_lot in available_lots:
                                if avail_lot.life_date and near_expiry > avail_lot.life_date and order.qty <= avail_lot.product_qty:
                                    near_expiry = avail_lot.life_date
                                    near_expiry_lot = avail_lot
                                if avail_lot.product_qty and qty_less_slot_greater_qty < avail_lot.product_qty\
                                        and order.qty > avail_lot.product_qty:
                                    qty_less_slot_greater_qty = avail_lot.product_qty
                                    qty_less_slot_near_expiry_lot = avail_lot
                            if not near_expiry_lot:
                                if false_near_expiry_lot:
                                    order.lot_id = false_near_expiry_lot.id
                                if qty_less_slot_near_expiry_lot and not order.lot_id:
                                    order.lot_id = qty_less_slot_near_expiry_lot.id
                                if available_lots and not qty_less_slot_near_expiry_lot:
                                    order.lot_id = available_lots[0]
                            if near_expiry_lot:
                                order.lot_id = near_expiry_lot.id
        res = super(PosOrder, self).create_picking()
        return res


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    lots_visible = fields.Boolean(compute='_compute_lots_visible')
    lot_id = fields.Many2one('stock.production.lot', 'Lot Ref')

    def create(self, vals):
        res = super(PosOrderLine, self).create(vals)
        if res.state == 'draft' and 'lot_id' in vals or 'qty' in vals:
            pos_lot_obj = self.env['pos.pack.operation.lot']
            for line in res:
                for i in line.pack_lot_ids:
                    i.unlink()
                if line.lot_id and line.product_id:
                    for each in range(int(abs(line.qty))):
                        lot_new = pos_lot_obj.create({
                            'pos_order_line_id': line.id,
                            'order_id': line.order_id.id,
                            'lot_name': line.lot_id.name,
                            'product_id': line.product_id.id})
        return res

    def write(self, vals):
        res = super(PosOrderLine, self).write(vals)
        if 'lot_id' in vals or 'qty' in vals:
            pos_lot_obj = self.env['pos.pack.operation.lot']
            for line in self:
                for i in line.pack_lot_ids:
                    i.unlink()
                if line.lot_id and line.product_id:
                    for each in range(int(abs(line.qty))):
                        lot_new = pos_lot_obj.create({
                            'pos_order_line_id': line.id,
                            'order_id': line.order_id.id,
                            'lot_name': line.lot_id.name,
                            'product_id': line.product_id.id})
        return res

    @api.onchange('product_id', 'qty')
    def onchange_pdt_lot(self):
        for order in self:
            order.lot_id = False
            product_id = order.product_id
            if product_id and product_id.type != 'service' and product_id.tracking != 'none' \
                    and product_id.with_expiry == True:
                available_lots = self.env['stock.production.lot'].search([('product_id','=', product_id.id)])
                if not available_lots:
                    # new_lot = self.env['stock.production.lot'].create({'product_id': product_id.id})
                    # print(new_lot,"----", new_lot.product_id)
                    # order.lot_id = new_lot.id
                    raise UserError('No lots available for this product')
                qty_less_slot_greater_qty = False
                qty_less_slot_near_expiry_lot = False
                near_expiry = False
                near_expiry_lot = False
                false_near_expiry_lot = False
                for avail_lot in available_lots:
                    if avail_lot.life_date and order.qty <= avail_lot.product_qty:
                        near_expiry = avail_lot.life_date
                        near_expiry_lot = avail_lot
                        break
                    if avail_lot.life_date and order.qty > avail_lot.product_qty:
                        qty_less_slot_greater_qty = avail_lot.product_qty
                        qty_less_slot_near_expiry_lot = avail_lot
                        break
                    if not avail_lot.life_date and order.qty <= avail_lot.product_qty:
                        false_near_expiry_lot = avail_lot
                for avail_lot in available_lots:
                    if avail_lot.life_date and near_expiry > avail_lot.life_date and order.qty <= avail_lot.product_qty:
                        near_expiry = avail_lot.life_date
                        near_expiry_lot = avail_lot
                    if avail_lot.product_qty and qty_less_slot_greater_qty < avail_lot.product_qty\
                            and order.qty > avail_lot.product_qty:
                        qty_less_slot_greater_qty = avail_lot.product_qty
                        qty_less_slot_near_expiry_lot = avail_lot
                if not near_expiry_lot:
                    if false_near_expiry_lot:
                        order.lot_id = false_near_expiry_lot.id
                    if qty_less_slot_near_expiry_lot and not order.lot_id:
                        order.lot_id = qty_less_slot_near_expiry_lot.id
                    if available_lots and not qty_less_slot_near_expiry_lot:
                        order.lot_id = available_lots[0]
                if near_expiry_lot:
                    order.lot_id = near_expiry_lot.id


    @api.one
    @api.depends('product_id')
    def _compute_lots_visible(self):
        if self.product_id:
            if self.product_id.type != 'service' and self.product_id.tracking != 'none' and self.product_id.with_expiry == True:
                self.lots_visible = True
            else:
                self.lots_visible = False
        else:
            self.lots_visible = False
