# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class SmsConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'sms.config.settings'

    appointment_alert = fields.Integer('Appointment alert before', default=30, required=True)

    @api.multi
    def set_appointment_alert(self):
        return self.env['ir.values'].sudo().set_default('sms.config.settings', 'appointment_alert', self.appointment_alert)

    @api.model
    def get_appointment_alert(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('sms.config.settings', "appointment_alert")
        res = {'appointment_alert': value}
        return res