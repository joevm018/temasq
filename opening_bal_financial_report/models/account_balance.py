# -*- coding: utf-8 -*-

import time
from odoo import api, models


class ReportTrialBalance(models.AbstractModel):
    _inherit = 'report.account.report_trialbalance'

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance', 'opening_balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result.keys():
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
                # Opening balance start........
                account_opening_result = {}
                # Prepare sql query base on selected parameters from wizard
                init_tables, init_where_clause, init_where_params = self.env['account.move.line'].with_context(
                date_from=self.env.context.get('date_from'),
                date_to=False,
                initial_bal=True)._query_get()
                init_tables = init_tables.replace('"', '')
                if not init_tables:
                    init_tables = 'account_move_line'
                wheres = [""]
                if init_where_clause.strip():
                    wheres.append(init_where_clause.strip())
                filters = " AND ".join(wheres)
                # compute the balance, debit and credit for the provided accounts
                request = (
                "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                " FROM " + init_tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
                params = (tuple(accounts.ids),) + tuple(init_where_params)
                self.env.cr.execute(request, params)
                for row_open in self.env.cr.dictfetchall():
                    account_opening_result[row_open.pop('id')] = row_open
                for res_open_key, res_open_value in account_opening_result.items():
                    if account.id == res_open_key:
                        res['opening_balance'] = res_open_value['balance']
                # Opening balance end........
            if display_account == 'all':
                account_res.append(res)
            if display_account in ['movement', 'not_zero'] and not currency.is_zero(res['balance']):
                account_res.append(res)
        return account_res