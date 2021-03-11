# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    staff_ids = fields.Many2many('hr.employee', 'service_staff_relation', 'service_id', 'staff_id', string='Staffs',
                                 domain=[('is_beautician', '=', True)])

    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        ir_values = self.env['ir.values']
        if res.get('type') == 'consu':
            res['property_account_income_id'] = ir_values.get_default('account.config.settings', 'consum_income_acc')
            res['property_account_expense_id'] = ir_values.get_default('account.config.settings', 'consum_expense_acc')
        if res.get('type') == 'product':
            res['property_account_income_id'] = ir_values.get_default('account.config.settings', 'retail_income_acc')
            res['property_account_expense_id'] = ir_values.get_default('account.config.settings', 'retail_expense_acc')
        if res.get('type') == 'service':
            res['property_account_income_id'] = ir_values.get_default('account.config.settings', 'service_income_acc')
            res['property_account_expense_id'] = ir_values.get_default('account.config.settings', 'service_expense_acc')
        return res

    @api.model
    def create(self, vals):
        ir_values = self.env['ir.values']
        if vals.get('type') == 'consu':
            vals['property_account_income_id'] = ir_values.get_default('account.config.settings', 'consum_income_acc')
            vals['property_account_expense_id'] = ir_values.get_default('account.config.settings', 'consum_expense_acc')
        if vals.get('type') == 'product':
            vals['property_account_income_id'] = ir_values.get_default('account.config.settings', 'retail_income_acc')
            vals['property_account_expense_id'] = ir_values.get_default('account.config.settings', 'retail_expense_acc')
        if vals.get('type') == 'service':
            vals['property_account_income_id'] = ir_values.get_default('account.config.settings', 'service_income_acc')
            vals['property_account_expense_id'] = ir_values.get_default('account.config.settings', 'service_expense_acc')
        res = super(ProductTemplate, self).create(vals)
        product = self.env["product.product"].search([("product_tmpl_id", "=", res.id)])
        if product.type == 'consu':
            product.write({'available_in_pos':False})
        return res



