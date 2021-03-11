# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime


class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_cash_payment = fields.Boolean(
        string='Is cash paymert', compute='_compute_payment', store=True)
    is_bank_payment = fields.Boolean(
        string='Is bank paymert', compute='_compute_payment', store=True)

    @api.depends('statement_ids')
    def _compute_payment(self):
        for order in self.filtered(
            lambda s: datetime.strptime(
                s.date_order, '%Y-%m-%d %H:%M:%S'
            ).date() == date.today()
        ):
            cash_order = len(order.statement_ids.filtered(
                lambda o: o.journal_id.type == 'cash'))
            bank_order = len(order.statement_ids.filtered(
                lambda o: o.journal_id.type == 'bank'))
            if cash_order:
                order.is_cash_payment = True
            if bank_order:
                order.is_bank_payment = True


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    price_subtotal_incl = fields.Float(
        compute='_compute_amount_line_all',
        digits=0, string='Subtotal', store=True)


class PosTopServices(models.Model):
    _name = 'pos.top.service'

    product = fields.Many2one('product.product', 'Product ID')
    product_name = fields.Char('Product Name')
    no_of_products = fields.Integer('No of products')

    @api.multi
    def _compute_service_product(self):
        product_records = {}
        sorted_product_records = []
        services = self.env['pos.order.line'].search([]).filtered(
            lambda o: o.product_id.type == 'service')
        for service in services:
            if service.product_id not in product_records:
                product_records.update({service.product_id: 0})
            product_records[service.product_id] += service.qty

        for product_id, qty in sorted(
            product_records.iteritems(),
            key=lambda (k, v): (v, k),
            reverse=True
        ):
            sorted_product_records.append({
                'product': product_id.id,
                'product_name': product_id.name,
                'no_of_products': int(qty)
            })
        cnt = 1
        product_qty = 0
        for product in sorted_product_records:
            if cnt < 6:
                prd = self.search([
                    ('product', '=', product.get('product'))])
                if not prd:
                    self.create(product)
                else:
                    self.write({
                        'no_of_products': product.get('no_of_products')})
            else:
                product_qty += int(qty)
                if len(sorted_product_records) == cnt:
                    prd = self.search([
                        ('product_name', '=', 'Others')])
                    if not prd:
                        self.create({
                            'product_name': 'Others',
                            'no_of_products': product_qty})
                    else:
                        self.write({
                            'no_of_products': product.get('no_of_products')})
            cnt += 1
