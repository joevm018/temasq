# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime
from odoo import SUPERUSER_ID
import time,  pytz,base64
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    qatar_id = fields.Char('Qatar ID')
    joining_date = fields.Date('Joining Date')
    normal_working_hr = fields.Float('Normal working hours per day', required=True,
                                     default=lambda self: self.env['ir.values'].get_default('base.config.settings', 'normal_working_hr'))

    def _check_normal_working_hr(self):
        for emp in self:
            min, max = 0, 24
            normal_working_hr = emp.normal_working_hr
            if not min < normal_working_hr < max: return False
        return True

    _constraints = [(_check_normal_working_hr, 'Please enter working hours properly!', ['normal_working_hr'])]

    def _download_attendance(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()
        return True

    def attendance_report_alert_all(self, date_from):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()
        date_from1 = date_from
        date_from = date_from + " 00:00:00"
        today = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start = start - timedelta(hours=3)
        stop = start + timedelta(days=1)
        data = {'date_from': str(start), 'date_to': str(stop), 'employee_id': False}
        data.update({'form': data})
        pdf = self.env['report'].get_pdf([], 'hr_report_attendance.report_attendance', data=data)
        ATTACHMENT_NAME = 'Attendance Report: ' + str(date_from1)
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'mimetype': 'application/x-pdf'
        })
        mail_to_hr = self.env['ir.config_parameter'].sudo().get_param('hr_report_attendance.mail_to_hr')
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

    @api.model
    def attendance_report_alert_mail_today(self, cron_mode=True):
        date_from = time.strftime('%Y-%m-%d')
        self.attendance_report_alert_all(date_from)

    @api.model
    def attendance_report_alert_mail_yesterday(self, cron_mode=True):
        today_date = datetime.utcnow().date()
        today_end = fields.Datetime.to_string(today_date + relativedelta(days=-1))
        today_end = datetime.strptime(today_end, "%Y-%m-%d %H:%M:%S").date()
        today_end = today_end.strftime("%Y-%m-%d")
        self.attendance_report_alert_all(today_end)



