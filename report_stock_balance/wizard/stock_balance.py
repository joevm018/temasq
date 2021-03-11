# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta


class StockReport(models.TransientModel):
    _name = 'stock.balance.wizard'
    _description = 'Stock Report'

    start_date = fields.Date()
    end_date = fields.Date()
    product_ids = fields.Many2many('product.product', 'product_stock_rel', 'stock_id', 'product_id',
                                   string="Product", domain=[('type', 'in', ['product', 'consu'])])
    report_type = fields.Selection([('type_stock', 'Stock'),
                                  ('type_cost', 'Cost')], string='Type', required=True)

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        product_ids = False
        list_product_id = []
        name_product_id = ""
        if self.product_ids:
            for prod in self.product_ids:
                list_product_id.append(prod.id)
                if name_product_id != "":
                    name_product_id += ", "
                name_product_id += prod.name
            product_ids = [list_product_id, name_product_id]
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'product_ids': product_ids,
                'report_type': self.report_type}
        return self.env['report'].get_action([], 'report_stock_balance.report_stock_balance', data=data)


class ReportStockBalance(models.AbstractModel):
    _name = 'report.report_stock_balance.report_stock_balance'

    # def get_sale_po_lines(self, warehouse):
    #     lines = []
    #     stock_products = self.env['product.product'].search([('type', 'in', ['product', 'consu'])])
    #     product_ids = tuple([pro_id.id for pro_id in stock_products])
    #     sale_query = """
    #            SELECT sum(s_o_l.product_uom_qty) AS product_uom_qty, s_o_l.product_id FROM sale_order_line AS s_o_l
    #            JOIN sale_order AS s_o ON s_o_l.order_id = s_o.id
    #            WHERE s_o.state IN ('sale','done')
    #            AND s_o.warehouse_id = %s
    #            AND s_o_l.product_id in %s group by s_o_l.product_id"""
    #     purchase_query = """
    #            SELECT sum(p_o_l.product_qty) AS product_qty, p_o_l.product_id FROM purchase_order_line AS p_o_l
    #            JOIN purchase_order AS p_o ON p_o_l.order_id = p_o.id
    #            INNER JOIN stock_picking_type AS s_p_t ON p_o.picking_type_id = s_p_t.id
    #            WHERE p_o.state IN ('purchase','done')
    #            AND s_p_t.warehouse_id = %s AND p_o_l.product_id in %s group by p_o_l.product_id"""
    #     params = warehouse, product_ids if product_ids else (0, 0)
    #     self.env.cr.execute(sale_query, params)
    #     sol_query_obj = self.env.cr.dictfetchall()
    #     self.env.cr.execute(purchase_query, params)
    #     pol_query_obj = self.env.cr.dictfetchall()
    #     for obj in stock_products:
    #         sale_value = 0
    #         purchase_value = 0
    #         for sol_product in sol_query_obj:
    #             if sol_product['product_id'] == obj.id:
    #                 sale_value = sol_product['product_uom_qty']
    #         for pol_product in pol_query_obj:
    #             if pol_product['product_id'] == obj.id:
    #                 purchase_value = pol_product['product_qty']
    #         virtual_available = obj.with_context({'warehouse': warehouse}).virtual_available
    #         outgoing_qty = obj.with_context({'warehouse': warehouse}).outgoing_qty
    #         incoming_qty = obj.with_context({'warehouse': warehouse}).incoming_qty
    #         available_qty = virtual_available + outgoing_qty - incoming_qty
    #         value = available_qty * obj.standard_price
    #         vals = {
    #             'sku': obj.default_code,
    #             'name': obj.name,
    #             'category': obj.categ_id.name,
    #             'cost_price': obj.standard_price,
    #             'available': available_qty,
    #             'virtual': virtual_available,
    #             'incoming': incoming_qty,
    #             'outgoing': outgoing_qty,
    #             'net_on_hand': obj.with_context({'warehouse': warehouse}).qty_available,
    #             'total_value': value,
    #             'sale_value': sale_value,
    #             'purchase_value': purchase_value,
    #         }
    #         lines.append(vals)
    #     return lines

    @api.model
    def get_stock_details(self, date_start=False, date_stop=False, product_ids=False, report_type=False):
        # self.get_sale_po_lines(1)
        stock_products = self.env['product.product'].search([('type', 'in', ['product', 'consu'])])
        fields = ['credit', 'debit', 'balance', 'opening_balance']
        product_wise_counts = {}
        product_list = []
        for prod in stock_products:
            if prod not in product_list:
                product_list.append(prod)
            product_wise_counts[prod] = dict((fn, 0.0) for fn in fields)
        dom = [('state', '=', 'done')]
        if date_start:
            date_start_obj = datetime.strptime(date_start, '%Y-%m-%d')
            ord_date_start = date_start_obj.strftime("%Y-%m-%d 00:00:00")
            ord_date_start = datetime.strptime(ord_date_start, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
            dom.append(('date', '>=', str(ord_date_start)))
        if date_stop:
            date_end_obj = datetime.strptime(date_stop, '%Y-%m-%d')
            ord_date_stop = date_end_obj.strftime("%Y-%m-%d 23:59:59")
            ord_date_stop = datetime.strptime(ord_date_stop, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
            dom.append(('date', '<=', str(ord_date_stop)))
        if product_ids:
            dom.append(('product_id', 'in', product_ids[0]))
        stock_moves = self.env['stock.move'].search(dom)
        # for prod_id in product_list:
        #     unit_cost_price = 0
        #     total_cost_price = 0
        #     opening_stock = 0
        #     total_purchase_count = 0
        #     total_sale_count = 0
        #     for stock_move in stock_moves:
        #         if prod_id.id == stock_move.product_id.id:
        #             if stock_move.location_id.usage == "internal":
        #                 total_sale_count += stock_move.product_uom_qty
        #             elif stock_move.location_dest_id.usage == "internal":
        #                 total_purchase_count += stock_move.product_uom_qty
        #     product_wise_counts[prod_id] = {}
        #     product_wise_counts[prod_id]['product_code'] = prod_id.default_code
        #     product_wise_counts[prod_id]['product_name'] = prod_id.name
        #     if date_start:
        #         opening_stock = prod_id.with_context(to_date=date_start).qty_available
        #     product_wise_counts[prod_id]['unit_cost_price'] = unit_cost_price
        #     product_wise_counts[prod_id]['opening_stock'] = opening_stock
        #     product_wise_counts[prod_id]['total_purchase_count'] = total_purchase_count
        #     total_stock = opening_stock + total_purchase_count
        #     product_wise_counts[prod_id]['total_stock'] = total_stock
        #     product_wise_counts[prod_id]['total_sale_count'] = total_sale_count
        #     # closing_stock = prod_id.with_context(to_date=date_stop).qty_available
        #     closing_stock = prod_id.qty_available
        #     product_wise_counts[prod_id]['closing_stock'] = closing_stock
        #     product_wise_counts[prod_id]['total_cost_price'] = total_cost_price
        # from collections import OrderedDict
        # sorted_product_wise_counts = OrderedDict(sorted(product_wise_counts.items()))

        product_moves_dict = {}
        open_stock = []
        for products in stock_moves:
            open_stock.append(products.product_id.with_context(to_date=date_start))
        for moves in stock_moves:
            qty_in = 0
            qty_out = 0
            # if moves.location_id.usage == "internal" and moves.location_dest_id.usage != "internal":
            # Sale...........
            if moves.location_id.usage == "internal" and moves.location_dest_id.usage == "customer":
                qty_out = moves.product_uom_qty
            # Purchase......
            # elif moves.location_dest_id.usage == "internal" and moves.location_id.usage != "internal":
            elif moves.location_dest_id.usage == "internal" and moves.location_id.usage == "supplier":
                qty_in = moves.product_uom_qty
            qty_in_previous = 0
            qty_out_previous = 0
            if moves.product_id.id in product_moves_dict.keys():
                if product_moves_dict[moves.product_id.id]['qty_in']:
                    qty_in_previous = product_moves_dict[moves.product_id.id]['qty_in']
                if product_moves_dict[moves.product_id.id]['qty_out']:
                    qty_out_previous = product_moves_dict[moves.product_id.id]['qty_out']
            product_moves_dict[moves.product_id.id] = {'qty_available': moves.product_id.qty_available,
                                                         'qty_in': qty_in_previous + qty_in,
                                                         'qty_out': qty_out_previous + qty_out,
                                                         'open_qty': 0,
                                                         'product_code': moves.product_id.default_code,
                                                         'product_name': moves.product_id.name,
                                                         'unit_cost_price': moves.product_id.list_price,
                                                         }

        for lines in open_stock:
            for product in product_moves_dict:
                if product == lines.id:
                    product_moves_dict[lines.id]['open_qty'] = lines.qty_available
        for key, value in product_moves_dict.items():
            value['opening_stock'] = 0.0
            if date_start:
                value['opening_stock'] = value['open_qty']
            value['total_purchase_count'] = value['qty_in']
            value['total_stock'] = value['opening_stock'] + value['total_purchase_count']
            value['total_sale_count'] = value['qty_out']
            value['closing_stock'] = value['total_stock'] - value['total_sale_count']
            # value['closing_stock'] = value['qty_available']
            value['total_cost_price'] = value['total_sale_count'] * value['unit_cost_price']
        product_ids_name = ""
        if product_ids:
            product_ids_name = product_ids[1]
        return {
            'date_from': date_start,
            'date_to': date_stop,
            # 'product_wise_counts': sorted_product_wise_counts,
            'product_wise_counts': product_moves_dict,
            'product_name': product_ids_name,
            'report_type': report_type,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_stock_details(data['date_start'], data['date_stop'], data['product_ids'], data['report_type']))
        return self.env['report'].render('report_stock_balance.report_stock_balance', data)
