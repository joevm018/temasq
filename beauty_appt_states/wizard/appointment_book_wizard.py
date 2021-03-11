from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo import SUPERUSER_ID
import pytz
import base64
import dateutil.parser

class AppointmentReportWizard(models.TransientModel):
    _inherit = "appointment.report.wizard"

    state_appt = fields.Selection([
        ('Booked', 'Booked'),
        ('Confirmed', 'Confirmed'),
        ('No Response', 'No Response'),
        ('Cancelled', 'Cancelled'),
        ('Executed', 'Executed')
    ], 'Appt state')
   
    @api.multi
    def appointment_report(self):
        staff_assigned_id = False
        if self.staff_assigned_id:
            staff_assigned_id = [self.staff_assigned_id.id, self.staff_assigned_id.name]
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'state_appt': self.state_appt,
                'staff_assigned_id':staff_assigned_id,
            },
        }
        return self.env['report'].get_action(self,report_name='beauty_pos.report_appointment_template', data=data)


class ReportAppointment(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.beauty_pos.report_appointment_template'

    @api.model
    def render_html(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        state_appt = data['form']['state_appt']
        staff_assigned_id = data['form']['staff_assigned_id']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)
        
        start_date = date_start_obj.strftime("%Y-%m-%d 00:00:00")
        stop_date = date_end_obj.strftime("%Y-%m-%d 23:59:59")
        docs = []
        # order_lines = {}
        dom = [('order_id.date_order', '>=', start_date),('order_id.date_order', '<=', stop_date)]
        if staff_assigned_id:
            dom.append(('staff_assigned_id', '=', staff_assigned_id[0]))
        if state_appt:
            dom.append(('state_appt', '=', state_appt))
        appointment_line = self.env['pos.order.line'].search(dom)
        appointments = []
        for appt_line in appointment_line:
            if appt_line.order_id not in appointments:
                appointments.append(appt_line.order_id)
        today = datetime.now()
        repor_date = today.strftime("%m/%d/%Y %H:%M:%S")
        staff_assigned_id_name = False
        staff_assigned_id_id = False
        if staff_assigned_id:
            staff_assigned_id_name =  staff_assigned_id[1]
            staff_assigned_id_id =  staff_assigned_id[0]
        if not state_appt:
            state_appt = 'All'
        appt_args = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'state_appt': state_appt,
            'staff_assigned_id': staff_assigned_id_id,
            'staff_assigned_id_name': staff_assigned_id_name,
            'report_date':repor_date,
            'appointments': sorted(appointments, key=lambda l: l.date_order),
        }
        return  self.env['report'].render('beauty_pos.report_appointment_template', appt_args)



