# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class DailyCollection(models.TransientModel):
    _name = 'daily.collection.wizard'
    _description = 'Daily Collection Report'

    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Cashier")
    show_details = fields.Boolean(string="Detailed")

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
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'partner_id': self.partner_id.id,
                'user_id': self.user_id.id, 'show_details':self.show_details}
        return self.env['report'].get_action([], 'daily_collection_report.report_daily_collection', data=data)

    @api.multi
    def email_report(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'partner_id': self.partner_id.id,
                'user_id': self.user_id.id, 'show_details': self.show_details}
        pdf = self.env['report'].get_pdf([], 'daily_collection_report.report_daily_collection', data=data)
        start_date = self.start_date
        end_date = self.end_date
        attachment_id = self.env['ir.attachment'].create({
            'name': 'Daily Collection Report: ' + str(start_date) + " To " + str(end_date),
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': 'Daily Collection Report.pdf',
            'mimetype': 'application/x-pdf'
        })
        from_email = user.company_id.owner_email
        mail_values = {
            # 'email_from': from_email,
            'reply_to': from_email,
            'email_to': from_email,
            'subject': 'Daily Collection Report: ' + str(start_date) + ' To ' + str(end_date),
            'body_html': """<div>
                                            <p>Hello,</p>
                                            <p>This email was created automatically by Odoo Beauty Manager. Please find the attached Daily Collection Report.</p>
                                        </div>
                                        <div>Thank You</div>""",
            'attachment_ids': [(4, attachment_id.id)]
        }
        result = self.env['mail.mail'].create(mail_values).send()
        if result:
            message = "Daily Collection Report is sent by Mail !!"
            self.env.user.notify_info(message, title='Email Sent', sticky=False)


