# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class ComboReportWizard(models.TransientModel):
    _name = 'combo.report.wizard'
    _description = 'Combo Packs Report'

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
    product_id = fields.Many2one('product.product', string="Combo Pack", domain=[('combo_pack', '=', True)])

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
        partner_id = False
        if self.partner_id:
            partner_id = [self.partner_id.id, self.partner_id.name]
        product_id = False
        if self.product_id:
            product_id = [self.product_id.id, self.product_id.name]
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'partner_id': partner_id,
                'product_id': product_id}
        return self.env['report'].get_action([], 'combo_packs_management.report_combo_packs', data=data)

    @api.multi
    def email_report(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'partner_id': self.partner_id.id,
                'product_id': self.product_id.id}
        pdf = self.env['report'].get_pdf([], 'combo_packs_management.report_combo_packs', data=data)
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
    _name = 'report.combo_packs_management.report_combo_packs'

    @api.model
    def get_partner_details(self, date_start=False, date_stop=False, partner_id=False, product_id=False):
        dom = [('date_order', '>=', date_start), ('date_order', '<=', date_stop), ('is_reversed', '=', False), ('partner_id', '!=', False), ('have_combo', '=', True), ('state', 'in', ['paid', 'invoiced', 'done'])]

        if partner_id:
            dom.append(('partner_id', '=', partner_id[0]))
        orders = self.env['pos.order'].search(dom)
        if product_id:
            pdt_orders = []
            for i in orders:
                for line in i.lines:
                    if i not in pdt_orders and line.product_id.id == product_id[0]:
                        pdt_orders.append(i)
            orders = pdt_orders
        order_data = []
        session_obj = self.env['combo.session']
        for order in orders:
            lines = []
            combo = False
            for line in order.lines:
                if line.product_id.combo_pack:
                    combo = True
                    sessions_dict = {}
                    if product_id:
                        if line.product_id.id == product_id[0]:
                            sessions = session_obj.search([('order_line_id', '=', line.id)])
                            sessions_dict['line'] = line
                            sessions_dict['sessions'] = sessions
                            lines.append(sessions_dict)
                    else:
                        sessions = session_obj.search([('order_line_id', '=', line.id)])
                        sessions_dict['line'] = line
                        sessions_dict['sessions'] = sessions
                        lines.append(sessions_dict)
            if combo:
                order_list = {
                    'number': order.name,
                    'customer': order.partner_id.name,
                    'date': order.date_order,
                    'lines': lines
                }
                order_data.append(order_list)
        return {'orders': sorted(order_data, key=lambda l: l['number'])}

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        result = self.get_partner_details(data['date_start'],
                                          data['date_stop'],
                                          data['partner_id'],
                                          data['product_id'])
        data.update(result)
        return self.env['report'].render('combo_packs_management.report_combo_packs', data)
