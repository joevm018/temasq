# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
import base64
from odoo.exceptions import UserError


class CashierDetails(models.TransientModel):
    _name = 'cashier.transaction.wizard'
    _description = 'Cashier Details Report'

    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Responsible person")
    owner_email = fields.Char(string='Owner Email')

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
                'user_id': self.user_id.id}
        return self.env['report'].get_action([], 'cashier_transaction_report.report_cashier_transaction', data=data)

    @api.multi
    def email_report(self):
        to_email = self.owner_email
        if not to_email:
           raise UserError(_("Enter Email Id."))
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'partner_id': self.partner_id.id,
                'user_id': self.user_id.id}
        pdf = self.env['report'].get_pdf([], 'cashier_transaction_report.report_cashier_transaction', data=data)
        start_date = self.start_date
        end_date = self.end_date
        attachment_id = self.env['ir.attachment'].create({
            'name': 'Cashier Details Report: ' + str(start_date) + " To " + str(end_date),
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': 'Cashier Details Report.pdf',
            'mimetype': 'application/x-pdf'
        })
        mail_values = {
            # 'email_from': to_email,
            'reply_to': to_email,
            'email_to': to_email,
            'subject': 'Cashier Details Report: ' + str(start_date) + ' To ' + str(end_date),
            'body_html': """<div>
                                <p>Hello,</p>
                                <p>This email was created automatically by Odoo Beauty Manager. Please find the attached Cashier Details Report.</p>
                            </div>
                            <div>Thank You</div>""",
            'attachment_ids': [(4, attachment_id.id)]
        }
        result = self.env['mail.mail'].create(mail_values).send()
        if result:
            message = "Cashier Details Report is sent by Mail !!"
            self.env.user.notify_info(message, title='Email Sent', sticky=False)


