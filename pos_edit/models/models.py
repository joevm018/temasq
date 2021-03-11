# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosSessionInherited(models.Model):
    _inherit = 'pos.session'
    start_at = fields.Datetime(string='Opening', readonly=True, states={'opening_control': [('readonly', False)]})
    stop_at = fields.Datetime(string='Closing', readonly=False, copy=False, states={'closed': [('readonly', True)]})

    @api.multi
    def action_pos_session_closing_control(self):
        for session in self:
            for statement in session.statement_ids:
                if (statement != session.cash_register_id) and (statement.balance_end != statement.balance_end_real):
                    statement.write({'balance_end_real': statement.balance_end})
            #DO NOT FORWARD-PORT
            if session.state == 'closing_control':
                session.action_pos_session_close()
                continue
            if session.stop_at:
                session.write({'state': 'closing_control'})
            else:
                session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            if not session.config_id.cash_control:
                session.action_pos_session_close()


class PosOrderInherited(models.Model):
    _inherit = "pos.order"

    date_order = fields.Datetime(string='Order Date', index=True, default=fields.Datetime.now)
    lines = fields.One2many('pos.order.line', 'order_id', string='Order Lines', readonly=False, copy=True)
