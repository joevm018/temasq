# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosOrderInherited(models.Model):
    _inherit = "pos.order"

    delivery_note = fields.Char(string='Delivery note')
    delivery_category = fields.Selection([('HOME DELIVERY', 'HOME DELIVERY'), ('SALES', 'SALES')],
                                         string='Delivery Category')

    @api.model
    def _order_fields(self, ui_order):
        delivery_details = super(PosOrderInherited, self)._order_fields(ui_order)
        if ui_order.get('delivery_note'):
            delivery_details['delivery_note'] = ui_order['delivery_note']
        if ui_order.get('delivery_category'):
            delivery_details['delivery_category'] = ui_order['delivery_category']
        return delivery_details

    @api.multi
    def print_bill(self):
        return self.env['report'].get_action(self.id, 'point_of_sale.report_invoice')


