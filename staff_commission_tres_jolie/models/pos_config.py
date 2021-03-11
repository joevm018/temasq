# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosConfigSettings(models.TransientModel):
    _inherit = 'pos.config.settings'

    default_item_commission = fields.Float(
        string="Default Item Commission Percentage",
        default=10)
    default_commission_type = fields.Selection(
        [('fixed', 'Fixed'), ('percentage', 'Percentage')],
        string='Default Commission Type', default='fixed', required=True)

    @api.multi
    def set_default_commission_type(self):
        ir_values_obj = self.env['ir.values'].sudo()
        ir_values_obj.set_default(
            'pos.config.settings', 'default_commission_type',
            self.default_commission_type)
        ir_values_obj.set_default(
            'pos.config.settings', 'default_item_commission',
            self.default_item_commission)

    @api.model
    def get_default_commission_type(self, fields_list):
        ir_values = self.env['ir.values'].sudo()
        default_commission_type = ir_values.get_default(
            'pos.config.settings', "default_commission_type")
        default_item_commission = ir_values.get_default(
            'pos.config.settings', "default_item_commission")
        res = {
            'default_commission_type': default_commission_type or 'fixed',
            'default_item_commission': default_item_commission or 10,
        }
        return res
