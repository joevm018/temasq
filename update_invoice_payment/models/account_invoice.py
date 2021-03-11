# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    payment_ids = fields.One2many('account.payment', compute="_compute_payment_ids", string='Payments')

    @api.one
    def _compute_payment_ids(self):
        self.payment_ids = self.env["account.payment"].search([("invoice_ids", "=", self.id)])

    @api.multi
    def modify_invoice(self):
        moves = self.env['account.move']
        for inv in self:
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_move_line_ids:
                raise UserError(_('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))
        self.write({'state': 'draft', 'date': False, 'move_id': False})
        if not self.journal_id.update_posted:
            self.journal_id.write({'update_posted': True})
        if moves:
            moves.button_cancel()
            moves.unlink()
