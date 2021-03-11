# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import date, datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64
from dateutil.relativedelta import relativedelta


class PosOrder(models.Model):
    _inherit = "pos.order"

    date_start = fields.Datetime(string='Start Time')
    date_stop = fields.Datetime(string='End Time')

    @api.model
    def create(self, vals):
        date_now = datetime.now()
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        prev_procedure_stop = False
        for lines in vals['lines']:
            # ........POS Session - start value there for service. so assign stop time based on duration.......
            if lines[2].get('procedure_start_val') and not lines[2].get('procedure_stop_val'):
                if lines[2].get('product_id'):
                    duration = 0
                    product = self.env['product.product'].browse(lines[2].get('product_id'))
                    if product.type == 'service':
                        if product.duration_in_min:
                            duration = product.duration_in_min
                        else:
                            duration = 30
                        start_val = lines[2].get('procedure_start_val')
                        [start_hour, start_min] = start_val.split(":")
                        start_hour = int(start_hour)
                        start_min = int(start_min)
                        date_now = date_now.replace(hour=start_hour, minute=start_min, second=0)
                        start_time = pytz.utc.localize(date_now).astimezone(tz)
                        start_time = start_time.replace(tzinfo=None)
                        difference = relativedelta(date_now, start_time)
                        days = difference.days
                        hours = difference.hours
                        minutes = difference.minutes
                        date_now = date_now + timedelta(days=days, hours=hours, minutes=minutes)
                        procedure_stop = date_now + timedelta(days=0, hours=0, minutes=duration)
                        lines[2]['procedure_stop'] = procedure_stop
            # ......POS Session - If no start time for services, Assign start and stop time based on variable prev_procedure_stop.....
            if not lines[2].get('procedure_start_val') and prev_procedure_stop:
                if lines[2].get('product_id'):
                    duration = 0
                    product = self.env['product.product'].browse(lines[2].get('product_id'))
                    if product.type == 'service':
                        if product.duration_in_min:
                            duration = product.duration_in_min
                        else:
                            duration = 30
                        lines[2]['procedure_start'] = prev_procedure_stop
                        procedure_stop = prev_procedure_stop + timedelta(days=0, hours=0, minutes=duration)
                        lines[2]['procedure_stop'] = procedure_stop
            # .............POS Session - Assign previous stop value from pos to a variable prev_procedure_stop.............
            if lines[2].get('procedure_stop_val'):
                stop_val = lines[2].get('procedure_stop_val')
                [stop_hour, stop_min] = stop_val.split(":")
                stop_hour = int(stop_hour)
                stop_min = int(stop_min)
                date_now = date_now.replace(hour=stop_hour, minute=stop_min, second=0)
                stop_time = pytz.utc.localize(date_now).astimezone(tz)
                stop_time = stop_time.replace(tzinfo=None)
                difference = relativedelta(date_now, stop_time)
                days = difference.days
                hours = difference.hours
                minutes = difference.minutes
                date_now = date_now + timedelta(days=days, hours=hours, minutes=minutes)
                prev_procedure_stop  = date_now
            # POS Session - if service1 with start value, then for nxt service assign start n stop value
            if lines[2].get('procedure_stop'):
                if isinstance(lines[2].get('procedure_stop'), datetime):
                    prev_procedure_stop  = lines[2].get('procedure_stop')
        return super(PosOrder, self).create(vals)

    @api.multi
    def _sale_details_notification(self):
        # From Scheduled action: Sales Details Notification
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        selected_date = date.today()
        last_day_selected_month = date(selected_date.year, selected_date.month, 27)
        todayy = datetime.now()
        todayy = todayy.replace(hour=0, minute=0, second=0, microsecond=0)
        today_start = todayy - timedelta(hours=3)
        today_end2 = todayy + timedelta(days=1)
        today_end = today_start + timedelta(days=1)
        month_start2 = todayy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start = month_start2 - timedelta(hours=3)
        pos_config_ids = self.env['pos.config'].search([])
        data = {'date_start': str(today_start), 'date_stop': str(today_end), 'partner_id': False,
                'user_id': False}
        pdf = self.env['report'].get_pdf([], 'pos_daily_report.report_partner_details', data=data)
        attachment_id = self.env['ir.attachment'].create({
            'name': 'Sale Details: ' + str(todayy) + " To " + str(today_end2),
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': 'Sale Details Today.pdf',
            'mimetype': 'application/x-pdf'
        })
        attach = {
            attachment_id.id,
        }
        if selected_date == last_day_selected_month:
            data2 = {'date_start': str(month_start), 'date_stop': str(today_end),
                    'staff_assigned_id': False, 'partner_id': False, 'user_id': False}
            pdf2 = self.env['report'].get_pdf([], 'pos_staff.report_saledetails3', data=data2)
            attachment_id2 = self.env['ir.attachment'].create({
                'name': 'Sale Details: ' + str(month_start2) + " To " + str(today_end2),
                'type': 'binary',
                'datas': base64.encodestring(pdf2),
                'datas_fname': 'Sale Details Month.pdf',
                'mimetype': 'application/x-pdf'
            })
            attach = {
                    attachment_id.id,
                    attachment_id2.id
                }
        # conf = self.env['pos.config.settings'].search([], order='id desc', limit=1)
        # if not conf.email:
        #     warning = {
        #         'title': ' Warning !!!',
        #         'message': "Please enter the Owner email in Pos Configuration."
        #     }
        #     return {'warning': warning}

        from_email = user.company_id.owner_email
        mail_values = {
            'reply_to': from_email,
            'email_to': from_email,
            'subject': 'Sales Report',
            'body_html': """<div>
                                                <p>Hello,</p>
                                                <p>This email was created automatically by Odoo Beauty Manager. Please find the attached sales reports.</p>
                                            </div>
                                            <div>Thank You</div>""",
            'attachment_ids': [(6, 0, attach)]
        }
        self.env['mail.mail'].create(mail_values).send()
        pass


