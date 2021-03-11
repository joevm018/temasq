from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo import SUPERUSER_ID
import pytz
import base64
import dateutil.parser

class CheckinReprtWizard(models.TransientModel):
    _name = "checkin.report.wizard"

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    
    @api.multi
    def checkin_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
            },
        }
        return self.env['report'].get_action(self,report_name='beauty_pos.report_checkin_template', data=data)

class ReportCheckin(models.AbstractModel):
    _name = 'report.beauty_pos.report_checkin_template'

    @api.model
    def render_html(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)
        
        start_date = date_start_obj.strftime("%Y-%m-%d 00:00:00")
        stop_date = date_end_obj.strftime("%Y-%m-%d 23:59:59")
        checkedin = []
        not_checkedin = []
        # order_lines = {}
        checkins = self.env['pos.order'].search([
                ('date_order', '>=', start_date),
                ('date_order', '<=', stop_date)
            ])
        today = datetime.now()
        repor_date = today.strftime("%m/%d/%Y %H:%M:%S")

        
        for record in checkins:
        	if record.checkin:
	            checkedin.append({
	                'status': record.state,
	                'order':record,
	                })
	        else:
	        	not_checkedin.append({
	                'status': record.state,
	                'order':record,
	                })

        fleet_args = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'report_date':repor_date,
            'checkedin': checkedin,
            'not_checkedin':not_checkedin,
        }
        return  self.env['report'].render('beauty_pos.report_checkin_template', fleet_args)



