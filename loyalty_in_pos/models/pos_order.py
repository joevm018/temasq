# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    reward_id = fields.Many2one('loyalty.reward', 'Loyalty reward')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    customer_loyalty = fields.Float('Remaining Loyalty Points', compute='_get_loyalty_points')
    loyalty_won = fields.Float('Earned points', readonly=True, compute='_get_points')
    points_spent = fields.Float('Loyalty Points Spent', readonly=True, compute='_get_points')
    loyalty_points = fields.Float(string='Loyalty Points on this order', readonly=True, copy=False,
                                  compute='_get_points',
                                  help='The amount of Loyalty points awarded '
                                       'to the customer with this order')
    have_reward = fields.Boolean('Have Reward?', compute='_get_loyalty_points')

    @api.depends('partner_id', 'lines')
    def _get_points(self):
        for order in self:
            spent = 0
            won = 0
            product_sold = 0
            total_sold = 0
            loyalty_obj = order.session_id.config_id.loyalty_id
            rounding = loyalty_obj.rounding
            if loyalty_obj and order.partner_id:
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
                            won += round(total_sold * loyalty_obj.pp_currency,1)
                            won += round(product_sold * loyalty_obj.pp_product,1)
                            won += round(loyalty_obj.pp_order,1)
            order.loyalty_won = won
            order.points_spent = spent
            order.loyalty_points = won - spent

    @api.multi
    def action_loyalty(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rewards',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'reward.wizard',
            'target': 'new',
            'context': {}
        }

    @api.depends('partner_id', 'state', 'session_id', 'lines')
    def _get_loyalty_points(self):
        for i in self:
            if i.partner_id:
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

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        # res['loyalty_points'] = ui_order.get('loyalty_points', 0)
        return res

    @api.model
    def create_from_ui(self, orders):
        res = super(PosOrder, self).create_from_ui(orders)
        for order in orders:
            order_partner = order['data']['partner_id']
            order_points = order['data'].get('loyalty_points', 0)
            # if order_points != 0 and order_partner:
            #     partner = self.env['res.partner'].browse(order_partner)
            #     partner.loyalty_points += order_points
        return res
