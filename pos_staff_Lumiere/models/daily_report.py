# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import date, datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class PosOrder(models.TransientModel):
    _name = "daily.report.wizard"

    report_date = fields.Date("Report of the Date", required=True, default=fields.Date.context_today)

    @api.multi
    def daily_report(self):
        # From confirm button on daily report mail menu
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        selected_date = self.report_date + " 00:00:00"
        todayy = datetime.strptime(selected_date, '%Y-%m-%d %H:%M:%S')
        todayy = todayy.replace(hour=0, minute=0, second=0, microsecond=0)
        today_start = todayy - timedelta(hours=3)
        today_end2 = todayy + timedelta(days=1)
        today_end = today_start + timedelta(days=1)
        month_start2 = todayy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start = month_start2 - timedelta(hours=3)
        pos_config_ids = self.env['pos.config'].search([])
        data = {'date_start': str(today_start), 'date_stop': str(today_end), 'partner_id': False,
                'user_id': False}
        pdf = self.env['report'].get_pdf([], 'pos_daily_report.report_partner_details', data=data)
        attachment_id = self.env['ir.attachment'].create({
            'name': 'Sale Details: ' + str(todayy) + " To " + str(today_end2),
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': 'Sale Details Today.pdf',
            'mimetype': 'application/x-pdf'
        })
        data2 = {'date_start': str(month_start), 'date_stop': str(today_end), 'user_id': False,
                    'partner_id': False}
        pdf2 = self.env['report'].get_pdf([], 'pos_daily_report.report_partner_details', data=data2)
        attachment_id2 = self.env['ir.attachment'].create({
                'name': 'Sale Details: ' + str(month_start2) + " To " + str(today_end2),
                'type': 'binary',
                'datas': base64.encodestring(pdf2),
                'datas_fname': 'Sale Details Month.pdf',
                'mimetype': 'application/x-pdf'
            })
        attach = {
                attachment_id.id,
                attachment_id2.id
            }

        from_email = user.company_id.owner_email
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': 'Sales Report : ' + self.report_date,
            'body_html': """<div>
                                                <p>Hello,</p>
                                                <p>This email was created automatically by Odoo Beauty Manager. Please find the attached sales reports.</p>
                                            </div>
                                            <div>Thank You</div>""",
            'attachment_ids': [(6, 0, attach)]
        }
        mail_id = self.env['mail.mail'].create(mail_values)
        mail_id.send()
        if mail_id.state == 'exception':
            message = mail_id.failure_reason
            self.env.user.notify_warning(message, title='Mail Delivery Failed !!!', sticky=True)
        else:
            message = "Daily report mail sent successfully."
            self.env.user.notify_info(message, title='Email sent', sticky=True)
