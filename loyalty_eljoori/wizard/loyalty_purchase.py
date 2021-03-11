# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class LoyaltyPurchase(models.TransientModel):
    _name = 'loyalty.purchase'

    loyalty_purchase_date = fields.Date('Purchased On', required=True, default=fields.Date.today)
    card_no = fields.Char('Card No', required=True)

    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        customers = self.env['res.partner'].search([('barcode', '=', self.card_no)])
        for i in customers:
            raise UserError(_("Found another customer with same card number !!"))
        if active_id:
            order = self.env['pos.order'].browse(active_id)
            order_list = []
            product_loyalty_card = self.env.ref('loyalty_eljoori.product_loyalty_card')
            order_list.append(self.env['pos.order.line'].create({
                'name': product_loyalty_card.name,
                'product_id': product_loyalty_card.id,
                'price_unit': product_loyalty_card.list_price,
            }).id)
            for ord in order.lines:
                order_list.append(ord.id)
            order['lines'] = [(6, 0, order_list)]
            partner_id = order.partner_id
            partner_id.barcode = self.card_no
            order.card_no = self.card_no
            partner_id.loyalty_purchase_date = self.loyalty_purchase_date
            order._get_have_loyalty()
            order.have_loyalty_card = True

