# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime
from odoo import SUPERUSER_ID
import time,  pytz,base64
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date


class VisaStatus(models.Model):
    _name = "visa.status"

    name = fields.Char(required=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    full_name = fields.Char('Full name', required=True)
    visa_details_status = fields.Many2one('visa.status', string='Visa Status')
    joining_date = fields.Date('Joining Date')
    working_hours = fields.Float('Working hours')

    document_ids = fields.One2many('employee.document', 'employee_id', string='Documents')

    @api.model
    def employee_documents_alert(self, cron_mode=True):
        for employee in self.search([('active', '=', True), ('document_ids', '!=', None)]):
            for documents in employee.document_ids:
                if documents.remind_x_day_before>=0:
                    notify_date = (date.today() + timedelta(days=documents.remind_x_day_before)).strftime('%Y-%m-%d')
                    if notify_date == documents.expiry_date:
                        message = documents.document_type.name + ' of ' + employee.name + \
                                  ' (ID: ' + documents.name + ') is going to be expire on ' + documents.expiry_date
                        self.env.user.notify_warning(message, title= documents.document_type.name + ' Expiry Alert',
                                                  sticky=True)



