from odoo import models, fields, api
import time
from datetime import datetime
from dateutil import relativedelta


class StaffCommissionReportWizard(models.TransientModel):
    _name = "staff.commission.wizard"

    date_start = fields.Date("Period From", required=True, default=time.strftime('%Y-%m-01'))
    date_end = fields.Date("Period To", required=True,
                           default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    employee_id = fields.Many2one('hr.employee', "Employee")

    def _get_company_id(self):
        group_multi_company = self.env.user.has_group('base.group_multi_company')
        if group_multi_company:
            company_ids = [x.id for x in self.env['res.company'].search([('id', 'in', self.env.user.company_ids.ids)])]
            domain_company = [('id', 'in', company_ids)]
        else:
            domain_company = [('id', '=', self.env.user.company_id.id)]
        return domain_company

    company_id = fields.Many2one('res.company', "Company", domain=_get_company_id, required=True)

    @api.model
    def default_get(self, fields):
        res = super(StaffCommissionReportWizard, self).default_get(fields)
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        return res

    @api.multi
    def staff_commission_report(self):
        employee_id = False
        if self.employee_id:
            employee_id = [self.employee_id.id, self.employee_id.name]
        datas = {'active_ids': self.env.context.get('active_ids', []),
                 'form': self.read(['date_start', 'date_end'])[0],
                 'employee_id': employee_id,
                 'company_id': [self.company_id.id, self.company_id.name],
                 }
        return self.env['report'].get_action([], 'staff_commission.staff_commission_report_pdf', data=datas)