class pos_staff_oreder_line(models.Model):
    _inherit = "pos.order.line"
    _description = "Point of Sale Extension"

    @api.model
    def _default_start(self):
        for order in self:
            if order.order_id:
                if order.order_id.date_stop:
                    return order.order_id.date_stop
                elif order.order_id.date_start:
                    return order.order_id.date_start
        return

    staff_assigned_id = fields.Many2one('hr.employee', string='Employee')
    offer_string = fields.Char(string='Offer String')
    procedure_start = fields.Datetime(string='Start Time', default=_default_start)
    procedure_stop = fields.Datetime(string='End Time')
    procedure_start_val = fields.Char(string='Start Time')
    procedure_stop_val = fields.Char(string='End Time')

    @api.model
    def create(self, vals):
        date_now = datetime.now()
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        if vals.get('procedure_start_val'):
            start_val = vals.get('procedure_start_val')
            [start_hour, start_min] = start_val.split(":")
            start_hour = int(start_hour)
            start_min = int(start_min)
            date_now = date_now.replace(hour=start_hour, minute=start_min, second=0)
            start_time = pytz.utc.localize(date_now).astimezone(tz)
            start_time = start_time.replace(tzinfo=None)
            difference = relativedelta(date_now, start_time)
            days = difference.days
            hours = difference.hours
            minutes = difference.minutes
            date_now = date_now + timedelta(days=days, hours=hours, minutes=minutes)
            vals['procedure_start'] = date_now
            if vals.get('order_id'):
                order_id = vals.get('order_id')
                pos_obj = self.env['pos.order'].browse(order_id)
                if pos_obj:
                    start_date = pos_obj.date_start
                    start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                    if start_date > date_now:
                        pos_obj.date_start = date_now
        if vals.get('procedure_stop_val'):
            stop_val = vals.get('procedure_stop_val')
            [stop_hour, stop_min] = stop_val.split(":")
            stop_hour = int(stop_hour)
            stop_min = int(stop_min)
            date_now = date_now.replace(hour=stop_hour, minute=stop_min, second=0)
            stop_time = pytz.utc.localize(date_now).astimezone(tz)
            stop_time = stop_time.replace(tzinfo=None)
            difference = relativedelta(date_now, stop_time)
            days = difference.days
            hours = difference.hours
            minutes = difference.minutes
            date_now = date_now + timedelta(days=days, hours=hours, minutes=minutes)
            vals['procedure_stop'] = date_now
            if vals.get('order_id'):
                order_id = vals.get('order_id')
                pos_obj = self.env['pos.order'].browse(order_id)
                if pos_obj:
                    stop_date = pos_obj.date_stop
                    stop_date = datetime.strptime(stop_date, '%Y-%m-%d %H:%M:%S')
                    if stop_date < date_now:
                        pos_obj.date_stop = date_now
        return super(pos_staff_oreder_line, self).create(vals)

    def _order_line_fields(self, vals):
        res = super(pos_staff_oreder_line, self)._order_line_fields(vals)
        return res
    pass


