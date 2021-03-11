from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class WebsiteCart(models.Model):
    _name = 'website.cart'
    _description = 'Website Cart'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Customer',required=True, domain=[('customer', '=', True)])
    cart_line = fields.One2many('website.cart.line', 'cart_id', string='Cart Lines', copy=True)


class WebsiteCartLine(models.Model):
    _name = 'website.cart.line'
    _description = 'Website Cart Line'

    cart_id = fields.Many2one('website.cart', string='Cart Reference', required=True, ondelete='cascade', copy=False)
    date_order = fields.Datetime(string='Date', required=True, copy=False, default=fields.Datetime.now)
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
                                   default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        vals = {}
        vals['product_uom_qty'] = 1.0
        product = self.product_id
        # name = product.name_get()[0][1]
        vals['name'] = product.name
        if not self.price_unit:
            vals['price_unit'] = product.list_price
        self.update(vals)