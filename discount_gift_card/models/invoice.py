# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class POSInvoiceGiftCard(models.Model):
    _inherit = 'account.invoice'

    redeemed_gift_id = fields.Many2one('pos.customer.card', 'Redeemed Gift Card')
    redeemed_amount = fields.Float(string='Redeemed Amount')
    amt_before_redeem = fields.Float(compute='_compute_amount', string='Before Redeem', default=0.0)

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id',
                 'discount_total', 'discount_percent', 'redeemed_gift_id', 'redeemed_amount')
    def _compute_amount(self):
        super(POSInvoiceGiftCard, self)._compute_amount()
        ord_amount_total = self.amount_total
        self.amt_before_redeem = ord_amount_total
        self.amount_total = ord_amount_total - self.redeemed_amount

    @api.multi
    def action_move_create(self):
        res = super(POSInvoiceGiftCard, self).action_move_create()
        if self.redeemed_amount > 0 and self.redeemed_gift_id:
            disc_gift_card_product = self.env.ref('discount_gift_card.product_product_discount_gift_card')
            if disc_gift_card_product.property_account_income_id.id:
                disc_gift_card_income_account = disc_gift_card_product.property_account_income_id.id
            elif disc_gift_card_product.categ_id.property_account_income_categ_id.id:
                disc_gift_card_income_account = disc_gift_card_product.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this product: "%s" (id:%d).')
                                % (disc_gift_card_product.name, disc_gift_card_product.id))
            lines = self.env['account.move.line'].search([('move_id', '=', self.move_id.id), ('debit', '>', 0),
                                                          ('account_id', '=', self.account_id.id)], limit=1)
            if self.redeemed_amount > 0:
                redeemed_amount = self.redeemed_amount
            lines.write({
                'debit': lines.debit - redeemed_amount
            })
            temp2 = {
                'partner_id': self.partner_id.id,
                'name': disc_gift_card_product.name,
                'credit': 0,
                'debit': redeemed_amount,
                'account_id': disc_gift_card_income_account,
                'quantity': 1,
                'move_id': self.move_id.id,
            }
            self.env['account.move.line'].create(temp2)
        return res