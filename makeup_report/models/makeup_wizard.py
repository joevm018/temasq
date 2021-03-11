# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import io
# from odoo.report.report_xlsx import ReportXlsx
from datetime import datetime

from odoo import api, fields, models
from odoo.tools.misc import xlwt


class FocWizard(models.TransientModel):
    _name = 'makeup.wizard'

    start_date = fields.Date('Start Date', default=fields.Date.context_today, required=True)
    end_date = fields.Date('End Date', default=fields.Date.context_today, required=True)
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Cashier")
    show_details = fields.Boolean(string="Detailed")
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),
                              ('get', 'get')], default='choose')
    type = fields.Selection([('create', 'Created Date'),
                             ('appt', 'Appointment Date')], default='appt', required=True)
    name = fields.Char('File Name', readonly=True)

    @api.multi
    def generate_excel_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Makeup Report')
        start_date = self.start_date
        end_date = self.end_date
        bold = xlwt.easyxf("pattern: pattern solid, fore-colour light_turquoise;"
                           "align: wrap on, horiz center, vert center;font: bold on;"
                           "borders: left thin, right thin, top thin, bottom thin;"
                           "font: name Times New Roman, color black;", num_format_str='#,##0.00')
        bold_grey = xlwt.easyxf("pattern: pattern solid, fore-colour grey25;"
                                "align: wrap on, horiz center, vert center;font: bold on;"
                                "borders: left thin, right thin, top thin, bottom thin;"
                                "font: name Times New Roman, color black;", num_format_str='#,##0.00')
        normal = xlwt.easyxf("align: wrap on, horiz center, vert center;"
                             "borders: left thin, right thin, top thin, bottom thin;"
                             "font: name Times New Roman;", num_format_str='#,##0.00')
        if self.show_details:
            if self.type == 'create':
                lst_search = [('state', 'in', ['paid', 'invoiced', 'done']),
                              ('create_date', '>=', start_date),
                              ('create_date', '<=', end_date)]
            else:
                lst_search = [('state', 'in', ['paid', 'invoiced', 'done']),
                              ('date_order', '>=', start_date),
                              ('date_order', '<=', end_date)]
            if self.partner_id:
                lst_search.append(('partner_id', '=', self.partner_id.id))
            if self.user_id:
                lst_search.append(('write_uid', '=', self.user_id.id))
            orders = self.env['pos.order'].search(lst_search, order='date_order asc')
            r = 1
            worksheet.write_merge(r, r, 0, 5, 'MAKEUP DETAILS REPORT', bold_grey)
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 3
            sl_no = 1
            c = 0
            r += 2
            total = 0
            total_adv = 0
            total_paid = 0
            total_due = 0
            output_header = ['SR.NO', 'DATE', 'APPOINTMENT DATE', 'CLIENT NAME', 'MOBILE',
                             'SERVICE DETAILS', 'TOTAL AMOUNT', 'PAID ADVANCE', 'PAID', 'DUE AMOUNT',
                             'MAKEUP ARTIST', 'NOTE']
            for item in output_header:
                worksheet.write(r, c, item, bold)
                col = worksheet.col(c)
                if c == 0:
                    col.width = 900 * 2
                elif c == 5:
                    col.width = 900 * 8
                else:
                    col.width = 900 * 4
                worksheet.row(r).height_mismatch = True
                worksheet.row(r).height = 220 * 3
                c += 1
            r += 1
            for ord in orders:
                data = []
                date_order = ''
                adv = False
                adv_paid = 0
                paid = 0
                for pay in ord.statement_ids:
                    if pay.is_advance:
                        adv = True
                        adv_paid += pay.amount
                    else:
                        paid += pay.amount
                if adv:
                    services = ''
                    artist = []
                    for line in ord.lines:
                        services += line.product_id.name + ', '
                        if line.staff_assigned_id and line.staff_assigned_id.name not in artist:
                            artist.append(line.staff_assigned_id.name)
                    artist_name = ''
                    for art in artist:
                        artist_name += art + ','
                    data.append(str(int(sl_no)))
                    sl_no += 1
                    create_date = ''
                    if ord.create_date:
                        create_date = datetime.strptime(ord.create_date, '%Y-%m-%d %H:%M:%S').date()
                        create_date = create_date.strftime('%d/%m/%Y')
                    data.append(create_date)
                    if ord.date_order:
                        date_order = datetime.strptime(ord.date_order, '%Y-%m-%d %H:%M:%S').date()
                        date_order = date_order.strftime('%d/%m/%Y')
                    data.append(date_order)
                    if ord.partner_id:
                        data.append(ord.partner_id.name)
                        data.append(ord.partner_id.phone)
                    else:
                        data.append('')
                        data.append('')
                    data.append(services)
                    data.append(ord.amount_total)
                    total += ord.amount_total
                    total_adv += adv_paid
                    total_paid += paid
                    total_due += ord.amount_total - adv_paid - paid
                    data.append(adv_paid)
                    data.append(paid)
                    data.append(ord.amount_total - adv_paid - paid)
                    data.append(artist_name)
                    if ord.note:
                        data.append(ord.note)
                    else:
                        data.append('')
                    c = 0
                    for item in data:
                        worksheet.write(r, c, item, normal)
                        c += 1
                    r += 1
            worksheet.write_merge(r, r, 0, 5, 'TOTAL', bold)
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 2
            c = 6
            worksheet.write(r, c, total, bold)
            c += 1
            worksheet.write(r, c, total_adv, bold)
            c += 1
            worksheet.write(r, c, total_paid, bold)
            c += 1
            worksheet.write(r, c, total_due, bold)
            c += 1
            worksheet.write_merge(r, r, c, c + 1, '', bold)
        else:
            lst_search = [('state', 'in', ['paid', 'invoiced', 'done']),
                          ('date_order', '>=', start_date),
                          ('date_order', '<=', end_date)]
            if self.partner_id:
                lst_search.append(('partner_id', '=', self.partner_id.id))
            if self.user_id:
                lst_search.append(('write_uid', '=', self.user_id.id))
            orders = self.env['pos.order'].search(lst_search, order='date_order asc')
            r = 1
            worksheet.write_merge(r, r, 0, 4, 'MAKEUP SERVICES -SUMMERY', bold_grey)
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 3
            sl_no = 1
            c = 0
            r += 2
            total = 0
            output_header = ['SR.NO', 'DATE', 'MAKEUP ARTIST', 'TOTAL AMOUNT', 'NOTE/REMARK']
            for item in output_header:
                worksheet.write(r, c, item, bold)
                col = worksheet.col(c)
                if c == 0:
                    col.width = 900 * 2
                elif c == 2:
                    col.width = 900 * 8
                else:
                    col.width = 900 * 4
                worksheet.row(r).height_mismatch = True
                worksheet.row(r).height = 220 * 3
                c += 1
            r += 1
            order_data = {}
            for ord in orders:
                adv = False
                for pay in ord.statement_ids:
                    if pay.is_advance:
                        adv = True
                if adv:
                    date_order = datetime.strptime(ord.date_order, '%Y-%m-%d %H:%M:%S').date()
                    date_order = date_order.strftime('%d/%m/%Y')
                    if date_order not in order_data.keys():
                        order_data[date_order] = {}
                    for line in ord.lines:
                        if line.staff_assigned_id:
                            if line.staff_assigned_id not in order_data[date_order].keys():
                                order_data[date_order][line.staff_assigned_id] = 0
                            order_data[date_order][line.staff_assigned_id] += line.after_global_disc_subtotal
                        else:
                            if 'No Staff' not in order_data[date_order].keys():
                                order_data[date_order]['No Staff'] = 0
                            order_data[date_order]['No Staff'] += line.after_global_disc_subtotal
            c = 0
            for ord_date in sorted(order_data.keys()):
                for staff in order_data[ord_date]:
                    worksheet.write(r, c, str(int(sl_no)), normal)
                    sl_no += 1
                    c += 1
                    worksheet.write(r, c, ord_date, normal)
                    c += 1
                    if staff == 'No Staff':
                        worksheet.write(r, c, staff, normal)
                    else:
                        worksheet.write(r, c, staff.name, normal)
                    c += 1
                    worksheet.write(r, c, order_data[ord_date][staff], normal)
                    total += order_data[ord_date][staff]
                    c += 1
                    worksheet.write(r, c, '', normal)
                    c += 1
                    c = 0
                    r += 1
            worksheet.write_merge(r, r, 0, 2, 'TOTAL', bold)
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 2
            c = 3
            worksheet.write(r, c, total, bold)
            c += 1
            worksheet.write(r, c, '', bold)
        buf = io.BytesIO()
        workbook.save(buf)
        out = base64.encodestring(buf.getvalue())
        name = "Makeup_report" + ".xls"
        self.write({'state': 'get', 'data': out, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'makeup.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
