from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class UpdateWizard(models.TransientModel):
    _name = 'update.wizard'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary(string='Payment Amount', required=True)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    payment_id = fields.Many2one('account.payment', 'Payment', required=True)

    @api.multi
    def action_confirm(self):
        wizard_vals = self.read()[0]
        if wizard_vals['payment_id']:
            payment = self.env['account.payment'].browse(wizard_vals['payment_id'][0])
            if any(len(record.invoice_ids) != 1 for record in payment):
                # For multiple invoices, there is account.register.payments wizard
                raise UserError(_("This method should only be called to process a single invoice's payment."))
            journal = self.env['account.journal'].browse(wizard_vals['journal_id'][0])
            if not journal.update_posted:
                journal.write({'update_posted': True})
            payment.cancel()
            # payment.action_draft()
            payment.write({'state': 'draft', 'amount': wizard_vals['amount'], 'journal_id': wizard_vals['journal_id'][0]})
            payment.post()