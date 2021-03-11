from odoo import api, fields, models


class IncomeReportWizard(models.TransientModel):
    _name = "income.account.report"

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        return {
            'domain': {
                'account_id': self._domain_account_id(),
            },
        }

    def _domain_account_id(self):
        direct_income = self.env.ref('account.data_account_type_revenue')
        indirect_income = self.env.ref('account.data_account_type_other_income')
        domain = [('user_type_id', 'in', (direct_income.id, indirect_income.id))]
        return domain

    period_start = fields.Date("Period From")
    period_stop = fields.Date("Period To")
    partner_id = fields.Many2one('res.partner', "Partner")
    account_id = fields.Many2one('account.account', "Account",domain=_domain_account_id)

    @api.multi
    def print_income_report(self):
        data = {
            'period_start': self.period_start,
            'period_stop': self.period_stop,
            'partner_id': False,
            'account_id': False,
                }
        if self.partner_id:
            data['partner_id'] = [self.partner_id.id, self.partner_id.name]
        if self.account_id:
            data['account_id'] = [self.account_id.id, self.account_id.display_name]
        return self.env['report'].get_action([], 'report_account_income.income_report_pdf', data=data)


class ReportAdvPayment(models.AbstractModel):
    _name = 'report.report_account_income.income_report_pdf'

    def find_opening_balance(self, period_start, period_stop, partner_id, account_id):
        cr = self.env.cr
        direct_income = self.env.ref('account.data_account_type_revenue')
        indirect_income = self.env.ref('account.data_account_type_other_income')
        domain = [('user_type_id', 'in', (direct_income.id, indirect_income.id))]
        accounts = self.env['account.account'].search(domain)
        account_ids = []
        for account in accounts:
            account_ids.append(account['id'])
        sum_deb = 0
        sum_cred = 0
        sum_bal = 0
        for acnt in account_ids:
            query = "SELECT sum(debit) as debit,sum(credit) as credit, sum(debit) - sum(credit)" \
                    "balance from account_move_line aml where aml.account_id = %s"
            vals = []
            if period_start:
                query += " and aml.date<%s"
                vals += [acnt, period_start]
            else:
                vals += [acnt]
            if partner_id:
                query += " and aml.partner_id=%s"
                vals += [partner_id[0]]
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
    def get_income_rep_details(self, period_start=False, period_stop=False, partner_id=False, account_id=False):
        direct_income = self.env.ref('account.data_account_type_revenue')
        indirect_income = self.env.ref('account.data_account_type_other_income')
        dom = [
            ('move_id.state', '=', 'posted'),
            ('account_id.user_type_id', 'in', (direct_income.id, indirect_income.id)),
        ]
        if period_stop:
            dom.append(('date', '<=', period_stop))
        if period_start:
            dom.append(('date', '>=', period_start))
        if partner_id:
            dom.append(('partner_id', '=', partner_id[0]))
        if account_id:
            dom.append(('account_id', '=', account_id[0]))
        income_records = self.env['account.move.line'].search(dom,)
        debit_sum = 0.0
        credit_sum = 0.0
        debit_opening = 0.0
        credit_opening = 0.0
        opening_balance = 0.0
        if period_start:
            debit_opening, credit_opening, opening_balance = self.find_opening_balance(period_start, period_stop, partner_id, account_id)
        current_balance = 0.0
        for income_rec in income_records:
            debit_sum += income_rec.debit
            credit_sum += income_rec.credit
            current_balance += (income_rec.debit - income_rec.credit)
        closing_balance = opening_balance + current_balance
        return {
            'income_records': sorted(income_records, key=lambda l: l.date),
            'period_start':  period_start,
            'period_stop':  period_stop,
            'partner_id': partner_id,
            'account_id': account_id,
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
        data.update(self.get_income_rep_details(data['period_start'],
                                                 data['period_stop'],
                                                 data['partner_id'],
                                                 data['account_id'],
                                                 ))
        return self.env['report'].render('report_account_income.income_report_pdf', data)
