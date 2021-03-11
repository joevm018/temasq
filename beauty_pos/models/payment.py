from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    is_advance = fields.Boolean('Is Advance')


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    def _default_journal(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            session = self.env['pos.order'].browse(active_id).session_id
            cash = session.config_id.journal_ids.filtered(lambda journal: journal.type == 'cash')
            if cash:
                return cash[0]
            return session.config_id.journal_ids and session.config_id.journal_ids.ids[0] or False
        return False

    def _default_session(self):
        session = self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)
        if session:
            return session
        else:
            raise UserError(_("There is no open session right now. You have to open one session to make payment !!!"))

    journal_id = fields.Many2one('account.journal', string='Payment Mode', required=True, default=_default_journal)
    session_id = fields.Many2one(
        'pos.session', string='Session', required=True, index=True,
        domain="[('state', '=', 'opened')]", default=_default_session)

    is_advance = fields.Boolean('Is Advance ?', default=False)

    @api.multi
    def check(self):
        """Check the order:
        if the order is not paid: continue payment,
        if the order is paid print ticket.
        """
        if self.is_advance:
            if self.payment_name:
                self.payment_name = "ADVANCE"+ ":" + self.payment_name
            else:
                self.payment_name = "ADVANCE"
        self.ensure_one()
        order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        order.write({'session_id': self.session_id.id, 'cashier_name':self.env.user.id })
        res = super(PosMakePayment, self).check()
        for record in order.lines:
            if record.qty < 0:
                picking_id = order.picking_id
                move = self.env['stock.move'].search([('picking_id', '=', picking_id.id)])
                for rec in move:
                    rec.write({'is_return': True})
        if order.total_balance < 0:
            cash = self.session_id.config_id.journal_ids.filtered(lambda journal: journal.type == 'cash')
            journal_balance = self.journal_id.id
            if cash:
                journal_balance = cash.id
            wizard = self.env['pos.make.payment'].create({
                'session_id': self.session_id.id,
                'amount': order.total_balance,
                'journal_id': journal_balance,
                'payment_date': self.payment_date,
            })
            wizard.check()
            if order.test_paid():
                order.action_pos_order_paid()
                return {'type': 'ir.actions.act_window_close'}
        return res
