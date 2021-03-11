# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _get_product_domain(self):
        domain_company = [('purchase_ok', '=', True)]
        id_list = []
        if self.partner_id and self.order_id.product_list:
            id_list = self.order_id.product_list.ids
        domain_company.append(('id', 'in', id_list))
        return domain_company

    product_id = fields.Many2one('product.product', string='Product', domain=_get_product_domain,
                                 change_default=True, required=True)

    @api.onchange('product_id')
    def onchange_treatment_ids(self):
        domain = self._get_product_domain()
        return {
            'domain': {'product_id': domain}
        }


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    product_list = fields.Many2many(comodel_name="product.product", relation="purchase_inherit_product_product_rel",
                                    string="product List")

    @api.onchange('partner_id')
    def compute_pdt_list(self):
        for record in self:
            products = False
            if self.partner_id:
                products = self.env['supplier.cost'].search([('name', '=', self.partner_id.id)])
                if self.partner_id.parent_id:
                    products = self.env['supplier.cost'].search([('name', '=', self.partner_id.parent_id.id)])

            product_list = []
            if products:
                for i in products:
                    if i.id not in product_list:
                        product_list.append(i.product_tmpl_id.product_variant_id.id)

                record.update({'product_list': [(6, 0, product_list)]})
            else:
                record.update({'product_list': False})

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrderInherit, self).button_confirm()
        supplier_cost_obj = self.env['supplier.cost']
        for po in self:
            for line in po.order_line:
                supplier_cost = supplier_cost_obj.search([('name', '=', self.partner_id.id),
                                                          ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                for cost in supplier_cost:
                    cost.cost = line.price_unit
