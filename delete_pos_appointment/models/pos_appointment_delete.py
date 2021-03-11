from odoo import api, fields, models,_
from odoo.exceptions import UserError


class PosAppointmentDelete(models.Model):
    _name = "pos.appointment.delete"

    date_from = fields.Datetime('From', required=True)
    date_to = fields.Datetime('To', required=True)

    @api.multi
    def cancel_archive_appointment(self):
        dom = [('date_order', '<=', self.date_to), ('date_order', '>=', self.date_from)]
        pos_orders = self.env['pos.order'].search(dom, order='date_order asc')
        for pos_ord in pos_orders:
            pos_ord.write({'state': 'cancel','active':False})

    @api.multi
    def cancel_appointment(self):
        dom = [('date_order', '<=', self.date_to), ('date_order', '>=', self.date_from)]
        pos_orders = self.env['pos.order'].search(dom, order='date_order asc')
        pos_orders.action_cancel_pos_appt()


class PosOrder(models.Model):
    _inherit = "pos.order"

    active = fields.Boolean(default=True)

    @api.multi
    def action_cancel_pos_appt(self):
        for order in self:
            for ord_line in order.lines:
                # if order.redeemed_gift_id:
                if order.redeemed_package_id:
                    session_avail = self.env['combo.session'].search(
                        [('order_line_id', '=',ord_line.id),
                         ('order_id', '=', ord_line.order_id.id)], limit=1)
                    ord_line.write({
                        'package_card_id': False,
                        'combo_session_id': session_avail.id,
                    })
                    session_avail.write({
                        'order_line_id': False,
                        'order_id': False,
                        'state': 'draft',
                        'redeemed_date': False,
                    })
                if order.purchased_gift_card_ids:
                    disc_gift_card_vals = {
                        'purchased_date': False,
                        'partner_id': False,
                        'gift_order_id': False,
                        'state': 'new',
                        'discount_gift_card_amount': 0.0,
                        'remaining_amount': 0.0,
                    }
                    order.purchased_gift_card_ids.write(disc_gift_card_vals)
                if order.purchased_package_card_ids:
                    package_card_vals = {
                        'purchased_date': False,
                        'partner_id': False,
                        'package_order_id': False,
                        'state': 'new',
                        'package_card_amount': 0.0,
                        'combo_session_ids': False,
                    }
                    order.purchased_package_card_ids.write(package_card_vals)
            if not order.invoice_id and not order.statement_ids and not order.picking_id:
                order.write({'state': 'cancel'})

