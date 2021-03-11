# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.pos_expense.report_profit_pos'

    @api.model
    def get_profit_details(self, date_start=False, date_stop=False):
        lst_expense_search = [('date', '>=', date_start), ('date', '<=', date_stop), ('state', '=', 'posted')]
        expenses = self.env['account.voucher'].search(lst_expense_search)
        info_expense = {'content': []}
        total_expense_total = 0.0
        for expen in expenses:
            total_expense_total += expen.amount
            info_expense['content'].append({
                'expense_line': expen,
            })

        lst_search = [('date_order', '>=', date_start), ('date_order', '<=', date_stop),
                      ('state', 'in', ['paid', 'invoiced', 'done'])]
        orders = self.env['pos.order'].search(lst_search)
        info_income = {'content': []}
        total_income_total = 0.0
        total_cost = 0.0
        for ord in orders:
            total_income_total += ord.amount_total
            cost = 0.0
            for line in ord.lines:
                cost += (line.qty * line.product_id.standard_price)
            info_income['content'].append({
                'order_line': ord,
                'cost': cost,
            })
            total_cost += cost

        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        if date_start:
            date_start = pytz.utc.localize(datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
        if date_stop:
            date_stop = pytz.utc.localize(datetime.strptime(date_stop, '%Y-%m-%d %H:%M:%S')).astimezone(tz)

        date_start = date_start.strftime('%m/%d/%Y %H:%M:%S')
        date_stop = date_stop.strftime('%m/%d/%Y %H:%M:%S')
        total_profit_total = total_income_total - total_cost - total_expense_total
        return {
            'date_from': date_start,
            'date_to': date_stop,
            'total_cost': total_cost,
            'info_income': info_income,
            'total_income_total': total_income_total,
            'info_expense': info_expense,
            'total_expense_total': total_expense_total,
            'total_profit_total': total_profit_total,
        }
