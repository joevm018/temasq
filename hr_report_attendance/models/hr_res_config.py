# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    mail_to_hr = fields.Char('HR Email')
    normal_working_hr = fields.Float('Organization Normal working hours per day', required=True)

    @api.multi
    def set_mail_to_hr(self):
        return self.env['ir.values'].sudo().set_default('base.config.settings', 'mail_to_hr', self.mail_to_hr)

    @api.model
    def get_mail_to_hr(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('base.config.settings', "mail_to_hr")
        res = {'mail_to_hr': value}
        return res

    @api.multi
    def set_normal_working_hr(self):
        return self.env['ir.values'].sudo().set_default('base.config.settings', 'normal_working_hr', self.normal_working_hr)

    @api.model
    def get_normal_working_hr(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('base.config.settings', "normal_working_hr")
        res = {'normal_working_hr': value}
        return res