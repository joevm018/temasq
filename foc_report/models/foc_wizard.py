# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import io
# from odoo.report.report_xlsx import ReportXlsx
from datetime import datetime

from odoo import api, fields, models
from odoo.tools.misc import xlwt


class FocWizard(models.TransientModel):
    _name = 'foc.wizard'

    start_date = fields.Date('Start Date', default=fields.Date.context_today)
    end_date = fields.Date('End Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Cashier")
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),  # choose language
                              ('get', 'get')], default='choose')
    name = fields.Char('File Name', readonly=True)

    @api.multi
    def generate_excel_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('FOC Report')
        lst_search = [('state', 'in', ['paid', 'invoiced', 'done'])]
        start_date = self.start_date
        end_date = self.end_date
        if start_date:
            lst_search.append(('date_order', '>=', start_date))
        if end_date:
            lst_search.append(('date_order', '<=', end_date))
        if self.partner_id:
            lst_search.append(('partner_id', '=', self.partner_id.id))
        if self.user_id:
            lst_search.append(('write_uid', '=', self.user_id.id))
        orders = self.env['pos.order'].search(lst_search, order='date_order asc')
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
        normal_grey = xlwt.easyxf("pattern: pattern solid, fore-colour grey25;"
                                  "align: wrap on, horiz center, vert center;"
                                  "borders: left thin, right thin, top thin, bottom thin;"
                                  "font: name Times New Roman;", num_format_str='#,##0.00')
        r = 1
        worksheet.write_merge(r, r, 0, 5, 'FREE OF CHARGE REPORT', bold_grey)
        worksheet.row(r).height_mismatch = True
        worksheet.row(r).height = 220 * 3
        sl_no = 1
        c = 0
        r += 2
        total = 0
        output_header = ['SR.NO', 'DATE', 'CLIENT NAME', 'SERVICE DETAILS', 'AMOUNT', 'APPROVED BY']
        for item in output_header:
            worksheet.write(r, c, item, bold)
            col = worksheet.col(c)
            if c == 0:
                col.width = 900 * 2
            elif c == 3:
                col.width = 1200 * 8
            else:
                col.width = 900 * 6
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 2
            c += 1
        r += 1
        for ord in orders:
            data = []
            date_order = ''
            foc = 0
            if ord.is_order_foc:
                data.append(str(int(sl_no)))
                sl_no += 1
                if ord.date_order:
                    date_order = datetime.strptime(ord.date_order, '%Y-%m-%d %H:%M:%S').date()
                    date_order = date_order.strftime('%d/%m/%Y')
                data.append(date_order)
                if ord.partner_id:
                    data.append(ord.partner_id.name)
                    data.append('')
                else:
                    data.append('')
                    data.append('')
                amt = 0
                for line in ord.lines:
                    amt += line.qty * line.price_unit
                total += amt
                data.append(amt)
                data.append(ord.write_uid.name)
                c = 0
                for item in data:
                    worksheet.write(r, c, item, normal_grey)
                    c += 1
                r += 1
                for line in ord.lines:
                    data = []
                    data.append('')
                    data.append('')
                    data.append('')
                    data.append(line.product_id.name)
                    data.append(line.qty * line.price_unit)
                    data.append('')
                    c = 0
                    for item in data:
                        worksheet.write(r, c, item, normal)
                        c += 1
                    r += 1
            else:
                for line in ord.lines:
                    if line.is_order_line_foc:
                        data = []
                        if not foc:
                            data.append(str(int(sl_no)))
                            sl_no += 1
                            if ord.date_order:
                                date_order = datetime.strptime(ord.date_order, '%Y-%m-%d %H:%M:%S').date()
                                date_order = date_order.strftime('%d/%m/%Y')
                            data.append(date_order)
                            if ord.partner_id:
                                data.append(ord.partner_id.name)
                                data.append('')
                            else:
                                data.append('')
                                data.append('')
                            amt = 0
                            for l in ord.lines:
                                if l.is_order_line_foc:
                                    amt += line.qty * line.price_unit
                            data.append(amt)
                            data.append(ord.write_uid.name)
                            total += amt
                            c = 0
                            for item in data:
                                worksheet.write(r, c, item, normal_grey)
                                c += 1
                            r += 1
                        if 1:
                            data = []
                            data.append('')
                            data.append('')
                            data.append('')
                            data.append(line.product_id.name)
                            data.append(line.qty * line.price_unit)
                            data.append('')
                            c = 0
                            for item in data:
                                worksheet.write(r, c, item, normal)
                                c += 1
                            r += 1
                        foc = 1
        worksheet.write_merge(r, r, 0, 3, 'TOTAL', bold)
        worksheet.row(r).height_mismatch = True
        worksheet.row(r).height = 220 * 2
        c = 4
        worksheet.write(r, c, total, bold)
        c += 1
        worksheet.write(r, c, '', bold)
        buf = io.BytesIO()
        workbook.save(buf)
        out = base64.encodestring(buf.getvalue())
        name = "FOC_report" + ".xls"
        self.write({'state': 'get', 'data': out, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'foc.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
