# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class PartnerDetails(models.TransientModel):
    _name = 'partner.details.wizard'
    _description = 'Partner Details Report'

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
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Cashier")

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
        return self.env['report'].get_action([], 'pos_daily_report.report_partner_details', data=data)

    @api.multi
    def email_report(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'partner_id': self.partner_id.id,
                'user_id': self.user_id.id}
        pdf = self.env['report'].get_pdf([], 'pos_daily_report.report_partner_details', data=data)
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
        start_date = pytz.utc.localize(start_date).astimezone(tz)
        start_date = start_date.replace(tzinfo=None)
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")
        end_date = pytz.utc.localize(end_date).astimezone(tz)
        end_date = end_date.replace(tzinfo=None)
        attachment_id = self.env['ir.attachment'].create({
            'name': 'Sale Details: ' + str(start_date) + " To " + str(end_date),
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': 'Sale Details.pdf',
            'mimetype': 'application/x-pdf'
        })
        # conf = self.env['pos.config.settings'].search([], order='id desc', limit=1)
        # if not conf.email:
        #     warning = {
        #         'title': ' Warning !!!',
        #         'message': "Please enter the Owner email in Pos Configuration."
        #     }
        #     return {'warning': warning}

        from_email = user.company_id.owner_email
        mail_values = {
            # 'email_from': from_email,
            'reply_to': from_email,
            'email_to': from_email,
            'subject': 'Sale Details: ' + str(start_date) + ' To ' + str(end_date),
            'body_html': """<div>
                                            <p>Hello,</p>
                                            <p>This email was created automatically by Odoo Beauty Manager. Please find the attached sales report.</p>
                                        </div>
                                        <div>Thank You</div>""",
            'attachment_ids': [(4, attachment_id.id)]
        }
        result = self.env['mail.mail'].create(mail_values).send()
        if result:
            message = "Sale Details Report is sent by Mail !!"
            self.env.user.notify_info(message, title='Email Sent', sticky=False)


class ReportSaleDetails(models.AbstractModel):
    _name = 'report.pos_daily_report.report_partner_details'

    @api.model
    def get_partner_details(self, date_start=False, date_stop=False, partner_id=False, user_id=False):
        lst_search = [('date_order', '>=', date_start), ('date_order', '<=', date_stop), ('state', 'in', ['paid', 'invoiced', 'done'])]

        if partner_id:
            lst_search.append(('partner_id', '=', partner_id))
        if user_id:
            lst_search.append(('cashier_name', '=', user_id))
        orders = self.env['pos.order'].search(lst_search)
        info = {'content': []}
        Consumable_price_subtotal_incl = 0.00
        Retail_price_subtotal_incl = 0.00
        Service_price_subtotal_incl = 0.00
        for ord in orders:
            services_list = ""
            staff_list = ""
            cash_amt = 0.0
            credit_amt = 0.0
            for statement in ord.statement_ids:
                if statement.journal_id.type=='cash':
                    cash_amt += statement.amount
                if statement.journal_id.type == 'bank':
                    credit_amt += statement.amount
            for order_line in ord.lines:
                if order_line.product_id.type == 'consu':
                    Consumable_price_subtotal_incl += order_line.after_global_disc_subtotal
                if order_line.product_id.type == 'product':
                    Retail_price_subtotal_incl += order_line.after_global_disc_subtotal
                if order_line.product_id.type == 'service':
                    Service_price_subtotal_incl += order_line.after_global_disc_subtotal

                if order_line.product_id:
                    if services_list=="":
                        services_list += order_line.product_id.name
                    else:
                        now_serv = " , " + order_line.product_id.name
                        services_list += now_serv
                if order_line.staff_assigned_id:
                    if staff_list=="":
                        staff_list += order_line.staff_assigned_id.name
                    else:
                        now_serv = " , " + order_line.staff_assigned_id.name
                        staff_list += now_serv
            info['content'].append({
                'order_line': ord,
                'services_list': services_list,
                'staff_list': staff_list,
                'cash_amt': cash_amt,
                'credit_amt': credit_amt,
            })
        user_currency = self.env.user.company_id.currency_id
        total = 0.0
        products_sold2 = {}
        staff_sold = {}
        taxes = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                keyy = (line.order_id.partner_id, line.product_id, line.price_unit, line.discount,
                        line.staff_assigned_id, line.offer_string)
                products_sold2.setdefault(keyy, [0.0, 0.0])
                products_sold2[keyy][0] += line.qty
                products_sold2[keyy][1] += line.after_global_disc_subtotal

                staff_sold.setdefault(line.staff_assigned_id.name, [0.0, 0.0, 0.0, 0.0])
                staff_sold[line.staff_assigned_id.name][3] += line.after_global_disc_subtotal
                if line.product_id.type == 'consu':
                    staff_sold[line.staff_assigned_id.name][0] += line.after_global_disc_subtotal
                if line.product_id.type == 'product':
                    staff_sold[line.staff_assigned_id.name][1] += line.after_global_disc_subtotal
                if line.product_id.type == 'service':
                    staff_sold[line.staff_assigned_id.name][2] += line.after_global_disc_subtotal

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(
                        line.price_unit * (1 - (line.discount or 0.0) / 100.0), currency, line.qty,
                        product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'total': 0.0})
                        total_tax = taxes[tax['id']]['total'] + tax['amount']
                        taxes[tax['id']]['total'] = round(total_tax, 2)
        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
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

        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        if date_start:
            date_start = pytz.utc.localize(datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
        if date_stop:
            date_stop = pytz.utc.localize(datetime.strptime(date_stop, '%Y-%m-%d %H:%M:%S')).astimezone(tz)

        date_start = date_start.strftime('%m/%d/%Y %H:%M:%S')
        date_stop = date_stop.strftime('%m/%d/%Y %H:%M:%S')
        return {
            'date_from': date_start,
            'date_to': date_stop,
            'Consumable_price_subtotal_incl': Consumable_price_subtotal_incl,
            'Retail_price_subtotal_incl': Retail_price_subtotal_incl,
            'Service_price_subtotal_incl': Service_price_subtotal_incl,
            'info': info,
            'partner_name': partner_id_name,
            'user_name': user_id_name,
            'payments': payments,
            'staff_summary': [{'name': key or 'No Staff', 'consu_value': consu_value, 'product_value': product_value,
                               'service_value': service_value, 'amount': round(value, 2)} for
                              (key, [consu_value, product_value, service_value, value]) in staff_sold.iteritems()],
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_partner_details(data['date_start'], data['date_stop'], data['partner_id'], data['user_id']))
        return self.env['report'].render('pos_daily_report.report_partner_details ', data)
