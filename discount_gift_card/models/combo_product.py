from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import datetime
import odoo.addons.decimal_precision as dp


class ComboLines(models.Model):
    _name = 'combo.lines'

    name = fields.Many2one('product.template', 'Combo Pack')
    product_id = fields.Many2one('product.product', 'Item', domain=[('combo_pack', '=', False)], required=True)
    count = fields.Integer('Count', default=1)
    price = fields.Float('Offer Price Per Unit', store=True)
    subtotal = fields.Float('Sub Total', compute='_get_subtotal', store=True)

    @api.multi
    @api.depends('price', 'count')
    def _get_subtotal(self):
        for line in self:
            line.subtotal = line.count * line.price

    @api.onchange('product_id')
    def onchange_product(self):
        for i in self:
            if i.product_id:
                i.price = i.product_id.list_price


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    combo_pack = fields.Boolean('Combo Pack')
    pack_ids = fields.One2many('combo.lines', 'name', 'Combo Items')
    valid_period = fields.Boolean('Specify Valid Period..')
    start_date = fields.Date('Valid From')
    end_date = fields.Date('Valid Until')
    update_active = fields.Boolean('Update', compute='_get_active_update')
    list_price = fields.Float(
        'Sale Price', default=1.0, store=True,
        digits=dp.get_precision('Product Price'),
        help="Base price to compute the customer price. Sometimes called the catalog price.")

    @api.onchange('pack_ids')
    def onchange_pack_ids(self):
        for pdt in self:
            if pdt.pack_ids:
                price = 0
                for item in pdt.pack_ids:
                    price += item.subtotal
                pdt.write({'list_price': price, 'lst_price': price})
            else:
                pdt.write({'list_price': 0, 'lst_price': 0})

    @api.multi
    @api.depends('valid_period', 'start_date', 'end_date')
    def _get_active_update(self):
        for pdt in self:
            if pdt.valid_period:
                today_date = datetime.utcnow().date()
                if pdt.start_date and pdt.end_date:
                    start_date = datetime.strptime(str(pdt.start_date), '%Y-%m-%d').date()
                    end_date = datetime.strptime(str(pdt.end_date), '%Y-%m-%d').date()
                    if start_date <= today_date <= end_date:
                        pdt_obj = self.env['product.product'].search([('product_tmpl_id', '=', pdt.id), ('active', '=', False)])
                        if pdt_obj:
                            pdt_obj.active = True
                            pdt.write({'active': True})
                    else:
                        pdt_obj = self.env['product.product'].search([('product_tmpl_id', '=', pdt.id)])
                        if pdt_obj:
                            pdt_obj.active = False
                            pdt.write({'active': False})
            else:
                pdt.active = True
