# -*- coding: utf-8 -*-

import logging
from odoo import fields, api, models
from odoo.tools.translate import _
from odoo.exceptions import UserError


class NewPosOrder(models.Model):
    _inherit = "pos.order"

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount', 'lines.discount_fixed',
                 'discount_total', 'discount_percent')
    def _compute_amount_all(self):
        super(NewPosOrder, self)._compute_amount_all()
        for order in self:
            service_sum = 0
            for line in order.lines:
                if line.product_id.type == 'service':
                    service_sum += line.price_subtotal
            currency = order.pricelist_id.currency_id
            amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
            service_sum = currency.round(service_sum)
            order.amount_total = order.amount_tax + amount_untaxed
            if service_sum > order.discount_total:
                order.amount_total -= order.discount_total
                order.amt_discount = order.discount_total
            if order.discount_percent > 0:
                order.amount_total -= (service_sum * order.discount_percent / 100)
                order.amt_discount = (service_sum * order.discount_percent / 100)
            order.amt_before_discount = order.amount_tax + amount_untaxed
