# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import api, models


class CalendarConfig(models.Model):
    _inherit = 'calender.config'

    @api.model
    def add_appointment(self, data):
        order_id = False
        if not data.get('partner_id'):
            if (data.get('customer_new_name') and
                    data.get('customer_new_phone')):
                customer = self.env['res.partner'].create({
                    'name': data.get('customer_new_name'),
                    'phone': data.get('customer_new_phone'),
                    'dob_month': data.get('customer_new_dob_month'),
                    'dob_day': data.get('customer_new_dob_day'),
                })
                data.update({
                    'partner_id': customer.id,
                    'phone': data.get('customer_new_phone')
                })
        if not data.get('partner_id'):
            raise UserError('Set Customer')
        if data:
            for d_lines in data['lines']:
                d_lines[2]['checkin'] = False
                if 'price_unit' not in d_lines[2]:
                    d_lines[2]['price_unit'] = self.env[
                        'product.product'
                    ].browse(d_lines[2]['product_id']).lst_price
            data['checkin'] = False
            order_id = self.env['pos.order'].create(data)
        return order_id and order_id.lines.ids

    @api.model
    def fetch_calendar_extras(self):
        """Fetches extra details required for calender"""
        values_obj = self.env['ir.values']
        #  fetching time schedule
        time_schedule = {
            'schedule_start': values_obj.get_default('res.config.settings',
                                                     'schedule_start'),
            'schedule_end': values_obj.get_default('res.config.settings',
                                                   'schedule_end')
        }

        cr = self._cr
        # fetch services(products) -start
        cr.execute("SELECT pt.name, pp.id,pt.id as product_template_id, "
                   "(case when pt.type = 'service' "
                   "then pt.duration_in_min "
                   "else 30 end) as duration "
                   "FROM product_product pp "
                   "JOIN product_template pt "
                   "ON (pp.product_tmpl_id = pt.id) where "
                   "pp.active and pt.type='service' ORDER BY pt.name")
        services = cr.dictfetchall()
        for serv in services:
            serv['staff_ids'] = self.env['product.template'].browse(
                serv['product_template_id']).staff_ids.ids
        # fetch services(products) -end

        # fetch customers - start
        cr.execute("SELECT id, CONCAT  (name, ' ', phone) as name "
                   "FROM res_partner ")
        customers = cr.dictfetchall()
        # fetch customers -end

        ir_values_obj = self.env['ir.values']
        default_config_staff_type = ir_values_obj.get_default(
            'pos.config.settings', 'default_config_staff_type')
        config_staff_type = ''
        if default_config_staff_type:
            config_staff_type = 'service_based_staff'
        return [
            time_schedule, services, customers, config_staff_type
        ]
