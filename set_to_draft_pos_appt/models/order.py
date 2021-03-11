from odoo import api, fields, models,_
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = "pos.order"

    def do_invoice_cancel(self, appt_invoice_id, appt):
        if appt_invoice_id.state == 'draft':
            appt_invoice_id.write({'move_name': False})
        if appt_invoice_id.state == 'open' and not appt_invoice_id.payment_ids:
            appt_invoice_id.modify_invoice()
        if appt_invoice_id.state == 'open' and appt_invoice_id.payment_ids:
            for paymt in appt_invoice_id.payment_ids:
                if not paymt.journal_id.update_posted:
                    paymt.journal_id.write({'update_posted': True})
                paymt.cancel()
            appt_invoice_id.modify_invoice()
        if appt_invoice_id.state == 'cancel':
            appt_invoice_id.action_invoice_draft()
        if appt_invoice_id.state == 'paid':
            for paymt in appt_invoice_id.payment_ids:
                if not paymt.journal_id.update_posted:
                    paymt.journal_id.write({'update_posted': True})
                paymt.cancel()
            appt_invoice_id.modify_invoice()
        appt_invoice_id.write({'state': 'draft', 'move_name': False})
        for paymt in appt_invoice_id.payment_ids:
            if not paymt.journal_id.update_posted:
                paymt.journal_id.write({'update_posted': True})
            paymt.cancel()
        appt_invoice_id.action_invoice_cancel()

    @api.multi
    def _create_returns(self, res):
        product_return_moves = res['product_return_moves']
        picking = res['picking_id']
        location_id = res['location_id']
        return_moves = []
        for p_return_moves in product_return_moves:
            return_moves.append(self.env['stock.move'].browse(p_return_moves[2]['move_id']))
        unreserve_moves = self.env['stock.move']
        for move in return_moves:
            to_check_moves = self.env['stock.move'] | move.move_dest_id
            while to_check_moves:
                current_move = to_check_moves[-1]
                to_check_moves = to_check_moves[:-1]
                if current_move.state not in ('done', 'cancel') and current_move.reserved_quant_ids:
                    unreserve_moves |= current_move
                split_move_ids = self.env['stock.move'].search([('split_from', '=', current_move.id)])
                to_check_moves |= split_move_ids
        if unreserve_moves:
            unreserve_moves.do_unreserve()
            # break the link between moves in order to be able to fix them later if needed
            unreserve_moves.write({'move_orig_ids': False})

        # create new picking for returned products
        picking_type_id = picking.picking_type_id.return_picking_type_id.id or picking.picking_type_id.id
        new_picking = picking.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': picking.name,
            'location_id': picking.location_dest_id.id,
            'location_dest_id': location_id})
        new_picking.message_post_with_view('mail.message_origin_link',
                                           values={'self': new_picking, 'origin': picking},
                                           subtype_id=self.env.ref('mail.mt_note').id)

        returned_lines = 0
        for return_line in product_return_moves:
            return_line_move_id = self.env['stock.move'].browse(return_line[2]['move_id'])
            if not return_line_move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed"))
            new_qty = return_line[2]['quantity']
            if new_qty:
                # The return of a return should be linked with the original's destination move if it was not cancelled
                if return_line_move_id.origin_returned_move_id.move_dest_id.id and return_line_move_id.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = return_line_move_id.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False

                returned_lines += 1
                return_line_move_id.copy({
                    'product_id': return_line[2]['product_id'],
                    'product_uom_qty': new_qty,
                    'picking_id': new_picking.id,
                    'state': 'draft',
                    'location_id': return_line_move_id.location_dest_id.id,
                    'location_dest_id': location_id or return_line_move_id.location_id.id,
                    'picking_type_id': picking_type_id,
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                    'origin_returned_move_id': return_line_move_id.id,
                    'procure_method': 'make_to_stock',
                    'move_dest_id': move_dest_id,
                })

        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))
        new_picking.action_confirm()
        new_picking.action_assign()
        new_picking.force_assign()
        PosorderLine = self.env['pos.order.line']
        stock_lot_obj = self.env['stock.pack.operation.lot']
        for pack_operation in new_picking.pack_operation_product_ids:
            qty_done = 0
            if pack_operation.pack_lot_ids:
                for each in pack_operation.pack_lot_ids:
                    pos_pack_lots = PosorderLine.search([('order_id', '=', self.id),
                                                         ('lot_id', '=', each.lot_id.id)])
                    qty = 0
                    for p in pos_pack_lots:
                        qty += p.qty
                    each.qty = qty
                    qty_done += qty
            else:
                if pack_operation.product_id.tracking == 'lot':
                    pos_pack_lots = PosorderLine.search([('order_id', '=', self.id),
                                                         ('product_id', '=', pack_operation.product_id.id)])
                    prdt_dict = {}
                    for p in pos_pack_lots:
                        if p.lot_id.id not in prdt_dict.keys():
                            prdt_dict[p.lot_id.id] = p.qty
                        else:
                            prdt_dict[p.lot_id.id] += p.qty
                    for item in prdt_dict:
                        stock_lot_obj.create({'operation_id': pack_operation.id,
                                              'lot_id': item,
                                              'qty':prdt_dict[item]})

                else:
                    qty_done = pack_operation.product_qty
            pack_operation.qty_done = qty_done
        new_picking.action_done()
        return new_picking.id, picking_type_id

    def create_returns(self, res):
        for wizard in self:
            new_picking_id, pick_type_id = wizard._create_returns(res)
            return new_picking_id

    def pos_delivery_cancel(self, picking):
        if picking.state != 'done':
            picking.action_cancel()
        else:
            res = {}
            Quant = self.env['stock.quant']
            move_dest_exists = False
            product_return_moves = []
            res.update({'picking_id': picking})
            for move in picking.move_lines:
                if move.scrapped:
                    continue
                if move.move_dest_id:
                    move_dest_exists = True
                # Sum the quants in that location that can be returned (they should have been moved by the moves that were included in the returned picking)
                quantity = sum(quant.qty for quant in Quant.search([
                    ('history_ids', 'in', move.id),
                    ('qty', '>', 0.0)
                ]).filtered(
                    lambda quant: not quant.reservation_id or quant.reservation_id.origin_returned_move_id != move)
                )
                quantity = move.product_id.uom_id._compute_quantity(quantity, move.product_uom)
                product_return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': quantity, 'move_id': move.id}))

            if not product_return_moves:
                raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)!"))
            res.update({'product_return_moves': product_return_moves})
            res.update({'move_dest_exists': move_dest_exists})
            if picking.location_id.usage == 'internal':
                res.update({'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
            res.update({'original_location_id': picking.location_id.id})
            location_id = picking.location_id.id
            if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
            res['location_id'] = location_id
            self.create_returns(res)

    @api.multi
    def action_set_to_draft(self):
        for order in self:
            # Delete all Payments
            for statement in order.statement_ids:
                # If Appt in invoiced state + Session validated and posted (payment with journal entry)
                if statement.journal_entry_ids or statement.move_name:
                    raise UserError('Related session is already posted and validated. So cant perform this operation.')
                statement.unlink()
            # Delete related Invoice if exists :If Appt in invoiced state + Session not validated and posted (payment without journal entry)
            if order.invoice_id:
                if order.invoice_id.number:
                    credit_note = self.env['account.invoice'].search([('origin', '=', order.invoice_id.number)])
                    for c_note in credit_note:
                        self.do_invoice_cancel(c_note, order)
                self.do_invoice_cancel(order.invoice_id, order)
                order.write({'invoice_id': False})
            if order.picking_id:
                self.pos_delivery_cancel(order.picking_id)
                order.write({'picking_id': False})
            if not order.invoice_id and not order.statement_ids and not order.picking_id:
                order.write({'state': 'draft'})