from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import datetime


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    combo_session_id = fields.Many2one('combo.session', 'Session', readonly=True)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    have_combo = fields.Boolean('Have combo', compute='_get_combo')
    combo_session_ids = fields.One2many('combo.session', 'order_id',
                                        'Combo sessions')
    session_created = fields.Boolean(string="Session Created")

    @api.depends('combo_session_ids')
    def _get_combo(self):
        for i in self:
            if i.combo_session_ids:
                i.have_combo = True
            else:
                i.have_combo = False

    @api.multi
    def reverse(self):
        """Create a copy of order  for refund order"""
        res = super(PosOrder, self).reverse()
        for i in self.combo_session_ids:
            i.write({'state': 'cancel'})

    @api.multi
    def action_pos_order_paid(self):
        if not self.test_paid():
            raise UserError(_("Order is not paid."))
        self.write({'state': 'paid'})
        session_obj = self.env['combo.session']
        if self.partner_id:
            for line in self.lines:
                if line.combo_session_id:
                    line.combo_session_id.state = 'done'
                    line.combo_session_id.date = self.date_order
                if line.product_id.combo_pack and not self.session_created:
                    count = 0
                    vals = {
                        'order_id': self.id,
                        'order_line_id': line.id,
                        'customer_id': self.partner_id.id,
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
                    if self.combo_session_ids:
                        # marking as session created
                        self.session_created = True
        return self.create_picking()
