# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError


class RewardWizard(models.TransientModel):
    _inherit = 'reward.wizard'

    customer_id = fields.Many2one('res.partner', 'Customer')
    card_no = fields.Char('Card No', required=True)

    @api.onchange('card_no')
    def onchange_card(self):
        if self.card_no:
            customer_obj = self.env['res.partner'].search([('barcode', '=', self.card_no)], limit=1)
            if customer_obj:
                self.customer_id = customer_obj.id
            else:
                self.customer_id = False
                raise UserError('There is no customer with the card number entered.')

    @api.multi
    def action_confirm(self):
        order_obj = self.env['pos.order'].browse(self.env.context.get('active_id'))
        if self.reward_id.type == 'gift':
            vals = {
                'product_id': self.reward_id.gift_product_id.id,
                'price_unit': 0,
                'qty': 1,
                'reward_id': self.reward_id.id,
                'order_id': self.env.context.get('active_id')
            }
            self.env['pos.order.line'].create(vals)

        if self.reward_id.type == 'discount':
            order_total = order_obj.amount_total
            discount = order_total * self.reward_id.discount
            discount_max = self.reward_id.discount_max
            given_discount = 0
            if discount_max and discount > discount_max:
                discount = discount_max;
            qty = int(order_obj.customer_loyalty/self.reward_id.point_cost)
            quty = min(qty,order_obj.amount_total)
            vals = {
                'product_id': self.reward_id.discount_product_id.id,
                'price_unit': -discount,
                'qty': quty,
                'reward_id': self.reward_id.id,
                'order_id': self.env.context.get('active_id')
            }
            self.env['pos.order.line'].create(vals)
            order_obj.card_no = self.card_no