class ReportSaleDetails(models.AbstractModel):
    _name = 'report.daily_collection_report.report_daily_collection'

    @api.model
    def get_daily_collection_details(self, date_start=False, date_stop=False, partner_id=False, user_id=False, show_details=False):
        d_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        d_date_stop = datetime.strptime(date_stop, '%Y-%m-%d').date()
        date_start_obj = datetime.strptime(date_start, '%Y-%m-%d')
        date_end_obj = datetime.strptime(date_stop, '%Y-%m-%d')
        ord_date_start = date_start_obj.strftime("%Y-%m-%d 00:00:00")
        ord_date_stop = date_end_obj.strftime("%Y-%m-%d 23:59:59")
        ord_date_start = datetime.strptime(ord_date_start, '%Y-%m-%d %H:%M:%S')- timedelta(hours=3)
        ord_date_stop = datetime.strptime(ord_date_stop, '%Y-%m-%d %H:%M:%S')- timedelta(hours=3)
        days_dif = (d_date_stop - d_date_start).days
        days_list = []
        for i in range(days_dif + 1):
            day = d_date_start + timedelta(days=i)
            days_list.append(str(day))
        adv_payment_search = [('date', 'in', days_list), ('is_advance', '=', True),('pos_statement_id.state', '!=', 'cancel')]
        lst_search = [('date_order', '>=', str(ord_date_start)), ('date_order', '<=', str(ord_date_stop)), ('state', 'in', ['paid', 'invoiced', 'done'])]
        credit_repay_payments_search = [('payment_date', 'in', days_list), ('payment_type', '=', 'inbound')]
        if partner_id:
            lst_search.append(('partner_id', '=', partner_id))
            adv_payment_search.append(('pos_statement_id.partner_id', '=', partner_id))
            credit_repay_payments_search.append(('partner_id', '=', partner_id))
        if user_id:
            lst_search.append(('cashier_name', '=', user_id))
            adv_payment_search.append(('pos_statement_id.cashier_name', '=', user_id))
            credit_repay_payments_search.append(('create_uid', '=', user_id))
        normal_orders = self.env['pos.order'].search(lst_search)
        normal_payment_search = [('date', 'in', days_list), ('is_advance', '=', False),
                                 ('pos_statement_id', 'in', normal_orders.ids)]
        normal_payments = self.env['account.bank.statement.line'].search(normal_payment_search)
        advance_payments = self.env['account.bank.statement.line'].search(adv_payment_search)
        all_account_payments = self.env['account.payment'].search(credit_repay_payments_search)
        advance_orders = []
        credit_repay_orders = []
        credit_repay_payments = []
        all_orders = []
        for norm_ord in normal_orders:
            if norm_ord not in all_orders:
                all_orders.append(norm_ord)
        for adv_paymt in advance_payments:
            if adv_paymt.pos_statement_id not in advance_orders:
                advance_orders.append(adv_paymt.pos_statement_id)
            if adv_paymt.pos_statement_id not in all_orders:
                all_orders.append(adv_paymt.pos_statement_id)
        for all_acc_paymt in all_account_payments:
            if all_acc_paymt.invoice_ids:
                inv_related_order =  self.env['pos.order'].search([('invoice_id', '=', all_acc_paymt.invoice_ids[0].id)])
                if inv_related_order:
                    if all_acc_paymt not in credit_repay_payments:
                        credit_repay_payments.append(all_acc_paymt)
                    if inv_related_order not in credit_repay_orders:
                        credit_repay_orders.append(inv_related_order)
                    if inv_related_order not in all_orders:
                        all_orders.append(inv_related_order)
        info = {'content': []}
        for ord in all_orders:
            credit_repayment_cash = 0.0
            credit_repayment_card = 0.0
            cash_amt = 0.0
            credit_amt = 0.0
            pay_later_amt = 0.0
            for statement in ord.statement_ids:
                if statement.date in days_list:
                    if statement.journal_id.type == 'cash':
                        cash_amt += statement.amount
                    if statement.journal_id.type == 'bank':
                        if statement.journal_id.is_pay_later:
                            pay_later_amt += statement.amount
                        else:
                            credit_amt += statement.amount
            cashier_here = False
            if ord.invoice_id:
                for cred_repay_paymt in credit_repay_payments:
                    if ord.invoice_id in cred_repay_paymt.invoice_ids:
                        cashier_here = cred_repay_paymt.create_uid.name
                        if cred_repay_paymt.journal_id.type == 'cash':
                            credit_repayment_cash += cred_repay_paymt.amount
                        if cred_repay_paymt.journal_id.type == 'bank':
                            if not cred_repay_paymt.journal_id.is_pay_later:
                                credit_repayment_card += cred_repay_paymt.amount
            else:
                cashier_here = ord.cashier_name.name
            info['content'].append({
                'order_here': ord,
                'cashier_name': cashier_here,
                'cash_amt': cash_amt + credit_repayment_cash,
                'credit_amt': credit_amt + credit_repayment_card,
                'pay_later_amt': pay_later_amt,
                'sale_amt': cash_amt + credit_amt + credit_repayment_cash + credit_repayment_card,
            })
        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', normal_orders.ids)]).ids
        if st_line_ids:
            self.env.cr.execute("""
                                SELECT aj.name, sum(amount) total
                                FROM account_bank_statement_line AS absl,
                                     account_bank_statement AS abs,
                                     account_journal AS aj 
                                WHERE absl.statement_id = abs.id
                                    AND abs.journal_id = aj.id 
                                    AND absl.id IN %s 
                                GROUP BY aj.name
                            """, (tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []
        partner_id_name = ""
        if partner_id:
            partner_id_name = self.env['res.partner'].browse(partner_id).name
        user_id_name = ""
        if user_id:
            user_id_name = self.env['res.users'].browse(user_id).name
        return {
            'date_from': date_start,
            'date_to': date_stop,
            'partner_name': partner_id_name,
            'show_details': show_details,
            'user_name': user_id_name,
            'info': info,
            'payments': payments,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_daily_collection_details(data['date_start'], data['date_stop'], data['partner_id'],
                                             data['user_id'], data['show_details']))
        return self.env['report'].render('daily_collection_report.report_daily_collection', data)