class POSConfiguration(models.TransientModel):
    _inherit = 'pos.config.settings'

    @api.model
    def _get_default_email(self):
        last_ids = self.env['pos.config.settings'].search([], order='id desc', limit=1)
        email = last_ids.email
        if not email:
            email = self.env.user.email
        return email

    email = fields.Char('Owner Email(Multiple mail ids must be separated by commas)', default=_get_default_email)

    @api.model
    def get_default_email(self, fields):
        last_ids = self.env['pos.config.settings'].search([], order='id desc', limit=1)
        email = last_ids.email
        if not email:
            email = self.env.user.email
        return {'email': email}


class pos_details_report(models.TransientModel):
    _inherit = "pos.details.wizard"

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
    staff_assigned_id = fields.Many2one('hr.employee', string='Employee')
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)])
    user_id = fields.Many2one('res.users', string="Responsible person")

    @api.multi
    def generate_report2(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date,
                'user_id': self.user_id.id,
                'staff_assigned_id': self.staff_assigned_id.id, 'partner_id': self.partner_id.id}
        return self.env['report'].get_action([], 'pos_staff.report_saledetails2', data=data)

    @api.multi
    def generate_report(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date,
                'user_id': self.user_id.id,
                'staff_assigned_id': self.staff_assigned_id.id, 'partner_id': self.partner_id.id}
        return self.env['report'].get_action([], 'point_of_sale.report_saledetails', data=data)

    @api.multi
    def email_report(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        data = {'date_start': self.start_date,
                'date_stop': self.end_date,
                'user_id': self.user_id.id,
                'staff_assigned_id': self.staff_assigned_id.id,
                'partner_id': self.partner_id.id}
        pdf = self.env['report'].get_pdf([], 'point_of_sale.report_saledetails', data=data)
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
        start_date = pytz.utc.localize(start_date).astimezone(tz)
        start_date = start_date.replace(tzinfo=None)
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")
        end_date = pytz.utc.localize(end_date).astimezone(tz)
        end_date = end_date.replace(tzinfo=None)
        attachment_id = self.env['ir.attachment'].create({
                    'name': 'Sale Details: ' + str(start_date) + " To " + str(end_date),
                    'type': 'binary',
                    'datas': base64.encodestring(pdf),
                    'datas_fname': 'Sale Details.pdf',
                    'mimetype': 'application/x-pdf'
                })
        # conf = self.env['pos.config.settings'].search([], order='id desc', limit=1)
        # if not conf.email:
        #     warning = {
        #         'title': ' Warning !!!',
        #         'message': "Please enter the Owner email in Pos Configuration."
        #     }
        #     return {'warning': warning}

        from_email = user.company_id.owner_email
        mail_values = {
            # 'email_from': from_email,
            'reply_to': from_email,
            'email_to': from_email,
            'subject': 'Sale Details: ' + str(start_date) + ' To ' + str(end_date),
            'body_html': """<div>
                                        <p>Hello,</p>
                                        <p>This email was created automatically by Odoo Beauty Manager. Please find the attached sales report.</p>
                                    </div>
                                    <div>Thank You</div>""",
            'attachment_ids': [(4, attachment_id.id)]
        }
        self.env['mail.mail'].create(mail_values).send()
        # if result:
        #     message = "Sale Details Report is sent by Mail !!"
        #     self.env.user.notify_info(message, title='Email Sent', sticky=False)

    @api.multi
    def email_report2(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'config_ids': self.pos_config_ids.ids,
                'staff_assigned_id': self.staff_assigned_id.id, 'partner_id': self.partner_id.id}
        pdf = self.env['report'].get_pdf([], 'pos_staff.report_saledetails2', data=data)
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
        start_date = pytz.utc.localize(start_date).astimezone(tz)
        start_date = start_date.replace(tzinfo=None)
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")
        end_date = pytz.utc.localize(end_date).astimezone(tz)
        end_date = end_date.replace(tzinfo=None)
        attachment_id = self.env['ir.attachment'].create({
                    'name': 'Sale Details: ' + str(start_date) + " To " + str(end_date),
                    'type': 'binary',
                    'datas': base64.encodestring(pdf),
                    'datas_fname': 'Sale Details.pdf',
                    'mimetype': 'application/x-pdf'
                })
        # conf = self.env['pos.config.settings'].search([], order='id desc', limit=1)
        # if not conf.email:
        #     warning = {
        #         'title': ' Warning !!!',
        #         'message': "Please enter the Owner email in Pos Configuration."
        #     }
        #     return {'warning': warning}

        from_email = user.company_id.owner_email
        mail_values = {
            # 'email_from': from_email,
            'reply_to': from_email,
            'email_to': from_email,
            'subject': 'Sale Details: ' + str(start_date) + ' To ' + str(end_date),
            'body_html': """<div>
                                        <p>Hello,</p>
                                        <p>This email was created automatically by Odoo Beauty Manager. Please find the attached sales report.</p>
                                    </div>
                                    <div>Thank You</div>""",
            'attachment_ids': [(4, attachment_id.id)]
        }
        self.env['mail.mail'].create(mail_values).send()
        # if result:
        #     message = "Sale Details Report is sent by Mail !!"
        #     self.env.user.notify_info(message, title='Email Sent', sticky=False)


class ReportSaleDetails(models.AbstractModel):

    _inherit = 'report.point_of_sale.report_saledetails'

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
                # key = (line.product_id, line.price_unit, line.price_subtotal_incl, line.discount,
                #        line.staff_assigned_id, line.offer_string)
                # products_sold.setdefault(key, 0.0)
                # products_sold[key] += line.qty

                keyy = (line.order_id.partner_id,line.product_id, line.price_unit, line.discount,
                       line.staff_assigned_id, line.offer_string)
                products_sold2.setdefault(keyy, [0.0, 0.0])
                products_sold2[keyy][0] += line.qty
                products_sold2[keyy][1] += line.price_subtotal_incl

                staff_sold.setdefault(line.staff_assigned_id.name, 0.0)
                staff_sold[line.staff_assigned_id.name] += line.price_subtotal_incl

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
        ddd = {
            'total_paid': user_currency.round(total),
            'payments': payments,
            'date_from': date_start,
            'date_to': date_stop,
            'staff_summary': [{'name': key or 'No Staff', 'amount': round(value, 2)} for (key, value ) in staff_sold.iteritems()],
            'company_name': self.env.user.company_id.name,
            'taxes': taxes.values(),
            'products': sorted([{
                'product_id': product.id,
                'partner_name': partner.name or "",
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'price_subtotal_incl': price_subtotal_incl,
                'discount': discount,
                'staff': staff.name,
                'offer_string': offer_string.split('--')[-1].strip() if offer_string else '',
                'uom': product.uom_id.name
            } for (partner,product, price_unit, discount, staff, offer_string), [qty, price_subtotal_incl] in products_sold2.items()], key=lambda l: l['product_name'])
        }
        return ddd

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['date_start'], data['date_stop'], data['staff_assigned_id'],
                                          data['partner_id'], data['user_id']))
        return self.env['report'].render('point_of_sale.report_saledetails', data)


