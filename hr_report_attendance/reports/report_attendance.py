# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class ReportParserAttendance(models.AbstractModel):
    _name = 'report.hr_report_attendance.report_attendance'

    @api.model
    def get_report_attendance(self, date_start=False, date_stop=False, employee_id=False):
        info = {'content': []}
        dom = ['|', '&', ('check_in', '<=', date_stop), ('check_in', '>=', date_start), '&', ('check_out', '<=', date_stop), ('check_out', '>=', date_start)]
        if employee_id:
            dom.append(('employee_id', '=', employee_id[0]))
        attendance = self.env['hr.attendance'].search(dom, order='check_in asc')
        employee_name = "All"
        if employee_id:
            employee_name = self.env['hr.employee'].browse(employee_id[0]).name
        employee_list = []
        for att in attendance:
            if att.employee_id not in employee_list:
                employee_list.append(att.employee_id)
        for emp in employee_list:
            total_work_hour = 0.0
            total_prev_ot = 0.0
            domm = ['|', '&', ('check_in', '<=', date_stop), ('check_in', '>=', date_start), '&', ('check_out', '<=', date_stop), ('check_out', '>=', date_start)]
            if not employee_id:
                domm.append(('employee_id', '=', emp.id))
            emp_attendance = self.env['hr.attendance'].search(domm, order='check_in asc')
            for att in emp_attendance:
                checkinn = att.check_in
                checkoutt = att.check_out
                work_hour = 0
                ot_hour = 0
                if att.check_in and att.check_out:
                    if att.employee_id not in employee_list:
                        employee_list.append(att.employee_id)
                    normal_ot_per_Day = att.employee_id.normal_working_hr
                    if not normal_ot_per_Day:
                        raise ValidationError(_('Configure Normal working hours per day for %s')
                                        % (att.employee_id.name))
                    if att.worked_hours:
                        worked_hour = "{:.2f}".format(att.worked_hours)
                        work_hour = float(worked_hour)
                        total_work_hour += float(worked_hour)
                    if total_work_hour - normal_ot_per_Day - total_prev_ot < 0:
                        ot_hour = 0
                    else:
                        ot_hour = total_work_hour - normal_ot_per_Day - total_prev_ot
                    total_prev_ot += ot_hour
                info['content'].append({
                    'employee_id': att.employee_id.name,
                    'emp_id': att.employee_id.id,
                    'check_in': checkinn,
                    'check_out': checkoutt,
                    'work_hour': float(work_hour),
                    'ot_hour': float(ot_hour),
                })

        info['content'] = sorted(info['content'], key=lambda l: l['employee_id'])
        return {
                'employee_list': employee_list,
                'attendances': info,
                'date_now': datetime.utcnow().date().strftime('%m/%d/%Y %H:%M:%S'),
                'employee_name': employee_name,
                'date_start': date_start,
                'date_stop': date_stop,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_report_attendance(data['form']['date_from'], data['form']['date_to'],
                                               data['form']['employee_id']))
        return self.env['report'].render('hr_report_attendance.report_attendance', data)
