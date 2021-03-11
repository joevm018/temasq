# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from ast import literal_eval
from odoo.exceptions import ValidationError


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    default_bank_id = fields.Many2one('account.journal', 'Default Bank', domain=[('type', '=', 'bank')], required=True)
    default_card_id = fields.Many2one('account.journal', 'Default Card Journal', domain=[('type', '=', 'bank')], required=True)

    @api.multi
    def set_default_bank_id(self):
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'default_bank_id',
                                                        self.default_bank_id.id)

    @api.model
    def get_default_bank_id(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('account.config.settings', "default_bank_id")
        res = {'default_bank_id': value}
        return res

    @api.multi
    def set_default_card_id(self):
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'default_card_id',
                                                        self.default_card_id.id)

    @api.model
    def get_default_card_id(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('account.config.settings', "default_card_id")
        res = {'default_card_id': value}
        return res



class ResCompany(models.Model):
    _inherit = "res.company"

    @api.constrains('default_bank_id', 'name')
    def _check_same_company_default_bank_id(self):
        if self.default_bank_id.company_id:
            if self.id != self.default_bank_id.company_id.id:
                raise ValidationError(_('Error ! Bank Journal should be of same company'))

    default_bank_id = fields.Many2one('account.journal', 'Default Bank', domain=[('type', '=', 'bank')], required=False)


    @api.constrains('default_card_id', 'name')
    def _check_same_company_default_card_id(self):
        if self.default_card_id.company_id:
            if self.id != self.default_card_id.company_id.id:
                raise ValidationError(_('Error ! Card Journal should be of same company'))

    default_card_id = fields.Many2one('account.journal', 'Default Card Journal', domain=[('type', '=', 'bank')],
                                      required=False)