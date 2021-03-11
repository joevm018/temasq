# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SwipeCard(models.TransientModel):
    _name = 'swipe.card'

    card_no = fields.Char('Card No', required=True)

    def action_confirm(self):
        order_obj = self.env['pos.order'].browse(self.env.context.get('active_id'))
        customer_obj = self.env['res.partner'].search([('barcode', '=', self.card_no)], limit=1)
        if customer_obj:
            order_obj.card_no = self.card_no
        else:
            raise UserError('There is no customer with the card number entered.')
