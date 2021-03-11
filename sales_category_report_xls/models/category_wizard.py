# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# from odoo.report.report_xlsx import ReportXlsx
import base64
import io

from odoo import api, fields, models
from odoo.tools.misc import xlwt


class SummaryWizard(models.TransientModel):
    _name = 'category.wizard'

    start_date = fields.Date('Start Date', default=fields.Date.context_today)
    end_date = fields.Date('End Date', default=fields.Date.context_today)
    staff_id = fields.Many2one('hr.employee', string="Staff")
    categ_id = fields.Many2one('pos.category', string="Category")
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
        orders = self.env['pos.order'].search(lst_search, order='date_order asc')
        # categ_ids = self.env['pos.category'].search([])
        categ_ids = {}
        staff_ids = {}
        if self.categ_id:
            categ_ids = {self.categ_id: {'staff': {}, 'total': 0}}
        if self.staff_id:
            staff_ids = {self.staff_id: 0}

        for ord in orders:
            for line in ord.lines:
                if self.staff_id and self.staff_id.id != line.staff_assigned_id.id:
                    continue
                if self.categ_id and self.categ_id.id != line.product_id.pos_categ_id.id:
                    continue
                if not line.staff_assigned_id:
                    if 'Undefined' not in staff_ids.keys():
                        staff_ids['Undefined'] = line.after_global_disc_subtotal
                    else:
                        staff_ids['Undefined'] += line.after_global_disc_subtotal
                else:
                    if line.staff_assigned_id not in staff_ids.keys():
                        staff_ids[line.staff_assigned_id] = line.after_global_disc_subtotal
                    else:
                        staff_ids[line.staff_assigned_id] += line.after_global_disc_subtotal
                if line.product_id.pos_categ_id:
                    if line.product_id.pos_categ_id not in categ_ids.keys():
                        categ_ids[line.product_id.pos_categ_id] = {'staff': {}, 'total': 0}
                        if line.staff_assigned_id:
                            if line.staff_assigned_id not in categ_ids[line.product_id.pos_categ_id]['staff'].keys():
                                categ_ids[line.product_id.pos_categ_id]['staff'][line.staff_assigned_id] = {
                                    'amount': line.after_global_disc_subtotal,
                                    'total': line.after_global_disc_subtotal}
                                categ_ids[line.product_id.pos_categ_id]['total'] += line.after_global_disc_subtotal
                            else:
                                categ_ids[line.product_id.pos_categ_id]['staff'][line.staff_assigned_id][
                                    'amount'] += line.after_global_disc_subtotal
                                categ_ids[line.product_id.pos_categ_id]['staff'][line.staff_assigned_id][
                                    'total'] += line.after_global_disc_subtotal
                                categ_ids[line.product_id.pos_categ_id]['total'] += line.after_global_disc_subtotal
                        else:
                            if 'Undefined' not in categ_ids['Undefined']['staff'].keys():
                                categ_ids[line.product_id.pos_categ_id]['staff']['Undefined'] = {'amount': 0,
                                                                                                 'total': 0}
                            categ_ids[line.product_id.pos_categ_id]['staff']['Undefined'][
                                'amount'] += line.after_global_disc_subtotal
                            categ_ids[line.product_id.pos_categ_id]['staff']['Undefined'][
                                'total'] += line.after_global_disc_subtotal
                            categ_ids[line.product_id.pos_categ_id][
                                'total'] += line.after_global_disc_subtotal
                    else:
                        if line.staff_assigned_id:
                            if line.staff_assigned_id not in categ_ids[line.product_id.pos_categ_id]['staff'].keys():
                                categ_ids[line.product_id.pos_categ_id]['staff'][line.staff_assigned_id] = {'amount': 0,
                                                                                                 'total': 0}
                            categ_ids[line.product_id.pos_categ_id]['staff'][line.staff_assigned_id][
                                    'amount'] += line.after_global_disc_subtotal
                            categ_ids[line.product_id.pos_categ_id]['staff'][line.staff_assigned_id][
                                    'total'] += line.after_global_disc_subtotal
                            categ_ids[line.product_id.pos_categ_id]['total'] += line.after_global_disc_subtotal
                        else:
                            if 'Undefined' not in categ_ids[line.product_id.pos_categ_id]['staff'].keys():
                                categ_ids[line.product_id.pos_categ_id]['staff']['Undefined'] = {'amount': 0,
                                                                                                 'total': 0}
                            categ_ids[line.product_id.pos_categ_id]['staff']['Undefined'][
                                'amount'] += line.after_global_disc_subtotal
                            categ_ids[line.product_id.pos_categ_id]['staff']['Undefined'][
                                'total'] += line.after_global_disc_subtotal
                            categ_ids[line.product_id.pos_categ_id]['total'] += line.after_global_disc_subtotal

                else:
                    if 'Undefined' not in categ_ids.keys():
                        categ_ids['Undefined'] = {'staff': {}, 'total': 0}
                        if line.staff_assigned_id:
                            if line.staff_assigned_id not in categ_ids['Undefined']['staff'].keys():
                                categ_ids['Undefined']['staff'][line.staff_assigned_id] = {
                                    'amount': line.after_global_disc_subtotal,
                                    'total': line.after_global_disc_subtotal}
                                categ_ids['Undefined']['total'] = line.after_global_disc_subtotal
                            else:
                                categ_ids['Undefined']['staff'][line.staff_assigned_id][
                                    'amount'] += line.after_global_disc_subtotal
                                categ_ids['Undefined']['staff'][line.staff_assigned_id][
                                    'total'] += line.after_global_disc_subtotal
                                categ_ids['Undefined']['total'] += line.after_global_disc_subtotal
                        else:
                            if 'Undefined' not in categ_ids['Undefined']['staff'].keys():
                                categ_ids['Undefined']['staff']['Undefined'] = {
                                    'amount': line.after_global_disc_subtotal,
                                    'total': line.after_global_disc_subtotal}
                                categ_ids['Undefined']['total'] = line.after_global_disc_subtotal
                            else:
                                categ_ids['Undefined']['staff']['Undefined'][
                                    'amount'] += line.after_global_disc_subtotal
                                categ_ids['Undefined']['staff']['Undefined']['total'] += line.after_global_disc_subtotal
                                categ_ids['Undefined']['total'] += line.after_global_disc_subtotal

                    else:
                        if line.staff_assigned_id:
                            if line.staff_assigned_id not in categ_ids['Undefined']['staff'].keys():
                                categ_ids['Undefined']['staff'][line.staff_assigned_id] = {}
                                categ_ids['Undefined']['staff'][line.staff_assigned_id][
                                    'amount'] = line.after_global_disc_subtotal
                                categ_ids['Undefined']['staff'][line.staff_assigned_id][
                                    'total'] = line.after_global_disc_subtotal
                                categ_ids['Undefined']['total'] = line.after_global_disc_subtotal
                            else:
                                categ_ids['Undefined']['staff'][line.staff_assigned_id][
                                    'amount'] += line.after_global_disc_subtotal
                                categ_ids['Undefined']['staff'][line.staff_assigned_id][
                                    'total'] += line.after_global_disc_subtotal
                                categ_ids['Undefined']['total'] += line.after_global_disc_subtotal
                        else:
                            if 'Undefined' not in categ_ids['Undefined']['staff'].keys():
                                categ_ids['Undefined']['staff']['Undefined'] = {}
                                categ_ids['Undefined']['staff']['Undefined'][
                                    'amount'] = line.after_global_disc_subtotal
                                categ_ids['Undefined']['staff']['Undefined'][
                                    'total'] = line.after_global_disc_subtotal
                                categ_ids['Undefined'][
                                    'total'] = line.after_global_disc_subtotal

                            else:
                                categ_ids['Undefined']['staff']['Undefined'][
                                    'amount'] += line.after_global_disc_subtotal
                                categ_ids['Undefined']['staff']['Undefined']['total'] += line.after_global_disc_subtotal
                                categ_ids['Undefined']['total'] += line.after_global_disc_subtotal
        bold = xlwt.easyxf("pattern: pattern solid, fore-colour light_turquoise;"
                           "align: wrap on, horiz center, vert center;font: bold on;"
                           "borders: left thin, right thin, top thin, bottom thin;"
                           "font: name Times New Roman, color black;", num_format_str='#,##0.00')
        normal = xlwt.easyxf("align: wrap on, horiz center, vert center;"
                             "borders: left thin, right thin, top thin, bottom thin;"
                             "font: name Times New Roman;", num_format_str='#,##0.00')

        r = 0
        c = 0
        cash = card = total = 0
        worksheet.write(r, c, 'EMPLOYEE', bold)
        col = worksheet.col(c)
        if c == 1:
            col.width = 900 * 6
        else:
            col.width = 900 * 4
        worksheet.row(r).height_mismatch = True
        worksheet.row(r).height = 220 * 2
        c += 1
        for item in categ_ids:
            if item == 'Undefined':
                worksheet.write(r, c, item, bold)
            else:
                worksheet.write(r, c, item.name, bold)
            col = worksheet.col(c)
            if c == 1:
                col.width = 900 * 6
            else:
                col.width = 900 * 4
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 2
            c += 1
        worksheet.write(r, c, 'TOTAL', bold)
        col = worksheet.col(c)
        if c == 1:
            col.width = 900 * 6
        else:
            col.width = 900 * 4
        worksheet.row(r).height_mismatch = True
        worksheet.row(r).height = 220 * 2
        c += 1
        for staff in staff_ids:
            r += 1
            c = 0
            if staff == 'Undefined':
                worksheet.write(r, c, staff, bold)
            else:
                worksheet.write(r, c, staff.name, bold)
            col = worksheet.col(c)
            col.width = 900 * 4
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 2
            c += 1
            for cat in categ_ids:
                if staff in categ_ids[cat]['staff'].keys():
                    worksheet.write(r, c, str(categ_ids[cat]['staff'][staff]['amount']), normal)
                else:
                    worksheet.write(r, c, '', normal)
                col = worksheet.col(c)
                col.width = 900 * 4
                worksheet.row(r).height_mismatch = True
                worksheet.row(r).height = 220 * 2
                c += 1
            worksheet.write(r, c, staff_ids[staff], normal)
            c += 1
        r += 1
        c = 0
        worksheet.write(r, c, 'TOTAL', bold)
        c += 1
        cat_sum = 0
        for cat in categ_ids:
            cat_sum += categ_ids[cat]['total']
            worksheet.write(r, c, categ_ids[cat]['total'], bold)
            c += 1
        worksheet.write(r, c, cat_sum, bold)
        c += 1
        buf = io.BytesIO()
        workbook.save(buf)
        out = base64.encodestring(buf.getvalue())
        name = "Category_report" + ".xls"
        self.write({'state': 'get', 'data': out, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'category.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
