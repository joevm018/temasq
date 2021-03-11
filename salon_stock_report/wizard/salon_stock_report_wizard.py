from odoo import api, fields, models
# from odoo.report.report_xlsx import ReportXlsx
from datetime import datetime
import base64
from odoo.tools.misc import xlwt
import io


class StockReportWizard(models.TransientModel):
    _name = "salon.stock.report"

    start_date = fields.Date("Period From", default=fields.Date.context_today)
    end_date = fields.Date("Period To", default=fields.Date.context_today)
    expiry_date = fields.Date("Expiry Based on", required=True, default=fields.Date.context_today)
    show_no_stock = fields.Boolean(string="Show No Stock Items")
    show_detailed = fields.Boolean(string="Show Lot Details")
    show_expiry = fields.Boolean(string="Show Expired Items only")
    pdt_ids = fields.Many2many('product.product', 'pdt_stock_rela', 'pdt_id', 'report_id', 'Items',
                               domain=[('type', '!=', 'service')])
    location_id = fields.Many2one('stock.location', 'Location', required=True, domain="[('usage', '=', 'internal')]")
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),  # choose language
                              ('get', 'get')], default='choose')
    name = fields.Char('File Name', readonly=True)

    def _get_company_id(self):
        group_multi_company = self.env.user.has_group('base.group_multi_company')
        if group_multi_company:
            company_ids = [x.id for x in self.env['res.company'].search([('id', 'in', self.env.user.company_ids.ids)])]
            domain_company = [('id', 'in', company_ids)]
        else:
            domain_company = [('id', '=', self.env.user.company_id.id)]
        return domain_company

    company_id = fields.Many2one('res.company', "Company", domain=_get_company_id, required=True)

    @api.multi
    def stock_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Stock Info')
        bold = xlwt.easyxf("pattern: pattern solid, fore-colour light_turquoise;"
                           "align: wrap on, horiz center, vert center;font: bold on;"
                           "borders: left thin, right thin, top thin, bottom thin;"
                           "font: name Times New Roman, color black;", num_format_str='#,##0')
        grey = xlwt.easyxf("pattern: pattern solid, fore-colour grey25;"
                           "align: wrap on, horiz center, vert center;"
                           "borders: left thin, right thin, top thin, bottom thin;"
                           "font: name Times New Roman, color black;", num_format_str='#,##0.00')
        normal = xlwt.easyxf("align: horiz center, vert center;"
                             "borders: left thin, right thin, top thin, bottom thin;"
                             "font: name Times New Roman;", num_format_str='#,##0')
        r = 0
        c = 0
        output_header = ['Barcode', 'Item Name', 'Purchased Qty', 'Sold Qty', 'Consumed Qty',
                         'Adjusted Qty', 'Current Stock', 'Unit Cost', 'Inventory Value']
        for item in output_header:
            worksheet.write(r, c, item, bold)
            col = worksheet.col(c)
            if c == 2:
                col.width = 1200 * 9
            if c == 1:
                col.width = 900 * 8
            else:
                col.width = 900 * 4
            worksheet.row(r).height_mismatch = True
            worksheet.row(r).height = 220 * 2
            c += 1
        quant_obj = self.env['stock.quant']
        move_obj = self.env['stock.move']
        dom = [('state', '=', 'done'), ]
        if self.start_date:
            dom.append(('date', '>=', self.start_date))
        if self.end_date:
            dom.append(('date', '<=', self.end_date))
        moves = move_obj.search(dom).ids

        if self.pdt_ids:
            for pdt in self.pdt_ids:
                count = pdt.with_context(location=self.location_id.id)
                if self.show_no_stock or count.qty_available > 0:
                    data = []
                    if pdt.barcode:
                        data.append(pdt.barcode)
                    else:
                        data.append('')
                    data.append(pdt.name)
                    move_ids = move_obj.search([('product_id', '=', pdt.id),
                                                ('id', 'in', moves),
                                                ('location_id.usage', '=', 'supplier'),
                                                ('location_dest_id.usage', '=', 'internal')])
                    purchase_count = sum(move.product_uom_qty for move in move_ids)
                    sale_ids = move_obj.search([('product_id', '=', pdt.id),
                                                ('id', 'in', moves),
                                                ('location_id.usage', '=', 'internal'),
                                                ('location_dest_id.usage', '=', 'customer')])
                    sale_count = sum(move.product_uom_qty for move in sale_ids)
                    consu_ids = move_obj.search([('product_id', '=', pdt.id),
                                                 ('id', 'in', moves),
                                                 ('consumed', '=', True),
                                                 ('location_id.usage', '=', 'inventory'),
                                                 ('location_dest_id.usage', '=', 'internal')])
                    consu_count = sum(move.product_uom_qty for move in consu_ids)
                    consum_ids = move_obj.search([('product_id', '=', pdt.id),
                                                  ('id', 'in', moves),
                                                  ('consumed', '=', True),
                                                  ('location_id.usage', '=', 'internal'),
                                                  ('location_dest_id.usage', '=', 'inventory')])
                    consum_count = sum(move.product_uom_qty for move in consum_ids)

                    adjust_ids = move_obj.search([('product_id', '=', pdt.id),
                                                  ('id', 'in', moves),
                                                  ('consumed', '=', False),
                                                  ('location_id.usage', '=', 'inventory'),
                                                  ('location_dest_id.usage', '=', 'internal')])
                    adjust_count = sum(move.product_uom_qty for move in adjust_ids)
                    adjus_ids = move_obj.search([('product_id', '=', pdt.id),
                                                 ('id', 'in', moves),
                                                 ('consumed', '=', False),
                                                 ('location_id.usage', '=', 'internal'),
                                                 ('location_dest_id.usage', '=', 'inventory')])
                    adjus_count = sum(move.product_uom_qty for move in adjus_ids)

                    data.append(purchase_count)
                    data.append(sale_count)
                    data.append(consum_count - consu_count)
                    data.append(adjust_count - adjus_count)
                    data.append(count.qty_available)
                    data.append(pdt.standard_price)
                    data.append(count.qty_available * pdt.standard_price)
                    r += 1
                    c = 0
                    for item in data:
                        if self.show_detailed:
                            worksheet.write(r, c, item, grey)
                        else:
                            worksheet.write(r, c, item, normal)
                        c += 1
                    if self.show_detailed:
                        qry = 'select sum(stock_quant.qty), stock_quant.lot_id, p_o.name, p_o.life_date from stock_quant JOIN stock_production_lot AS p_o ON stock_quant.lot_id = p_o.id where stock_quant.product_id=%s and stock_quant.location_id=%s group by stock_quant.lot_id, p_o.name, p_o.life_date'
                        params = (pdt.id, self.location_id.id)
                        self.env.cr.execute(qry, params)
                        result = self.env.cr.dictfetchall()
                        for item in result:
                            r += 1
                            c = 0
                            if item['lot_id']:
                                worksheet.write_merge(r, r, c, c + 4, item['name'], normal)
                                c += 5
                            else:
                                worksheet.write_merge(r, r, c, c + 4, '', normal)
                                c += 5
                            date_order = ''
                            if item['life_date']:
                                date_order = datetime.strptime(item['life_date'], '%Y-%m-%d %H:%M:%S').date()
                                date_order = date_order.strftime('%d/%m/%Y')
                            data.append(date_order)
                            worksheet.write(r, c, date_order, normal)
                            c += 1
                            worksheet.write(r, c, item['sum'], normal)
                            c += 1
                            worksheet.write(r, c, '', normal)
                            c += 1
                            worksheet.write(r, c, '', normal)
                            c += 1
        else:
            for pdt in self.env['product.product'].search([('type', '!=', 'service')]):
                count = pdt.with_context(location=self.location_id.id)
                if self.show_no_stock or count.qty_available > 0:
                    data = []
                    if pdt.barcode:
                        data.append(pdt.barcode)
                    else:
                        data.append('')
                    data.append(pdt.name)
                    move_ids = move_obj.search([('product_id', '=', pdt.id),
                                                ('id', 'in', moves),
                                                ('location_id.usage', '=', 'supplier'),
                                                ('location_dest_id.usage', '=', 'internal')])
                    purchase_count = sum(move.product_uom_qty for move in move_ids)
                    sale_ids = move_obj.search([('product_id', '=', pdt.id),
                                                ('id', 'in', moves),
                                                ('location_id.usage', '=', 'internal'),
                                                ('location_dest_id.usage', '=', 'customer')])
                    sale_count = sum(move.product_uom_qty for move in sale_ids)
                    consu_ids = move_obj.search([('product_id', '=', pdt.id),
                                                 ('id', 'in', moves),
                                                 ('consumed', '=', True),
                                                 ('location_id.usage', '=', 'inventory'),
                                                 ('location_dest_id.usage', '=', 'internal')])
                    consu_count = sum(move.product_uom_qty for move in consu_ids)
                    consum_ids = move_obj.search([('product_id', '=', pdt.id),
                                                  ('id', 'in', moves),
                                                  ('consumed', '=', True),
                                                  ('location_id.usage', '=', 'internal'),
                                                  ('location_dest_id.usage', '=', 'inventory')])
                    consum_count = sum(move.product_uom_qty for move in consum_ids)

                    adjust_ids = move_obj.search([('product_id', '=', pdt.id),
                                                  ('id', 'in', moves),
                                                  ('consumed', '=', False),
                                                  ('location_id.usage', '=', 'inventory'),
                                                  ('location_dest_id.usage', '=', 'internal')])
                    adjust_count = sum(move.product_uom_qty for move in adjust_ids)
                    adjus_ids = move_obj.search([('product_id', '=', pdt.id),
                                                 ('id', 'in', moves),
                                                 ('consumed', '=', False),
                                                 ('location_id.usage', '=', 'internal'),
                                                 ('location_dest_id.usage', '=', 'inventory')])
                    adjus_count = sum(move.product_uom_qty for move in adjus_ids)

                    data.append(purchase_count)
                    data.append(sale_count)
                    data.append(consum_count - consu_count)
                    data.append(adjust_count - adjus_count)
                    data.append(count.qty_available)
                    data.append(pdt.standard_price)
                    data.append(count.qty_available * pdt.standard_price)
                    r += 1
                    c = 0
                    for item in data:
                        if self.show_detailed:
                            worksheet.write(r, c, item, grey)
                        else:
                            worksheet.write(r, c, item, normal)
                        c += 1
                    if self.show_detailed:
                        qry = 'select sum(stock_quant.qty), stock_quant.lot_id, p_o.name, p_o.life_date from stock_quant JOIN stock_production_lot AS p_o ON stock_quant.lot_id = p_o.id where stock_quant.product_id=%s and stock_quant.location_id=%s group by stock_quant.lot_id, p_o.name, p_o.life_date'
                        params = (pdt.id, self.location_id.id)
                        self.env.cr.execute(qry, params)
                        result = self.env.cr.dictfetchall()
                        for item in result:
                            r += 1
                            c = 0
                            if item['lot_id']:
                                worksheet.write_merge(r, r, c, c + 4, item['name'], normal)
                                c += 5
                            else:
                                worksheet.write_merge(r, r, c, c + 4, '', normal)
                                c += 5
                            date_order = ''
                            if item['life_date']:
                                date_order = datetime.strptime(item['life_date'], '%Y-%m-%d %H:%M:%S').date()
                                date_order = date_order.strftime('%d/%m/%Y')
                            data.append(date_order)
                            worksheet.write(r, c, date_order, normal)
                            c += 1
                            worksheet.write(r, c, item['sum'], normal)
                            c += 1
                            worksheet.write(r, c, '', normal)
                            c += 1
                            worksheet.write(r, c, '', normal)
                            c += 1

        buf = io.BytesIO()
        workbook.save(buf)
        out = base64.encodestring(buf.getvalue())
        name = "Stock_report" + ".xls"
        self.write({'state': 'get', 'data': out, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'salon.stock.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.model
    def default_get(self, fields):
        res = super(StockReportWizard, self).default_get(fields)
        if 'location_id' in fields and not res.get('location_id'):
            res['location_id'] = self.env.ref('stock.stock_location_stock').id
        self._get_company_id()
        res['company_id'] = self.env.user.company_id.id
        return res
