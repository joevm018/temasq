# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, tools
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz


class ReportSaleDetails2(models.AbstractModel):
    _name = 'report.pos_staff.report_saledetails2'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False,
                         staff_id=False, customer_id=False, user_id=False):
        """ Serialise the orders of the day information

        params: date_start, date_stop string representing the datetime of order
        """
        today = fields.Datetime.from_string(fields.Date.context_today(self))

        # avoid a date_stop smaller than date_start
        date_stop = max(date_stop, date_start)
        lst_search = [
            ('date_order', '>=', str(date_start)),
            ('date_order', '<', str(date_stop)),
            ('state', 'in', ['paid', 'invoiced', 'done']),
            ]
        if customer_id:
            lst_search.append(('partner_id', '=', customer_id))
        if user_id:
            lst_search.append(('cashier_name', '=', user_id))
        orders = self.env['pos.order'].search(lst_search)
        user_currency = self.env.user.company_id.currency_id
        total = 0.0
        # products_sold = {}
        products_sold2 = {}
        staff_sold = {}
        taxes = {}
        for order in orders:
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

                staff_sold.setdefault(line.staff_assigned_id.name, [0.0, 0.0, 0.0, 0.0])
                staff_sold[line.staff_assigned_id.name][3] += line.after_global_disc_subtotal
                if line.product_id.type == 'consu':
                    staff_sold[line.staff_assigned_id.name][0] += line.after_global_disc_subtotal
                if line.product_id.type == 'product':
                    staff_sold[line.staff_assigned_id.name][1] += line.after_global_disc_subtotal
                if line.product_id.type == 'service':
                    staff_sold[line.staff_assigned_id.name][2] += line.after_global_disc_subtotal

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'total': 0.0})
                        total_tax = taxes[tax['id']]['total'] + tax['amount']
                        taxes[tax['id']]['total'] = round(total_tax, 2)
        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
        if st_line_ids:
            self.env.cr.execute("""
                SELECT aj.name, sum(amount) total
                FROM account_bank_statement_line AS absl,
                     account_bank_statement AS abs,
                     account_journal AS aj 
                WHERE absl.statement_id = abs.id
                    AND abs.journal_id = aj.id 
                    AND absl.id IN %s 
                GROUP BY aj.name
            """, (tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        if date_start:
            date_start = pytz.utc.localize(datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
        if date_stop:
            date_stop = pytz.utc.localize(datetime.strptime(date_stop, '%Y-%m-%d %H:%M:%S')).astimezone(tz)

        date_start = date_start.strftime('%m/%d/%Y %H:%M:%S')
        date_stop = date_stop.strftime('%m/%d/%Y %H:%M:%S')
        user_name = False
        if user_id:
            user_obj = self.env['res.users'].search([('id', '=', user_id)])
            if user_obj:
                user_name = user_obj.name
        staff_name = self.env['hr.employee'].browse(staff_id).name
        partner_name = self.env['res.partner'].browse(customer_id).name
        return {
            'total_paid': user_currency.round(total),
            'payments': payments,
            'date_from': date_start,
            'date_to': date_stop,
            'user_id': user_name,
            'staff_id': staff_id,
            'staff_name': staff_name,
            'partner_name': partner_name,
            'staff_summary': [{'name': key or 'No Staff', 'consu_value': consu_value, 'product_value': product_value, 'service_value': service_value, 'amount': round(value, 2)} for (key, [consu_value, product_value, service_value, value] ) in staff_sold.iteritems()],
            'company_name': self.env.user.company_id.name,
            'taxes': taxes.values(),
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'type': product.type,
                'code': product.default_code,
                'quantity': qty,
                'price_subtotal_incl': after_global_disc_subtotal,
                'uom': product.uom_id.name
            } for (product), [qty, after_global_disc_subtotal] in products_sold2.items()], key=lambda l: l['product_name'])
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['date_start'], data['date_stop'], data['staff_assigned_id'],
                                          data['partner_id'], data['user_id']))
        return self.env['report'].render('pos_staff.report_saledetails2', data)
