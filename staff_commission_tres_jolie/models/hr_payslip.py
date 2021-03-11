from odoo import fields, models, api


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def compute_commission(self):
        for payslip in self:
            options = {
                'date_from': payslip.date_from,
                'date_to': payslip.date_to,
            }
            commission_final = payslip.employee_id.compute_total_commission(
                options)
            inc = False
            for i in payslip.input_line_ids:
                if i.code == 'INCENTIVE':
                    inc = i
            if inc:
                inc.amount = commission_final
            else:
                if payslip.contract_id:
                    contract = payslip.contract_id.id
                    vals = {
                        'payslip_id': payslip.id,
                        'contract_id': contract,
                        'name': 'Sales Commission',
                        'code': 'INCENTIVE',
                        'amount': commission_final,
                    }
                    payslip.env['hr.payslip.input'].create(vals)
