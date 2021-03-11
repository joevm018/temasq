# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

#
# class POSInvoiceNew(models.Model):
#     _inherit = 'account.invoice.line'
#
#     discount_fixed = fields.Float(string='Discount.Fixed', digits=dp.get_precision('DiscountFixed'),
#                             default=0.0)
#
#     @api.one
#     @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
#                  'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
#     def _compute_price(self):
#         super(POSInvoiceNew, self)._compute_price()
#         currency = self.invoice_id and self.invoice_id.currency_id or None
#         price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
#
#         if self.discount != 0:
#             price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
#         if self.discount_fixed != 0:
#             price = self.price_unit
#         taxes = False
#         if self.invoice_line_tax_ids:
#             taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
#                                                           partner=self.invoice_id.partner_id)
#
#         self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
#
#         if self.discount != 0:
#             self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
#
#         if self.discount_fixed != 0:
#             self.price_subtotal = price_subtotal_signed = taxes[
#                 'total_excluded'] if taxes else self.quantity * price - self.discount_fixed
#         if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
#             price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed,
#                                                                         self.invoice_id.company_id.currency_id)
#         sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
#         self.price_subtotal_signed = price_subtotal_signed * sign
#


class POSInvoiceTotalDisc(models.Model):
    _inherit = 'account.invoice'

    discount_total = fields.Float(string='Total Discount', default=0.0, readonly=True, states={'draft': [('readonly', False)]})
    discount_percent = fields.Float(string='Total Discount(%)', default=0.0, readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('discount_percent')
    def change_discount_fixed(self):
        if self.discount_percent:
            self.discount_total = 0.0

    @api.onchange('discount_total')
    def change_discount_percent(self):
        if self.discount_total:
            self.discount_percent = 0.0

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id',
                 'discount_total', 'discount_percent')
    def _compute_amount(self):
        super(POSInvoiceTotalDisc, self)._compute_amount()
        self.amount_total = self.amount_untaxed + self.amount_tax
        if self.discount_total > 0:
            self.amount_total -= self.discount_total
        if self.discount_percent > 0:
            self.amount_total -= ((self.amount_untaxed + self.amount_tax) * self.discount_percent / 100)

    @api.multi
    def action_move_create(self):
        res = super(POSInvoiceTotalDisc, self).action_move_create()
        order = self.env['pos.order'].search([('invoice_id', '=', self.id)])
        session = None
        if order:
            if order.discount_total > 0 or order.discount_percent > 0:
                session = order.session_id
                discount_ac = None
                if session:
                    if session.config_id.discount_account:
                       discount_ac = session.config_id.discount_account
                    else:
                        raise UserError(_('Please set a discount account for this session'))
                lines = self.env['account.move.line'].search([('move_id', '=', self.move_id.id), ('debit', '>', 0),
                                                              ('account_id', '=', self.account_id.id)], limit=1)
                if order.discount_total > 0:
                    discount = order.discount_total
                elif order.discount_percent > 0:
                    move_lines = self.env['account.move.line'].search([('move_id', '=', self.move_id.id), ('credit', '>', 0)])
                    sum = 0
                    for i in move_lines:
                        sum += i.credit
                    discount = sum - order.amount_total
                lines.write({
                    'debit': lines.debit - discount
                })
                temp2 = {
                    'partner_id': self.partner_id.id,
                    'name': "Discount",
                    'credit': 0,
                    'debit': discount,
                    'account_id': discount_ac.id,
                    'quantity': 1,
                    'move_id': self.move_id.id,
                }
                self.env['account.move.line'].create(temp2)
        return res
