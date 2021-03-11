# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.pos_daily_report.report_partner_details'

    @api.model
    def get_partner_details(self, date_start=False, date_stop=False, partner_id=False, user_id=False):
        res = super(ReportSaleDetails, self).get_partner_details(date_start, date_stop, partner_id, user_id)
        VIP_price_subtotal_incl = 0.00
        user_currency = self.env.user.company_id.currency_id
        total = 0.0
        products_sold2 = {}
        staff_sold = {}
        taxes = {}
        for x in res['info']['content']:
            for order in x['order_line']:
                if user_currency != order.pricelist_id.currency_id:
                    total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
                else:
                    total += order.amount_total
                currency = order.session_id.currency_id
                for line in order.lines:
                    VIP_price_subtotal_incl += line.after_vip_subtotal
                    keyy = (line.order_id.partner_id, line.product_id, line.price_unit, line.discount,
                            line.staff_assigned_id, line.offer_string)
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
                                     'service_value': service_value, 'vip_value': vip_value, 'amount': round(value, 2)} for
                                    (key, [consu_value, product_value, service_value, value, vip_value]) in staff_sold.iteritems()]
        res['VIP_price_subtotal_incl'] = VIP_price_subtotal_incl
        return res