class ReportCashierTransactionDetails(models.AbstractModel):
    _name = 'report.cashier_transaction_report.report_cashier_transaction'

    @api.model
    def get_cashier_details(self, date_start=False, date_stop=False, partner_id=False, user_id=False):
        d_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        d_date_stop = datetime.strptime(date_stop, '%Y-%m-%d').date()
        days_dif = (d_date_stop - d_date_start).days
        days_list = []
        for i in range(days_dif + 1):
            day = d_date_start + timedelta(days=i)
            days_list.append(str(day))
        day_wise_counts = {}
        for each_days in days_list:
            date_start_obj = datetime.strptime(each_days, '%Y-%m-%d')
            date_end_obj = datetime.strptime(each_days, '%Y-%m-%d')
            ord_date_start = date_start_obj.strftime("%Y-%m-%d 00:00:00")
            ord_date_stop = date_end_obj.strftime("%Y-%m-%d 23:59:59")
            ord_date_start = datetime.strptime(ord_date_start, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
            ord_date_stop = datetime.strptime(ord_date_stop, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
            lst_search = [('date_order', '>=', str(ord_date_start)), ('date_order', '<=', str(ord_date_stop)),
                          ('state', 'in', ['paid', 'invoiced', 'done'])]
            if partner_id:
                lst_search.append(('partner_id', '=', partner_id))
            if user_id:
                lst_search.append(('user_id', '=', user_id))
            normal_orders = self.env['pos.order'].search(lst_search)
            normal_payment_search = [('date', '=', each_days), ('is_advance', '=', False),('pos_statement_id', 'in', normal_orders.ids)]
            adv_payment_search = [('date', '=', each_days), ('is_advance', '=', True)]
            normal_payments = self.env['account.bank.statement.line'].search(normal_payment_search)
            advance_payments = self.env['account.bank.statement.line'].search(adv_payment_search)
            cash_amt = 0.0
            credit_amt = 0.0
            pay_later_amt = 0.0
            for statement in normal_payments:
                if statement.journal_id.type == 'cash':
                    cash_amt += statement.amount
                if statement.journal_id.type == 'bank':
                    if statement.journal_id.is_pay_later:
                        pay_later_amt += statement.amount
                    else:
                        credit_amt += statement.amount
            adv_cash_amt = 0.0
            adv_credit_amt = 0.0
            adv_pay_later_amt = 0.0
            for adv_statement in advance_payments:
                if adv_statement.journal_id.type == 'cash':
                    adv_cash_amt += adv_statement.amount
                if adv_statement.journal_id.type == 'bank':
                    if adv_statement.journal_id.is_pay_later:
                        adv_pay_later_amt += adv_statement.amount
                    else:
                        adv_credit_amt += adv_statement.amount
            product_cost_amt = 0.0
            service_cost_amt = 0.0
            reversed_amt = 0.0
            returned_amt = 0.0
            sales_amt = 0.0
            discount_amt = 0.0
            discount_line_amt = 0.0
            discount_global_amt = 0.0
            foc_amt = 0.0
            foc_line_amt = 0.0
            foc_global_amt = 0.0
            gift_card_amt = 0.0
            old_adv_remove_from_sale = 0.0
            for pos_order in normal_orders:
                for statem in  pos_order.statement_ids.filtered(lambda s: s.is_advance==True and s.date!= each_days):
                    old_adv_remove_from_sale += statem.amount
                line_product_cost = 0.0
                line_service_cost = 0.0
                for line in pos_order.lines:
                    if line.product_id.type == 'service':
                        line_service_cost += line.qty * line.product_id.standard_price
                    else:
                        line_product_cost += line.qty * line.product_id.standard_price
                product_cost_amt += line_product_cost
                service_cost_amt += line_service_cost
                if pos_order.amount_total < 0:
                    if pos_order.negative_entry and pos_order.is_reversed:
                        # B..........Rev: A . A reversed and created B as negative entry..A and B:Reversed entry(amt:-ve)
                        reversed_amt += pos_order.amount_total
                    if not pos_order.negative_entry and not pos_order.is_reversed:
                        # B.......... A . A returned and created B as new entry(amt:-ve).
                        returned_amt += pos_order.amount_total
                    # sales_amt += pos_order.amount_total
                # else:
                if pos_order.is_order_foc:
                    foc_global_amt += pos_order.amt_discount
                else:
                    discount_global_amt += pos_order.amt_discount
                line_subtotal = 0.0
                line_disc_subtotal = 0.0
                for line in pos_order.lines:
                    line_subtotal += line.qty * line.price_unit
                    if not pos_order.is_order_foc and line.is_order_line_foc:
                        foc_line_amt += line.qty * line.price_unit
                    else:
                        line_disc_subtotal += line.qty * line.price_unit
                line_discount = line_disc_subtotal - pos_order.amt_before_discount
                discount_line_amt += line_discount
                sales_amt += line_subtotal
                gift_card_amt += pos_order.redeemed_amount
            discount_amt = discount_line_amt + discount_global_amt
            foc_amt = foc_line_amt + foc_global_amt
            day_wise_counts[each_days] = {}
            day_wise_counts[each_days]['sales_amt'] = sales_amt - old_adv_remove_from_sale + adv_cash_amt + adv_credit_amt + adv_pay_later_amt
            day_wise_counts[each_days]['cash_amt'] = cash_amt
            day_wise_counts[each_days]['credit_amt'] = credit_amt
            day_wise_counts[each_days]['pay_later_amt'] = pay_later_amt
            day_wise_counts[each_days]['discount_amt'] = discount_amt
            day_wise_counts[each_days]['foc_amt'] = foc_amt
            day_wise_counts[each_days]['gift_card_amt'] = gift_card_amt
            day_wise_counts[each_days]['adv_cash_amt'] = adv_cash_amt
            day_wise_counts[each_days]['adv_credit_amt'] = adv_credit_amt
            day_wise_counts[each_days]['adv_pay_later_amt'] = adv_pay_later_amt
            day_wise_counts[each_days]['returned_amt'] = abs(returned_amt)
            day_wise_counts[each_days]['reversed_amt'] = abs(reversed_amt)
            day_wise_counts[each_days]['net_sales_amt'] = cash_amt + credit_amt + pay_later_amt + adv_cash_amt + adv_credit_amt + adv_pay_later_amt
            # day_wise_counts[each_days]['net_sales_amt'] = sales_amt - discount_amt + foc_amt + returned_amt - reversed_amt
            day_wise_counts[each_days]['product_cost_amt'] = product_cost_amt
            day_wise_counts[each_days]['service_cost_amt'] = service_cost_amt
            # if not day_wise_counts[each_days]['net_sales_amt'] == day_wise_counts[each_days]['sales_amt'] - discount_amt - foc_amt - gift_card_amt:
            #     if day_wise_counts[each_days]['net_sales_amt'] + total_balance != day_wise_counts[each_days]['sales_amt'] - discount_amt - foc_amt - gift_card_amt:
            #         print "not solved.........", each_days
        partner_id_name = ""
        if partner_id:

            partner_id_name = self.env['res.partner'].browse(partner_id).name
        user_id_name = ""
        if user_id:
            user_id_name = self.env['res.users'].browse(user_id).name
        from collections import OrderedDict
        ordered_daywise = OrderedDict(sorted(day_wise_counts.items()))
        return {
            'date_from': date_start,
            'date_to': date_stop,
            'day_wise_counts': ordered_daywise,
            'partner_name': partner_id_name,
            'user_name': user_id_name,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_cashier_details(data['date_start'], data['date_stop'], data['partner_id'], data['user_id']))
        return self.env['report'].render('cashier_transaction_report.report_cashier_transaction', data)
