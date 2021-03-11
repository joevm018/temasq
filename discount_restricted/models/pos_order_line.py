# -*- coding: utf-8 -*-

import logging
from odoo import fields, api, models
from odoo.tools.translate import _
from odoo.exceptions import UserError


class NewPosOrderLine(models.Model):
    _inherit = "pos.order.line"

    show_discount = fields.Boolean('Show Discount', compute='get_show_discount')

    @api.model
    @api.depends('product_id')
    def get_show_discount(self):
        for i in self:
            if i.product_id:
                if i.product_id.type == 'service':
                    i.show_discount = True
                else:
                    i.show_discount = False
            else:
                i.show_discount = False