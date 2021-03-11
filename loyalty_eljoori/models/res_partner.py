# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_purchase_date = fields.Date('Loyalty Purchase Date')

    def _get_loyalty(self):
        for partner in self:
            loyalty = 0
            if partner.id and partner.barcode:
                orders = self.env['pos.order'].search([('partner_id', '=', partner.id),
                                                       ('date_order', '>=', partner.loyalty_purchase_date),
                                                       ('state', 'in', ('paid', 'posted'))])
                for order in orders:
                    loyalty += order.loyalty_points
            partner.loyalty_points = loyalty
