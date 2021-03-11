from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class ChangeOrderDateWizard(models.TransientModel):
    _name = "change.orderdate.wizard"

    def _default_date(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['pos.order'].browse(active_id)
            start_times = []
            for line in order.lines:
                if line.procedure_start:
                    start_times.append(line.procedure_start)
            if start_times:
                min_start_time = min(start_times)
                return min_start_time
            return False
        return False

    new_date_from = fields.Datetime(string='Start Date', default=_default_date, required=True)

    @api.multi
    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['pos.order'].browse(active_id)
            stop_times = []
            start_times = []
            max_stop_time = False
            min_start_time = False
            for line in order.lines:
                if line.procedure_stop:
                    stop_times.append(line.procedure_stop)
                if line.procedure_start:
                    start_times.append(line.procedure_start)
            if stop_times:
                max_stop_time = max(stop_times)
            if start_times:
                min_start_time = min(start_times)
            if min_start_time and self.new_date_from:
                p_new_date_from = datetime.strptime(self.new_date_from, "%Y-%m-%d %H:%M:%S")
                p_min_start_time = datetime.strptime(min_start_time, "%Y-%m-%d %H:%M:%S")
                difference_here = p_new_date_from - p_min_start_time
                for ord_line in order.lines:
                    if ord_line.procedure_start:
                        p_procedure_start = datetime.strptime(ord_line.procedure_start, "%Y-%m-%d %H:%M:%S")
                        dom_here = [('staff_assigned_id', '=', ord_line.staff_assigned_id.id),
                                    ('procedure_start', '<', str(p_procedure_start + difference_here)),
                                    ('procedure_stop', '>', str(p_procedure_start + difference_here)),
                                    ]
                        staff_available = self.env['pos.order.line'].search(dom_here)
                        if staff_available:
                            for rec in staff_available:
                                if rec.order_id != ord_line.order_id:
                                    raise UserError(_('Staff "%s" is busy for procedure "%s" for Appointment - %s on this date.')
                                                % (rec.staff_assigned_id.name, rec.product_id.name, rec.order_id.name))
                        ord_line.write({'procedure_start': p_procedure_start + difference_here})
                    if ord_line.procedure_stop:
                        p_procedure_stop = datetime.strptime(ord_line.procedure_stop, "%Y-%m-%d %H:%M:%S")
                        ord_line.write({'procedure_stop': p_procedure_stop + difference_here})
                p_date_order = datetime.strptime(order.date_order, "%Y-%m-%d %H:%M:%S")
                order.write({'date_order':  p_date_order + difference_here})
                if max_stop_time:
                    p_max_stop_time = datetime.strptime(max_stop_time, "%Y-%m-%d %H:%M:%S")
                    order.write({'date_stop': p_max_stop_time + difference_here})
                if min_start_time:
                    p_min_start_time = datetime.strptime(min_start_time, "%Y-%m-%d %H:%M:%S")
                    order.write({'date_start': p_min_start_time + difference_here})


