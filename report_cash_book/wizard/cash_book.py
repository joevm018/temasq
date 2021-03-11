from odoo import api, fields, models


class CashBookReportWizard(models.TransientModel):
    _name = "cash.book.report"

    period_start = fields.Date("Period From")
    period_stop = fields.Date("Period To")
    partner_id = fields.Many2one('res.partner', "Partner")
    account_id = fields.Many2one('account.account', "Account", domain=[('is_cash','=',True)])

    @api.multi
    def print_cash_book_report(self):
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
        return self.env['report'].get_action([], 'report_cash_book.cash_book_report_pdf', data=data)


class ReportAdvPayment(models.AbstractModel):
    _name = 'report.report_cash_book.cash_book_report_pdf'

    def find_opening_balance(self, period_start, period_stop, partner_id, account_id):
        cr = self.env.cr
        accounts = self.env['account.account'].search([('is_cash', '=', True)])
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
    def get_cash_book_details(self, period_start=False, period_stop=False, partner_id=False, account_id=False):
        dom = [
            ('move_id.state', '=', 'posted'),
            ('account_id.is_cash', '=', True),
        ]
        if period_stop:
            dom.append(('date', '<=', period_stop))
        if period_start:
            dom.append(('date', '>=', period_start))
        if partner_id:
            dom.append(('partner_id', '=', partner_id[0]))
        if account_id:
            dom.append(('account_id', '=', account_id[0]))
        cash_book_records = self.env['account.move.line'].search(dom,)
        debit_sum = 0.0
        credit_sum = 0.0
        debit_opening = 0.0
        credit_opening = 0.0
        opening_balance = 0.0
        if period_start:
            debit_opening, credit_opening, opening_balance = self.find_opening_balance(period_start, period_stop, partner_id, account_id)
        current_balance = 0.0
        for cash_book in cash_book_records:
            debit_sum += cash_book.debit
            credit_sum += cash_book.credit
            current_balance += (cash_book.debit - cash_book.credit)
        closing_balance = opening_balance + current_balance
        return {
            'cash_book_records': sorted(cash_book_records, key=lambda l: l.date),
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
        data.update(self.get_cash_book_details(data['period_start'],
                                                 data['period_stop'],
                                                 data['partner_id'],
                                                 data['account_id'],
                                                 ))
        return self.env['report'].render('report_cash_book.cash_book_report_pdf', data)