class PosOrderReportInherit(models.Model):
    _inherit = "report.pos.order"
    _description = "Point of Sale Orders Statistics"

    staff_assigned_id = fields.Many2one('hr.employee', string='Employee')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_pos_order')
        self._cr.execute("""
                CREATE OR REPLACE VIEW report_pos_order AS (
                    SELECT
                        MIN(l.id) AS id,
                        COUNT(*) AS nbr_lines,
                        s.date_order AS date,
                        SUM(l.qty) AS product_qty,
                        SUM(l.qty * l.price_unit) AS price_sub_total,
                        SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total,
                        SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount,
                        (SUM(l.qty*l.price_unit)/SUM(l.qty * u.factor))::decimal AS average_price,
                        SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                        s.id as order_id,
                        s.partner_id AS partner_id,
                        s.state AS state,
                        s.user_id AS user_id,
                        s.location_id AS location_id,
                        s.company_id AS company_id,
                        s.sale_journal AS journal_id,
                        l.product_id AS product_id,
                        pt.categ_id AS product_categ_id,
                        p.product_tmpl_id,
                        ps.config_id,
                        pt.pos_categ_id,
                        pc.stock_location_id,
                        s.pricelist_id,
                        s.session_id,
                        s.invoice_id IS NOT NULL AS invoiced,
                        l.staff_assigned_id
                    FROM pos_order_line AS l
                        LEFT JOIN pos_order s ON (s.id=l.order_id)
                        LEFT JOIN product_product p ON (l.product_id=p.id)
                        LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom u ON (u.id=pt.uom_id)
                        LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                        LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
                        LEFT JOIN hr_employee hr on (hr.id=l.staff_assigned_id)
                    GROUP BY
                        s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                        s.user_id, s.location_id, s.company_id, s.sale_journal,
                        s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
                        l.product_id,
                        pt.categ_id, pt.pos_categ_id,
                        p.product_tmpl_id,
                        ps.config_id,
                        pc.stock_location_id,
                        l.staff_assigned_id
                    HAVING
                        SUM(l.qty * u.factor) != 0
                )
            """)
