from odoo import api, fields, models


class CustStatementReportWizard(models.TransientModel):
    _name = "cust.statement.report"

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        return {
            'domain': {
                'partner_ids': self._domain_partner_ids(),
                'account_id': self._domain_account_id(),
            },
        }

    def _domain_partner_ids(self):
        domain = []
        if self:
            self.partner_ids = False
            if self.partner_type == 'Customer':
                domain = [('customer', '=', True)]
            if self.partner_type == 'Vendor':
                domain = [('supplier', '=', True)]
        return domain

    def _domain_account_id(self):
        domain = [('internal_type', 'in', ('receivable', 'payable'))]
        # if self:
        #     self.partner_ids = False
        #     if self.partner_type == 'Customer':
        #         domain = [('internal_type', '=', 'receivable')]
        #     if self.partner_type == 'Vendor':
        #         domain = [('internal_type', '=', 'payable')]
        return domain

    partner_type = fields.Selection(selection=[('Customer', 'Customer'), ('Vendor', 'Vendor')], string='Type')
    partner_ids = fields.Many2many('res.partner', 'cust_statement_rel', 'cust_stmnt_id', 'partner_id', string='Partners',
                                   domain=_domain_partner_ids)
    period_start = fields.Date("Period From")
    period_stop = fields.Date("Period To")
    account_id = fields.Many2one('account.account', "Account" ,domain=_domain_account_id)

    @api.multi
    def print_cust_statement_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'partner_ids': self.partner_ids.ids,
            'account_id': False,
            'partner_type': self.partner_type,
                }
        if self.account_id:
            data['account_id'] = [self.account_id.id, self.account_id.display_name]
        return self.env['report'].get_action([], 'report_cust_statement.cust_statement_report_pdf', data=data)


class ReportAdvPayment(models.AbstractModel):
    _name = 'report.report_cust_statement.cust_statement_report_pdf'

    def find_opening_balance(self, period_start, period_stop, partner_ids, account_id, partner_type):
        cr = self.env.cr
        accounts = self.env['account.account'].search([('internal_type','in',('receivable', 'payable'))])
        account_ids = []
        for account in accounts:
            account_ids.append(account['id'])
        sum_deb = 0
        sum_cred = 0
        sum_bal = 0
        for acnt in account_ids:
            query = "SELECT sum(debit) as debit,sum(credit) as credit, sum(debit) - sum(credit) as " \
                    "balance from account_move_line aml where aml.account_id = %s"
            vals = []
            if period_start:
                query += " and aml.date<%s"
                vals += [acnt, period_start]
            else:
                vals += [acnt]
            if partner_ids:
                query += " and aml.partner_id in %s"
                vals += [tuple(partner_ids)]
            if account_id:
                query += " and aml.account_id=%s"
                vals += [account_id[0]]
            cr.execute(query, tuple(vals))
            values = cr.dictfetchall()
            for vals in values:
                if vals['balance']:
                    sum_deb += vals['debit']
                    sum_cred += vals['credit']
                    sum_bal += vals['balance']
        return sum_deb, sum_cred,sum_bal

    @api.model
    def get_cust_statement_details(self, period_start=False, period_stop=False, partner_ids=False, account_id=False, partner_type=False):
        dom = [
            ('move_id.state', '=', 'posted'),
            ('account_id.internal_type', 'in', ('receivable', 'payable')),
            # ('account_id.user_type_id', '=', self.env.ref('account.data_account_type_receivable').id),
        ]
        if period_stop:
            dom.append(('date', '<=', period_stop))
        if period_start:
            dom.append(('date', '>=', period_start))
        if partner_ids:
            dom.append(('partner_id', 'in', partner_ids))
        if not partner_ids:
            if partner_type == 'Customer':
                dom.append(('partner_id.customer', '=', True))
            if partner_type == 'Vendor':
                dom.append(('partner_id.supplier', '=', True))
        if account_id:
            dom.append(('account_id', '=', account_id[0]))
        cust_statement_records = self.env['account.move.line'].search(dom)
        debit_sum = 0.0
        credit_sum = 0.0
        debit_opening = 0.0
        credit_opening = 0.0
        opening_balance = 0.0
        if period_start:
            debit_opening, credit_opening, opening_balance = self.find_opening_balance(period_start, period_stop, partner_ids, account_id, partner_type)
        current_balance = 0.0
        for cust_statement in cust_statement_records:
            debit_sum += cust_statement.debit
            credit_sum += cust_statement.credit
            current_balance += (cust_statement.debit - cust_statement.credit)
        closing_balance = opening_balance + current_balance
        partner_name_ids = ""
        for part in partner_ids:
            part_name = self.env['res.partner'].browse(part).name
            if partner_name_ids != "":
                partner_name_ids += ", "
            partner_name_ids += part_name
        return {
            'cust_statement_records': sorted(cust_statement_records, key=lambda l: l.date),
            'period_start':  period_start,
            'period_stop':  period_stop,
            'partner_ids': partner_name_ids,
            'account_id': account_id,
            'partner_type': partner_type,
            'here_debit_sum': debit_sum,
            'here_credit_sum': credit_sum,
            'current_balance': current_balance,
            'debit_opening': debit_opening,
            'credit_opening': credit_opening,
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'currency_id': self.env.user.currency_id,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_cust_statement_details(data['period_start'],
                                                 data['period_stop'],
                                                 data['partner_ids'],
                                                 data['account_id'],
                                                 data['partner_type'],
                                                 ))
        return self.env['report'].render('report_cust_statement.cust_statement_report_pdf', data)
