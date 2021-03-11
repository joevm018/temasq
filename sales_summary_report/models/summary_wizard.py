# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
# from odoo.report.report_xlsx import ReportXlsx
from datetime import datetime
import base64
from odoo.tools.misc import xlwt
import io


class SummaryWizard(models.TransientModel):
    _name = 'summary.wizard'

    start_date = fields.Date('Start Date', default=fields.Date.context_today)
    end_date = fields.Date('End Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Cashier")
    detailed = fields.Boolean('Show details')
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),  # choose language
                              ('get', 'get')], default='choose')
    name = fields.Char('File Name', readonly=True)

    @api.multi
    def generate_excel_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Sales Report')
        # worksheet.filter_column(0, 'Region == East')
        #
        # worksheet.filter_column('A', 'x > 2000')
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
            lst_search.append(('cashier_name', '=', self.user_id.id))
        orders = self.env['pos.order'].search(lst_search, order='date_order asc')
        bold = xlwt.easyxf("pattern: pattern solid, fore-colour light_turquoise;"
                           "align: wrap on, horiz center, vert center;font: bold on;"
                           "borders: left thin, right thin, top thin, bottom thin;"
                           "font: name Times New Roman, color black;", num_format_str='#,##0.00')
        grey = xlwt.easyxf("pattern: pattern solid, fore-colour grey25;"
                           "align: wrap on, horiz center, vert center;"
                           "borders: left thin, right thin, top thin, bottom thin;"
                           "font: name Times New Roman, color black;", num_format_str='#,##0.00')
        grey_red = xlwt.easyxf("pattern: pattern solid, fore-colour grey25;"
                               "align: wrap on, horiz center, vert center;"
                               "borders: left thin, right thin, top thin, bottom thin;"
                               "font: name Times New Roman, color red;", num_format_str='#,##0.00')
        normal = xlwt.easyxf("align: wrap on, horiz center, vert center;"
                             "borders: left thin, right thin, top thin, bottom thin;"
                             "font: name Times New Roman;", num_format_str='#,##0.00')
        normal_red = xlwt.easyxf("align: wrap on, horiz center, vert center;"
                                 "borders: left thin, right thin, top thin, bottom thin;"
                                 "font: name Times New Roman, color red;", num_format_str='#,##0.00')
        normal_right = xlwt.easyxf("align: wrap on, horiz right, vert center;"
                                   "borders: left thin, right thin, top thin, bottom thin;"
                                   "font: name Times New Roman;", num_format_str='#,##0.00')
        r = 0
        c = 0
        if self.detailed:
            data_list = []
            cash = card = total = 0
            output_header = ['DATE', 'CUSTOMER', 'CONTACT NO.', 'ORDER NO.', 'SERVICES / RETAIL',
                             'AMOUNT', 'CATEGORY', 'SERVED STAFF', 'CASHIER', 'CASH PAYMENT', 'CARD PAYMENT']
            for item in output_header:
                worksheet.write(r, c, item, bold)
                col = worksheet.col(c)
                if c == 1:
                    col.width = 900 * 6
                else:
                    col.width = 900 * 4
                worksheet.row(r).height_mismatch = True
                worksheet.row(r).height = 220 * 2
                c += 1
            for ord in orders:
                data = []
                date_order = ''
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
                data.append(ord.name)
                data.append('')
                data.append(ord.amount_total)
                data.append('')
                data.append('')
                data.append(ord.cashier_name.name)
                data.append(ord.cash_amt)
                data.append(ord.credit_amt)
                cash += ord.cash_amt
                card += ord.credit_amt
                total += ord.amount_total
                data_list.append(data)
                r += 1
                c = 0
                for item in data:
                    if ord.negative_entry:
                        worksheet.write(r, c, item, grey_red)
                    else:
                        worksheet.write(r, c, item, grey)
                    c += 1
                for line in ord.lines:
                    r += 1
                    c = 4
                    worksheet.write_merge(r, r, 0, 4, line.product_id.name, normal_right)
                    c += 1
                    worksheet.write(r, c, line.price_subtotal_incl, normal)
                    c += 1
                    if line.product_id.pos_categ_id:
                        worksheet.write(r, c, line.product_id.pos_categ_id.name, normal)
                    else:
                        worksheet.write(r, c, '', normal)
                    c += 1
                    if line.staff_assigned_id:
                        worksheet.write(r, c, line.staff_assigned_id.name, normal)
                    else:
                        worksheet.write(r, c, '', normal)
                    c += 1
                    worksheet.write_merge(r, r, c, c + 2, '', normal_right)
            r += 1
            worksheet.write_merge(r, r, 0, 4, '', bold)
            c = 5
            worksheet.write(r, c, total, bold)
            c += 1
            worksheet.write_merge(r, r, c, c + 2, '', bold)
            c += 3
            worksheet.write(r, c, cash, bold)
            c += 1
            worksheet.write(r, c, card, bold)
        else:
            data_list = []
            cash = card = total = 0
            output_header = ['DATE', 'CUSTOMER', 'CONTACT NO.', 'ORDER NO.',
                             'AMOUNT', 'CASH PAYMENT', 'CARD PAYMENT', 'CASHIER']
            for item in output_header:
                worksheet.write(r, c, item, bold)
                col = worksheet.col(c)
                if c == 1:
                    col.width = 900 * 6
                else:
                    col.width = 900 * 4
                worksheet.row(r).height_mismatch = True
                worksheet.row(r).height = 220 * 2
                c += 1
            for ord in orders:
                data = []
                date_order = ''
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
                data.append(ord.name)
                data.append(ord.amount_total)
                data.append(ord.cash_amt)
                data.append(ord.credit_amt)
                data.append(ord.cashier_name.name)
                cash += ord.cash_amt
                card += ord.credit_amt
                total += ord.amount_total
                data_list.append(data)
                r += 1
                c = 0
                for item in data:
                    if ord.negative_entry:
                        worksheet.write(r, c, item, normal_red)
                    else:
                        worksheet.write(r, c, item, normal)
                    c += 1
            r += 1
            worksheet.write_merge(r, r, 0, 3, '', bold)
            c = 4
            worksheet.write(r, c, total, bold)
            c += 1
            worksheet.write(r, c, cash, bold)
            c += 1
            worksheet.write(r, c, card, bold)
            c += 1
            worksheet.write(r, c, '', bold)
            c += 1
        # worksheet.autofilter(0, 0, 1, 1)
        # worksheet.filter_column('A', 'x > 2000')
        # worksheet.filter_column('A')

        # worksheet.autofilter()
        buf = io.BytesIO()
        workbook.save(buf)
        out = base64.encodestring(buf.getvalue())
        name = "Sales_report" + ".xls"
        self.write({'state': 'get', 'data': out, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'summary.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
