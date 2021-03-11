# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ComboSession(models.Model):
    _inherit = 'combo.session'

    @api.model
    def search_read_session(self, s_domain, s_fields):
        sessions = self.search_read(domain=s_domain, fields=s_fields)
        s_ids = [i['id'] for i in sessions]
        booked = self.env['pos.order.line'].search(
            [('combo_session_id', 'in', s_ids)])
        booked = booked and booked.mapped('combo_session_id').ids or []
        available_sessions = []
        for s in sessions:
            if s['id'] not in booked:
                available_sessions.append(s)
        return available_sessions


class PosOrderLineSession(models.Model):
    _inherit = "pos.order.line"

    is_last_session = fields.Boolean(compute='check_is_last_session')

    def check_is_last_session(self):
        for rec in self:
            is_last_session = False
            if rec.partner_id:
                sessions = self.env['combo.session'].search([
                    ('customer_id', '=', rec.partner_id.id)],
                    order="date desc")
                if sessions:
                    # sessions found for this customer
                    # check for draft sessions
                    booked = self.search([
                        ('combo_session_id', '=', sessions.ids)])
                    booked = booked and booked.mapped(
                        "combo_session_id").ids or []
                    draft_sessions = sessions.filtered(
                        lambda s: s.state == 'draft' and s.id not in booked)
                    if len(draft_sessions) == 0:
                        # no draft session present
                        is_last_session = (sessions[0].id == rec.combo_session_id.id) and True or False
            rec.is_last_session = is_last_session

    def action_view_appointment(self):
        return {
            'type': "ir.actions.act_window",
            'res_model': "pos.order",
            'res_id': self.order_id.id,
            'view_type': "form",
            'view_mode': "form",
            'name': "Appointment"
        }

    def apply_confirm(self):
        return self.order_id.apply_confirm()

    def action_cancel_appt(self):
        return self.order_id.action_cancel_appt()

    def action_check_in(self):
        return self.order_id.action_check_in()

    @api.multi
    def get_formview_id(self):
        view_id = False
        if self._context.get('view_origin') == "scheduler_state_map":
            # action originated from scheduler on mouse right click of appt
            view_id = self.env.ref(
                'scheduler_extended_tres_jolie.appointment_scheduler_wizard',
                raise_if_not_found=False)
        return view_id and view_id.id or super(
            PosOrderLineSession, self).get_formview_id()


class PosOrderSession(models.Model):
    _inherit = "pos.order"

    @api.multi
    def write(self, vals):
        res = super(PosOrderSession, self).write(vals)
        if vals.get('state', "") == "paid":
            self.update_session_lines()
        return res

    def update_session_lines(self):
        """Mark session lines as done"""
        for line in self.lines.filtered(lambda l: l.combo_session_id):
            line.combo_session_id.write({
                'date': self.date_order,
                'staff_ids': [(4, line.staff_assigned_id.id)],
                'state': 'done'
            })
        return
