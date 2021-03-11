# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools import float_is_zero


class RewardWizard(models.TransientModel):
    _name = 'reward.wizard'

    def _get_reward_id(self):
        doc_ids = []
        order_obj = self.env['pos.order'].browse(self.env.context.get('active_id'))
        discount_reward_set = False
        gift_reward_set = False
        for line in order_obj.lines:
            if line.reward_id and line.reward_id.type == 'discount':
                discount_reward_set = True
            if line.reward_id and line.reward_id.type == 'gift':
                gift_reward_set = True
        customer_loyalty = order_obj.partner_id.loyalty_points
        spendable_points = customer_loyalty
        for reward in order_obj.session_id.config_id.loyalty_id.reward_ids:
            flag = 0
            if reward.minimum_points > spendable_points or reward.point_cost > spendable_points:
                flag = 1
            elif reward.type == 'gift' and (gift_reward_set or reward.point_cost > spendable_points):
                flag = 1
            elif reward.type == 'discount' and (discount_reward_set or reward.point_cost > spendable_points):
                flag = 1
            if flag == 0:
                doc_ids.append(reward.id)
        domain = [('id', 'in', doc_ids)]
        return domain

    @api.onchange('reward_id')
    def onchange_reward_id(self):
        domain = self._get_reward_id()
        return {
            'domain': {'reward_id': domain}
        }

    reward_id = fields.Many2one('loyalty.reward', 'Please select a reward',
                                domain=_get_reward_id, required=True)

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
            if discount_max and discount > discount_max:
                discount = discount_max;
            vals = {
                'product_id': self.reward_id.discount_product_id.id,
                'price_unit': -discount,
                'qty': 1,
                'reward_id': self.reward_id.id,
                'order_id': self.env.context.get('active_id')
            }
            self.env['pos.order.line'].create(vals)
