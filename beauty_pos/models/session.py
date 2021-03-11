from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class PosSession(models.Model):
    _inherit = "pos.session"

    def _confirm_orders(self):
        for session in self:
            company_id = session.config_id.journal_id.company_id.id
            orders = session.order_ids.filtered(lambda order: order.state == 'paid')
            journal_id = self.env['ir.config_parameter'].sudo().get_param(
                'pos.closing.journal_id_%s' % company_id, default=session.config_id.journal_id.id)
            if not journal_id:
                raise UserError(_("You have to set a Sale Journal for the POS:%s") % (session.config_id.name,))

            move = self.env['pos.order'].with_context(force_company=company_id)._create_account_move(session.start_at, session.name, int(journal_id), company_id)
            orders.with_context(force_company=company_id)._create_account_move_line(session, move)
            for order in session.order_ids.filtered(lambda o: o.state not in ['cancel', 'draft','done', 'invoiced']):
                if order.state not in ('paid'):
                    raise UserError(_("You cannot confirm all orders of this session, because they have not the 'paid' status"))
                order.action_pos_order_done()
            orders = session.order_ids.filtered(lambda order: order.state in ['invoiced', 'done'])
            orders.sudo()._reconcile_payments()

