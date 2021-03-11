# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class ServiceCountReportWizard(models.TransientModel):
    _name = 'service.count.report.wizard'
    _description = 'Service Count Report'

    def _get_start_time(self):
        start_time = datetime.now()
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = start_time - timedelta(hours=3)
        return start_time

    def _get_end_time(self):
        start_time = datetime.now()
        end_time = start_time.replace(hour=20, minute=59, second=59, microsecond=0)
        return end_time

    start_date = fields.Datetime(required=True, default=_get_start_time)
    end_date = fields.Datetime(required=True, default=_get_end_time)
    staff_assigned_id = fields.Many2many('hr.employee', string='Staff',domain=[('is_beautician','=',True)])
    product_id = fields.Many2many('product.product', string="Services", domain=[('type', '=', 'service')])

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        staff_assigned_id = False
        list_staff_id = []
        name_staff_id = ""
        if self.staff_assigned_id:
            for staff in self.staff_assigned_id:
                list_staff_id.append(staff.id)
                if name_staff_id != "":
                    name_staff_id += ", "
                name_staff_id += staff.name
            staff_assigned_id = [list_staff_id, name_staff_id]
        product_id = False
        list_product_id = []
        name_product_id = ""
        if self.product_id:
            for prod in self.product_id:
                list_product_id.append(prod.id)
                if name_product_id != "":
                    name_product_id += ", "
                name_product_id += prod.name
            product_id = [list_product_id, name_product_id]
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'staff_assigned_id': staff_assigned_id,
                'product_id': product_id}
        return self.env['report'].get_action([], 'service_count_report.report_service_count', data=data)


class ReportSaleDetails(models.AbstractModel):
    _name = 'report.service_count_report.report_service_count'

    @api.model
    def get_service_count_details(self, date_start=False, date_stop=False, staff_assigned_id=False, product_id=False):
        dom = []
        if staff_assigned_id:
            dom.append(('staff_assigned_id', 'in', staff_assigned_id[0]))
        if product_id:
            dom.append(('product_id', '=', product_id[0]))
        order_lines = self.env['pos.order.line'].search(dom)
        pdt_orders = []
        for order_l in order_lines:
            if order_l.order_id.state in ['paid', 'invoiced', 'done'] and \
                    order_l.order_id.date_order >= date_start and  order_l.order_id.date_order <= date_stop and order_l.product_id.type == 'service':
                pdt_orders.append(order_l)
        order_lines = pdt_orders
        product_list = []
        for order_l in order_lines:
            if order_l.product_id not in product_list:
                product_list.append(order_l.product_id)
        service_count_dict = {}
        for product in product_list:
            count_service = 0
            for order_l in order_lines:
                if product.id == order_l.product_id.id:
                    count_service = count_service + 1
            service_count_dict[product] = count_service
        order_list = {
            'service_count_dict': service_count_dict,
            'product_list': product_list,
        }
        return order_list

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        result = self.get_service_count_details(data['date_start'],
                                          data['date_stop'],
                                          data['staff_assigned_id'],
                                          data['product_id'])
        data.update(result)
        return self.env['report'].render('service_count_report.report_service_count', data)
