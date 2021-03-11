from odoo import api, fields, models, SUPERUSER_ID, _
import base64
from odoo.exceptions import Warning, UserError, ValidationError
from datetime import datetime
import time


class ReportStaffCommission(models.AbstractModel):
    _name = 'report.staff_commission.staff_commission_report_pdf'

    @api.model
    def get_staff_commission(self, start_date=False, end_date=False, employee_id=False, company_id=False):
        dom = [('date_order', '>=', start_date),
               ('date_order', '<=', end_date),
               ('state', 'in', ['paid', 'invoiced', 'done']), ]
        orders = self.env['pos.order'].search(dom)
        # if employee_id:
        #     dom.append(('dentist', '=', employee_id[0]))
        staff_sold = {}
        res = []
        for order in orders:
            for line in order.lines:
                if employee_id and employee_id != line.staff_assigned_id.id:
                    continue
                staff_sold.setdefault(line.staff_assigned_id.id, [0.0, 0.0, 0.0, 0.0])
                staff_sold[line.staff_assigned_id.id][3] += line.after_global_disc_subtotal
                if line.product_id.type == 'consu':
                    staff_sold[line.staff_assigned_id.id][0] += line.after_global_disc_subtotal
                if line.product_id.type == 'product':
                    staff_sold[line.staff_assigned_id.id][1] += line.after_global_disc_subtotal
                if line.product_id.type == 'service':
                    staff_sold[line.staff_assigned_id.id][2] += line.after_global_disc_subtotal
        for record in staff_sold:
            profit = staff_sold[record][3]
            employee_id_rec = self.env['hr.employee'].browse(record)
            list_commision = []
            for commission in employee_id_rec.commission_ids:
                commission_calc_amt = 0.0
                commission_final = 0.0
                from_amt = commission.from_amt
                to_amt = commission.to_amt
                commission_perc = commission.commission
                c_between = from_amt <= profit <= to_amt
                c_last = from_amt <= profit and not to_amt
                if c_between:
                    commission_calc_amt = profit - from_amt
                    calculated_comm = (commission_calc_amt * commission_perc) / 100
                    if calculated_comm > 0:
                        commission_final = calculated_comm
                if c_last:
                    commission_calc_amt = profit - from_amt
                    calculated_comm = (commission_calc_amt * commission_perc) / 100
                    if calculated_comm > 0:
                        commission_final = calculated_comm
                if not c_between and not c_last and from_amt <= profit:
                    commission_calc_amt = to_amt - from_amt
                    calculated_comm = (commission_calc_amt * commission_perc) / 100
                    if calculated_comm > 0:
                        commission_final = calculated_comm
                list_commision.append({'from_amt': from_amt,
                                       'to_amt': to_amt,
                                       'commission': commission_perc,
                                       'commission_calc_amt': commission_calc_amt,
                                       'commission_final': commission_final,
                                       })
            emp_data = {'id': record,
                 'name': employee_id_rec.name,
                 'profit': profit,
                 'list_commision': list_commision}
            commission_dr_percent = 0.0
            emp_data['commission_dr_percent'] = 0.0
            if emp_data['profit']:
                for list_comm in emp_data['list_commision']:
                    commission_dr_percent += list_comm['commission_final']
                emp_data['commission_dr_percent'] = commission_dr_percent
            res.append(
                emp_data
            )
        return {
            'date_start': start_date,
            'date_end': end_date,
            'res': res}

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_staff_commission(data['form']['date_start'],
                                              data['form']['date_end'],
                                              data['employee_id'],
                                              data['company_id']))
        return self.env['report'].render('staff_commission.staff_commission_report_pdf', data)
