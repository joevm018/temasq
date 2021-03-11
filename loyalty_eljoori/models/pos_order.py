# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    reward_id = fields.Many2one('loyalty.reward', 'Loyalty reward')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    card_no = fields.Char('Card No')
    have_loyalty_card = fields.Boolean('Have Loyalty Card', compute='_get_have_loyalty')

    @api.depends('partner_id', 'date_order')
    def _get_have_loyalty(self):
        for order in self:
            if order.partner_id and order.partner_id.barcode:
                order.have_loyalty_card = True
            else:
                order.have_loyalty_card = False

    def loyalty_purchase(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Loyalty Card',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'loyalty.purchase',
            'target': 'new',
            'context': {}
        }

    def swipe_card(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Swipe Card',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'swipe.card',
            'target': 'new',
            'context': {}
        }

    @api.depends('partner_id', 'lines')
    def _get_points(self):
        for order in self:
            spent = 0
            won = 0
            loyalty_obj = order.session_id.config_id.loyalty_id
            if loyalty_obj and order.partner_id and order.partner_id.barcode:
                if order.date_order >= order.partner_id.loyalty_purchase_date and order.card_no:
                    pdt_rules = self.env['loyalty.rule'].search([('type', '=', 'product')])
                    category_rules = self.env['loyalty.rule'].search([('type', '=', 'category')])
                    for line in order.lines:
                        overriden = False
                        if line.reward_id:
                            spent += line.qty * line.reward_id.point_cost
                        else:
                            for rule in pdt_rules:
                                if rule.product_id.id == line.product_id.id:
                                    won += round(line.qty * rule.pp_product, 1)
                                    won += round(line.price_subtotal * rule.pp_currency, 1)
                                    if not rule.cumulative:
                                        overriden = True
                                        break
                            for rule in category_rules:
                                if rule.category_id.id == line.product_id.pos_categ_id.id and not overriden:
                                    won += round(line.qty * rule.pp_product, 1)
                                    won += round(line.price_subtotal * rule.pp_currency, 1)
                                    if not rule.cumulative:
                                        overriden = True
                                        break
                            if not overriden:
                                product_sold = line.qty
                                total_sold = line.price_subtotal
                                won += round(total_sold * loyalty_obj.pp_currency, 1)
                                won += round(product_sold * loyalty_obj.pp_product, 1)
                                won += round(loyalty_obj.pp_order, 1)
            order.loyalty_won = won
            order.points_spent = spent
            order.loyalty_points = won - spent

    @api.depends('partner_id', 'state', 'session_id', 'lines')
    def _get_loyalty_points(self):
        for i in self:
            if i.partner_id and i.partner_id.barcode:
                i.customer_loyalty = i.partner_id.loyalty_points
                if i.state == 'draft' and i.session_id and i.session_id.config_id and i.session_id.config_id.loyalty_id:
                    doc_ids = []
                    discount_reward_set = False
                    gift_reward_set = False
                    for line in self.lines:
                        if line.reward_id and line.reward_id.type == 'discount':
                            discount_reward_set = True
                        if line.reward_id and line.reward_id.type == 'gift':
                            gift_reward_set = True
                    customer_loyalty = self.partner_id.loyalty_points
                    spendable_points = customer_loyalty
                    for reward in self.session_id.config_id.loyalty_id.reward_ids:
                        flag = 0
                        if reward.minimum_points > spendable_points or reward.point_cost > spendable_points:
                            flag = 1
                        elif reward.type == 'gift' and (gift_reward_set or reward.point_cost > spendable_points):
                            flag = 1
                        elif reward.type == 'discount' and (
                                discount_reward_set or reward.point_cost > spendable_points):
                            flag = 1
                        if flag == 0:
                            doc_ids.append(reward.id)
                    if doc_ids:
                        i.have_reward = True
                    else:
                        i.have_reward = False
                else:
                    i.have_reward = False
            else:
                i.customer_loyalty = 0
                i.have_reward = False
