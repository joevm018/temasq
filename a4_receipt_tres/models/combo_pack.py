from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    @api.multi
    def check(self):
        self.ensure_one()
        order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        session_obj = self.env['combo.session']
        if order.partner_id:
            for line in order.lines:
                if line.product_id.combo_pack and not order.session_created:
                    session_order_lines =  session_obj.search([
                        ('order_line_id', '=', line.id)])
                    if not session_order_lines:
                        count = 0
                        vals = {
                            'order_id': order.id,
                            'order_line_id': line.id,
                            'customer_id': order.partner_id.id,
                            'combo_id': line.product_id.id,
                            'date': False,
                            'state': 'draft'
                        }
                        while count < line.qty:
                            for combo_line in line.product_id.pack_ids:
                                countt = 0
                                vals['product_id'] = combo_line.product_id.id
                                while countt < combo_line.count:
                                    session_obj.create(vals)
                                    countt += 1
                            count += 1
                    if order.combo_session_ids:
                        # marking as session created
                        order.session_created = True
        res = super(PosMakePayment, self).check()
        return res


class ComboSession(models.Model):
    _inherit = 'combo.session'

    total_paid = fields.Float(compute='_compute_amount_paid', string='Paid Amount', digits=0)
    total_balance = fields.Float(compute='_compute_amount_balance', string='Due Amount', digits=0)

    @api.depends('order_id.statement_ids')
    def _compute_amount_paid(self):
        for combo_session in self:
            combo_session.total_paid = sum(payment.amount for payment in combo_session.order_id.statement_ids)

    @api.depends('order_id.statement_ids')
    def _compute_amount_balance(self):
        for combo_session in self:
            combo_session.total_balance = combo_session.order_id.amount_total - combo_session.order_id.total_paid