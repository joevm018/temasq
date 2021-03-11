# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountReportPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger"

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        return {
            'domain': {'partner_ids': self._domain_partner_ids()},
        }

    def _domain_partner_ids(self):
        domain = []
        if self:
            self.partner_ids = False
            if self.partner_type == 'Customer':
                domain = [('customer','=',True)]
            if self.partner_type == 'Vendor':
                domain = [('supplier','=',True)]
        return domain

    partner_type = fields.Selection(selection=[('Customer', 'Customer'), ('Vendor', 'Vendor')], string='Partner Type')
    partner_ids = fields.Many2many('res.partner', 'partner_ledger_partner_rel', 'id', 'partner_id', string='Partners',
                                    domain=_domain_partner_ids)

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'partner_ids': self.partner_ids.ids, 'partner_type': self.partner_type,
                             'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
        return self.env['report'].get_action(self, 'account.report_partnerledger', data=data)


