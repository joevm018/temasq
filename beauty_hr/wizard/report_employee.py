from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class EmployeeReport(models.TransientModel):
    _name = 'employee.report'

    employee_id = fields.Many2one('hr.employee', string='Employee')

    @api.multi
    def generate_report(self):
        employee = False
        if self.employee_id:
            employee = [self.employee_id.id, self.employee_id.name]
        data = {'employee_id': employee}
        return self.env['report'].get_action([], 'beauty_hr.employee_list_report', data=data)


class ReportEmpTotal(models.AbstractModel):
    _name = 'report.beauty_hr.employee_list_report'

    @api.model
    def get_sale_details(self, employee_id=False):
        lst_search = []
        if employee_id:
            lst_search.append(('id', '=', employee_id[0]))
        employees = self.env['hr.employee'].search(lst_search)
        document_type = self.env['document.type'].search([])
        heading_doc_list = []
        for doc_type in document_type:
            heading_doc_list.append(doc_type)
        info = {'content': []}
        for emp in employees:
            doc_dictionary = {}
            for doc_type in document_type:
                doc_dictionary[doc_type] = ['', '']

            count_doc = 0
            for heading_name in heading_doc_list:
                doc_list = []
                for emp_doc in emp.document_ids:
                    if heading_name.id == emp_doc.document_type.id:
                        count_doc += 1
                        doc_list.append(emp_doc.name)
                        doc_list.append(emp_doc.expiry_date)
                        doc_dictionary[heading_name] = doc_list
            info['content'].append({
                'employee_id': emp,
                'doc_values': doc_dictionary,
            })
        if not employee_id:
            employee_id_name = 'All'
        else:
            employee_id_name = employee_id[1]
        employee_list = {
            'count_list': sorted(info['content'], key=lambda l: l['employee_id']),
            'employee_id_name': employee_id_name,
            'heading_doc_list': heading_doc_list,
        }
        return employee_list

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        result = self.get_sale_details(data['employee_id'])
        data.update(result)
        return self.env['report'].render('beauty_hr.employee_list_report', data)
