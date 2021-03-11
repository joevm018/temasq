# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def update_payment(self):
        contextt = {}
        contextt['default_payment_id'] = self.id
        contextt['default_amount'] = self.amount
        contextt['default_journal_id'] = self.journal_id.id
        return {
            'name': _('Update Payment'),
            'view_id': self.env.ref('update_invoice_payment.view_update_wizard_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'update.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': contextt
        }

    @api.multi
    def delete_payment(self):
        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        if not self.journal_id.update_posted:
            self.journal_id.write({'update_posted': True})
        self.cancel()
        self._cr.execute('delete from update_wizard WHERE payment_id=%s', ([self.id]))
        self._cr.execute('delete from account_payment WHERE id=%s', ([self.id]))
