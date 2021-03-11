from odoo import api, fields, models, SUPERUSER_ID, _


class ReportStaffCommission(models.AbstractModel):
    _name = 'report.staff_commission_tres_jolie.staff_commission_report_pdf'

    @api.model
    def get_staff_commission(self, start_date=False, end_date=False,
                             employee_id=False, company_id=False):
        employee_obj = self.env['hr.employee']
        if employee_id:
            employees = employee_obj.browse(employee_id[0])
        else:
            employees = employee_obj.search([])
        options = {
            'date_from': start_date,
            'date_to': end_date,
        }
        commission_lines = []
        for employee in employees:
            target = employee.target
            referral_percent = employee.referral_percent
            service_income, referral_income, retail_income = 0, 0, 0
            tmp = {
                'name': employee.name,
                'service_revenue': service_income,
                'referral_revenue': referral_income,
                'total_revenue': (service_income + referral_income +
                                  retail_income),
                'retail_revenue': retail_income,
                'target': target,
                'referral_percent': referral_percent,
                'profit_percent': 0,
                'commission': 0,
                'achieved_from': 0,
                'achieved_to': 0,
            }
            if not (target > 0):
                commission_lines.append(tmp)
                continue
            service_income, referral_income, retail_income = employee.compute_employee_income(
                options)

            tmp = {
                'name': employee.name,
                'service_revenue': service_income,
                'referral_revenue': referral_income,
                'total_revenue': (service_income + referral_income +
                                  retail_income),
                'retail_revenue': retail_income,
                'target': target,
                'referral_percent': referral_percent
            }

            total_service_income = service_income + referral_income
            commission_info = employee._compute_total_commission(
                total_service_income, retail_income)
            tmp.update(commission_info)

            commission_lines.append(tmp)
        return {
            'date_start': start_date,
            'date_end': end_date,
            'res': commission_lines
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_staff_commission(
            data['form']['date_start'], data['form']['date_end'],
            data['employee_id'], data['company_id']))
        return self.env['report'].render(
            'staff_commission_tres_jolie.staff_commission_report_pdf', data)
