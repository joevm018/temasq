# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import  time,  pytz,base64
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError


class ReportAttendance(models.TransientModel):
    _name = 'report.attendance'
    _description = 'Report Attendance'

    def _get_start_time(self):
        start_time = datetime.now()
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = start_time - timedelta(hours=3)
        return start_time

    def _get_end_time(self):
        start_time = datetime.now()
        end_time = start_time.replace(hour=20, minute=59, second=59, microsecond=0)
        return end_time

    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Datetime('Period From', default=_get_start_time, required=True)
    date_to = fields.Datetime('Period To', default=_get_end_time, required=True)

    @api.multi
    def action_print_report_attendance(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env['report'].get_action([], 'hr_report_attendance.report_attendance', data=data)

    @api.multi
    def email_report(self):
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'employee_id': self.employee_id.id}
        here_date_from = self.date_from
        here_date_to = self.date_to
        # here......................
        data.update({'form': data})
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        display_date_date_start = datetime.strftime(pytz.utc.localize(datetime.strptime(here_date_from, '%Y-%m-%d %H:%M:%S')).astimezone(local),"%Y-%m-%d %H:%M:%S")
        start_date = fields.Datetime.from_string(display_date_date_start)
        # start_date = fields.Datetime.from_string(display_date_date_start) + timedelta(hours=2.5)
        display_date_date_stop = datetime.strftime( pytz.utc.localize(datetime.strptime(here_date_to, '%Y-%m-%d %H:%M:%S')).astimezone(local), "%Y-%m-%d %H:%M:%S")
        end_date = fields.Datetime.from_string(display_date_date_stop)
        # end_date = fields.Datetime.from_string(display_date_date_stop) + timedelta(hours=2.5)
        pdf = self.env['report'].get_pdf([], 'hr_report_attendance.report_attendance', data=data)
        ATTACHMENT_NAME = 'Attendance Report: ' + str(start_date) + " To " + str(end_date)
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'mimetype': 'application/x-pdf'
        })
        ir_values = self.env['ir.values']
        mail_to_hr = ir_values.get_default('base.config.settings', 'mail_to_hr')
        # mail_to_hr = self.env['ir.config_parameter'].sudo().get_param('hr_report_attendance.mail_to_hr')
        if not mail_to_hr:
            raise ValidationError(_('Configure Sender Mail from HR Settings'))

        from_email = mail_to_hr
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': ATTACHMENT_NAME,
            'body_html': """<div>
                                <p>Hello,</p>
                                <p>This email was created automatically. 
                                Please find the attached Attendance report.</p>
                            </div>
                            <div>Thank You</div>""",
            'attachment_ids': [(4, attachment_id.id)]
        }
        mail_id = self.env['mail.mail'].create(mail_values)
        mail_id.send()
        if mail_id.state == 'exception':
            message = mail_id.failure_reason
            self.env.user.notify_warning(message, title='Mail Delivery Failed !!!', sticky=True)
        else:
            message = "Attendance Report mail sent successfully."
            self.env.user.notify_info(message, title='Email sent', sticky=True)
