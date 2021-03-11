# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    consum_income_acc = fields.Many2one('account.account', string='Consumable Income Account', domain=[('deprecated', '=', False)])
    consum_expense_acc = fields.Many2one('account.account', string='Consumable Expense Account', domain=[('deprecated', '=', False)])
    retail_income_acc = fields.Many2one('account.account', string='Retail Income Account', domain=[('deprecated', '=', False)])
    retail_expense_acc = fields.Many2one('account.account', string='Retail Expense Account', domain=[('deprecated', '=', False)])
    service_income_acc = fields.Many2one('account.account', string='Service Income Account', domain=[('deprecated', '=', False)])
    service_expense_acc = fields.Many2one('account.account', string='Service Expense Account', domain=[('deprecated', '=', False)])

    @api.multi
    def set_consum_income_acc(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'consum_income_acc', self.consum_income_acc.id)

    @api.model
    def get_consum_income_acc(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('account.config.settings', "consum_income_acc")
        res = {'consum_income_acc': value}
        return res

    @api.multi
    def set_consum_expense_acc(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'consum_expense_acc', self.consum_expense_acc.id)

    @api.model
    def get_consum_expense_acc(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('account.config.settings', "consum_expense_acc")
        res = {'consum_expense_acc': value}
        return res

    @api.multi
    def set_retail_income_acc(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'retail_income_acc', self.retail_income_acc.id)

    @api.model
    def get_retail_income_acc(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('account.config.settings', "retail_income_acc")
        res = {'retail_income_acc': value}
        return res

    @api.multi
    def set_retail_expense_acc(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'retail_expense_acc', self.retail_expense_acc.id)

    @api.model
    def get_retail_expense_acc(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('account.config.settings', "retail_expense_acc")
        res = {'retail_expense_acc': value}
        return res

    @api.multi
    def set_service_income_acc(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'service_income_acc', self.service_income_acc.id)

    @api.model
    def get_service_income_acc(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('account.config.settings', "service_income_acc")
        res = {'service_income_acc': value}
        return res

    @api.multi
    def set_service_expense_acc(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'service_expense_acc', self.service_expense_acc.id)

    @api.model
    def get_service_expense_acc(self, fields_list):
        ir_values_obj = self.env['ir.values']
        value = ir_values_obj.sudo().get_default('account.config.settings', "service_expense_acc")
        res = {'service_expense_acc': value}
        return res

