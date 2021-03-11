# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from ast import literal_eval
from odoo.exceptions import ValidationError


class PosConfigSettings(models.TransientModel):
    _inherit = 'pos.config.settings'

    expiry_day = fields.Integer(string='Retail Items Expiry Alert before (Days)', default=30)
    consu_expiry_day = fields.Integer(string='Salon use Items Expiry Alert before (Days)', default=30)

    @api.multi
    def set_expiry_day(self):
        return self.env['ir.values'].sudo().set_default('pos.config.settings', 'expiry_day',
                                                        self.expiry_day)

    @api.model
    def get_expiry_day(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('pos.config.settings', "expiry_day")
        res = {'expiry_day': value}
        return res

    @api.multi
    def set_consu_expiry_day(self):
        return self.env['ir.values'].sudo().set_default('pos.config.settings', 'consu_expiry_day',
                                                        self.consu_expiry_day)

    @api.model
    def get_consu_expiry_day(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('pos.config.settings', "consu_expiry_day")
        res = {'consu_expiry_day': value}
        return res
