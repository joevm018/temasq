from datetime import datetime, timedelta
from odoo import api, fields, models


class DateWizard(models.TransientModel):
    _name = 'session.date'

    type = fields.Selection([('book', 'Book'),
                             ('done', 'done')],
                            string='Type')
    date = fields.Datetime('Done On', required=True, default=fields.Datetime.now)
    staff_ids = fields.Many2many('hr.employee', 'emp_session_rel', 'session_id', 'staff_id', 'Assigned Staff')

    def mark_book(self):
        act_id = self.env.context.get('active_ids', [])
        session_obj = self.env['combo.session'].search([('id', 'in', act_id)])
        staff = self.staff_ids.ids
        staff_id = False
        if staff:
            staff_id = staff[0]
        date_start = datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')
        duratn = 0
        if session_obj.product_id.type == 'service':
            if session_obj.product_id.duration_in_min:
                duratn = session_obj.product_id.duration_in_min
            else:
                duratn = 30
        date_stop = date_start + timedelta(minutes=duratn)
        line_data = [[0, 0, {'price_unit': 0, 'product_id': session_obj.product_id.id, 'checkin': False,
                             'procedure_start': self.date, 'procedure_stop': date_stop,
                             'staff_assigned_id': staff_id, 'combo_session_id': session_obj.id}]]
        data = {
            'partner_id': session_obj.customer_id.id,
            'date_order': self.date,
            'date_start': self.date,
            'date_stop': date_stop,
            'checkin': False,
            'lines': line_data
        }
        order_id = self.env['pos.order'].create(data)
        session_obj.write({'date': self.date, 'appointment_id': order_id.id, 'staff_ids': [(6, 0, staff)]})

    def confirm(self):
        act_id = self.env.context.get('active_ids', [])
        session_obj = self.env['combo.session'].search([('id', 'in', act_id)])
        staff = self.staff_ids.ids
        appt = False
        session_obj.write({'date': self.date, 'staff_ids': [(6, 0, staff)], 'state': 'done'})


class ComboSession(models.Model):
    _name = 'combo.session'

    name = fields.Char('Ref', default='New', readonly=True)
    order_id = fields.Many2one('pos.order', 'Order Ref', readonly=True)
    order_line_id = fields.Many2one('pos.order.line', 'Order Line Ref', readonly=True)
    customer_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    appointment_id = fields.Many2one('pos.order', 'Related Order', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    combo_id = fields.Many2one('product.product', 'Combo Pack', required=True, readonly=True)
    product_id = fields.Many2one('product.product', 'Item', required=True, readonly=True)
    staff_ids = fields.Many2many('hr.employee', 'employee_session_rel', 'session_id', 'employee_id', 'Assigned Staff',
                                 readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], string='Status',
                             index=True, readonly=True, copy=False, default='draft')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('combo.session')
        return super(ComboSession, self).create(vals)

    @api.multi
    def mark_book(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mark Booking',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'session.date',
            'target': 'new',
            'context': {'default_type': 'book'}
        }

    @api.multi
    def done(self):
        appt = False
        if self.appointment_id:
            appt = self.appointment_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mark session as Done',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'session.date',
            'target': 'new',
            'context': {'default_appointment_id': appt, 'default_type': 'done'}
        }

    @api.multi
    def undone(self):
        for i in self:
            i.write({'date': False, 'staff_ids': [(6, 0, [])], 'state': 'draft'})
