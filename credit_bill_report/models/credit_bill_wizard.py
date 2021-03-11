# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import io
# from odoo.report.report_xlsx import ReportXlsx
from datetime import datetime

from odoo import api, fields, models
from odoo.tools.misc import xlwt


class CreditBillWizard(models.TransientModel):
    _name = 'credit.bill.wizard'

    start_date = fields.Date('Start Date', default=fields.Date.context_today, required=True)
    end_date = fields.Date('End Date', default=fields.Date.context_today, required=True)
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Cashier")
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),
                              ('get', 'get')], default='choose')
    name = fields.Char('File Name', readonly=True)

    @api.multi
    def generate_excel_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Credit Bill Report')
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
        lst_search = [('state', 'in', ['paid', 'invoiced', 'done']),
                      ('date_order', '>=', start_date),
                      ('date_order', '<=', end_date)]
        if self.partner_id:
            lst_search.append(('partner_id', '=', self.partner_id.id))
        if self.user_id:
            lst_search.append(('write_uid', '=', self.user_id.id))
        orders = self.env['pos.order'].search(lst_search, order='date_order asc')
        r = 1
        worksheet.write_merge(r, r, 0, 7, 'CREDIT/DUE BILL REPORT', bold_grey)
        worksheet.row(r).height_mismatch = True
        worksheet.row(r).height = 220 * 3
        sl_no = 1
        c = 0
        r += 2
        total = 0
        total_paid = 0
        total_due = 0
        output_header = ['SR.NO', 'DATE', 'CLIENT NAME', 'SERVICE DETAILS', 'AMOUNT',
                         'PAID AMOUNT', 'DUE AMOUNT', 'REMARKS']
        for item in output_header:
            worksheet.write(r, c, item, bold)
            col = worksheet.col(c)
            if c == 0:
                col.width = 900 * 2
            elif c == 3:
                col.width = 900 * 10
            else:
                col.width = 900 * 4
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 3
            c += 1
        r += 1
        for ord in orders:
            data = []
            date_order = ''
            credit = False
            paid = 0
            for pay in ord.statement_ids:
                if pay.journal_id.is_pay_later:
                    if ord.invoice_id:
                        if ord.invoice_id.residual > 0:
                            credit = True
                    else:
                        credit = True
                else:
                    paid += pay.amount
            if credit:
                services = ''
                artist = []
                for line in ord.lines:
                    services += line.product_id.name + ', '
                    if line.staff_assigned_id and line.staff_assigned_id.name not in artist:
                        artist.append(line.staff_assigned_id.name)
                data.append(str(int(sl_no)))
                sl_no += 1
                if ord.date_order:
                    date_order = datetime.strptime(ord.date_order, '%Y-%m-%d %H:%M:%S').date()
                    date_order = date_order.strftime('%d/%m/%Y')
                data.append(date_order)
                if ord.partner_id:
                    data.append(ord.partner_id.name)
                else:
                    data.append('')
                data.append(services)
                data.append(ord.amount_total)
                total += ord.amount_total
                if ord.invoice_id and ord.invoice_id.state in ('open', 'done'):
                    total_paid += ord.amount_total - ord.invoice_id.residual
                    total_due += ord.invoice_id.residual
                    data.append(ord.amount_total - ord.invoice_id.residual)
                    data.append(ord.invoice_id.residual)
                else:
                    total_paid += paid
                    total_due += ord.amount_total - paid
                    data.append(paid)
                    data.append(ord.amount_total - paid)
                if ord.note:
                    data.append(ord.note)
                else:
                    data.append('')
                c = 0
                for item in data:
                    worksheet.write(r, c, item, normal)
                    c += 1
                r += 1
        worksheet.write_merge(r, r, 0, 3, 'TOTAL', bold)
        worksheet.row(r).height_mismatch = True
        worksheet.row(r).height = 220 * 2
        c = 4
        worksheet.write(r, c, total, bold)
        c += 1
        worksheet.write(r, c, total_paid, bold)
        c += 1
        worksheet.write(r, c, total_due, bold)
        c += 1
        worksheet.write(r, c, '', bold)
        buf = io.BytesIO()
        workbook.save(buf)
        out = base64.encodestring(buf.getvalue())
        name = "Credit_Bill_Report" + ".xls"
        self.write({'state': 'get', 'data': out, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'credit.bill.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
