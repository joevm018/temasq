# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz


class ReportSaleDetails3(models.AbstractModel):
    _inherit = 'report.pos_staff.report_saledetails3'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False,
                         staff_id=False, customer_id=False, user_id=False):
        res = super(ReportSaleDetails3, self).get_sale_details(date_start, date_stop, staff_id, customer_id, user_id)
        date_stop = max(date_stop, date_start)
        startt = date_start
        stopp = date_stop
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        date_start = pytz.utc.localize(datetime.strptime(str(date_start), '%Y-%m-%d %H:%M:%S')).astimezone(tz)
        start = date_start.strftime('%m/%d/%Y %H:%M:%S')
        date_start = date_start - timedelta(hours=3)
        date_stop = pytz.utc.localize(datetime.strptime(str(date_stop), '%Y-%m-%d %H:%M:%S')).astimezone(tz)
        stop = date_stop.strftime('%m/%d/%Y %H:%M:%S')
        date_stop = date_stop - timedelta(hours=3)
        date_start2 = date_start
        date_sold = {}
        while date_start2 != date_stop:
            date_stop2 = date_start2 + timedelta(hours=24)
            lst_search = [
                ('date_order', '>=', str(date_start2)),
                ('date_order', '<=', str(date_stop2)),
                ('state', 'in', ['paid', 'invoiced', 'done']),
            ]
            orders = self.env['pos.order'].search(lst_search)
            amt = 0
            for order in orders:
                amt += order.amount_total
            date_start2 = date_stop2
            date_add = date_stop2.strftime('%m/%d/%Y')
            date_sold.setdefault(date_add, amt)

        lst_search = [
            ('date_order', '>=', str(startt)),
            ('date_order', '<=', str(stopp)),
            ('state', 'in', ['paid', 'invoiced', 'done']),
        ]
        if customer_id:
            lst_search.append(('partner_id', '=', customer_id))
        orders = self.env['pos.order'].search(lst_search)
        user_currency = self.env.user.company_id.currency_id
        total = 0.0
        products_sold2 = {}
        staff_sold = {}
        taxes = {}
        VIP_price_subtotal_incl = 0.00
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                VIP_price_subtotal_incl += line.after_vip_subtotal
                if staff_id and staff_id != line.staff_assigned_id.id:
                    continue
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


    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['date_start'], data['date_stop'], data['staff_assigned_id'],
                                          data['partner_id'], data['user_id']))
        return self.env['report'].render('pos_staff.report_saledetails3', data)