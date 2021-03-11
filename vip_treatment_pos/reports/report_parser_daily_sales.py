# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, tools
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz


class ReportSaleDetails2(models.AbstractModel):
    _inherit = 'report.pos_staff.report_saledetails2'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False,
                         staff_id=False, customer_id=False, user_id=False):
        res = super(ReportSaleDetails2, self).get_sale_details(date_start, date_stop, staff_id, customer_id, user_id)
        date_stop = max(date_stop, date_start)
        lst_search = [
            ('date_order', '>=', str(date_start)),
            ('date_order', '<=', str(date_stop)),
            ('state', 'in', ['paid', 'invoiced', 'done']),
            ]
        if customer_id:
            lst_search.append(('partner_id', '=', customer_id))
        if user_id:
            lst_search.append(('user_id', '=', user_id))
        orders = self.env['pos.order'].search(lst_search)
        user_currency = self.env.user.company_id.currency_id
        total = 0.0
        vip_total = 0.0
        products_sold2 = {}
        staff_sold = {}
        for order in orders:
            vip_total += order.amt_service_charge
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                if staff_id and staff_id != line.staff_assigned_id.id:
                    continue

                keyy = (line.product_id)
                products_sold2.setdefault(keyy, [0.0, 0.0])
                products_sold2[keyy][0] += line.qty
                products_sold2[keyy][1] += line.after_global_disc_subtotal
                staff_sold.setdefault(line.staff_assigned_id.name, [0.0, 0.0, 0.0, 0.0, 0.0])
                staff_sold[line.staff_assigned_id.name][3] += line.after_global_disc_subtotal
                staff_sold[line.staff_assigned_id.name][3] += line.after_vip_subtotal
                if line.product_id.type == 'consu':
                    staff_sold[line.staff_assigned_id.name][0] += line.after_global_disc_subtotal
                if line.product_id.type == 'product':
                    staff_sold[line.staff_assigned_id.name][1] += line.after_global_disc_subtotal
                if line.product_id.type == 'service':
                    staff_sold[line.staff_assigned_id.name][2] += line.after_global_disc_subtotal
                staff_sold[line.staff_assigned_id.name][4] += line.after_vip_subtotal

        res['staff_summary'] = [{'name': key or 'No Staff', 'consu_value': consu_value, 'product_value': product_value,
                'service_value': service_value, 'vip_value': vip_value, 'amount': round(value, 2)}
               for (key, [consu_value, product_value, service_value, value, vip_value] ) in staff_sold.iteritems()]
        res['vip_total'] = vip_total
        return res