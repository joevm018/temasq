# -*- coding: utf-8 -*-
import math
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    def print_barcode(self):
        if not self.product_id.barcode:
            raise UserError(_('Please generate barcode for the product.'))
        return self.env['report'].get_action(self.id, 'beauty_pos.report_lot_barcode')