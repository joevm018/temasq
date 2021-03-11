# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class ProfitDetails(models.TransientModel):
    _name = 'profit.details.wizard'
    _description = 'Profit Details Report'

    def _get_start_time(self):
        start_time = datetime.now()
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = start_time - timedelta(hours=3)
        return start_time

    def _get_end_time(self):
        start_time = datetime.now()
        end_time = start_time.replace(hour=20, minute=59, second=59, microsecond=0)
        return end_time

    start_date = fields.Datetime(required=True, default=_get_start_time)
    end_date = fields.Datetime(required=True, default=_get_end_time)

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date}
        return self.env['report'].get_action([], 'pos_expense.report_profit_pos', data=data)


class ReportSaleDetails(models.AbstractModel):
    _name = 'report.pos_expense.report_profit_pos'

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
        for ord in orders:
            total_income_total += ord.amount_total
            info_income['content'].append({
                'order_line': ord,
            })

        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        if date_start:
            date_start = pytz.utc.localize(datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
        if date_stop:
            date_stop = pytz.utc.localize(datetime.strptime(date_stop, '%Y-%m-%d %H:%M:%S')).astimezone(tz)

        date_start = date_start.strftime('%m/%d/%Y %H:%M:%S')
        date_stop = date_stop.strftime('%m/%d/%Y %H:%M:%S')
        total_profit_total = total_income_total - total_expense_total
        return {
            'date_from': date_start,
            'date_to': date_stop,
            'info_income': info_income,
            'total_income_total': total_income_total,
            'info_expense': info_expense,
            'total_expense_total': total_expense_total,
            'total_profit_total': total_profit_total,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_profit_details(data['date_start'], data['date_stop']))
        return self.env['report'].render('pos_expense.report_profit_pos ', data)
