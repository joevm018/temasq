# -*- coding: utf-8 -*-
import math
import re
from odoo import api, fields, models,exceptions
from odoo.exceptions import Warning as UserError


class BarcodeWizard(models.TransientModel):
    _name = "barcode.wizard"

    def action_confirm(self):
        active_ids = self.env.context.get('active_ids', [])
        pdts = self.env['product.template'].search([('id', 'in', active_ids)])
        for i in pdts:
            i.generate_barcode()
