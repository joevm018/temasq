# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from ast import literal_eval
from odoo.exceptions import ValidationError


class PosConfigSettings(models.TransientModel):
    _inherit = 'pos.config.settings'

    default_config_staff_type = fields.Boolean(string='Staff domain in scheduler based on selected service')

    @api.multi
    def set_default_config_staff_type(self):
        return self.env['ir.values'].sudo().set_default('pos.config.settings', 'default_config_staff_type',
                                                        self.default_config_staff_type)

    @api.model
    def get_default_config_staff_type(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('pos.config.settings', "default_config_staff_type")
        res = {'default_config_staff_type': value}
        return res