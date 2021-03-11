from odoo import api, fields, models, tools, _


class ComboSession(models.Model):
    _name = 'combo.session'

    name = fields.Char('Ref', default='New', readonly=True)
    package_card_id = fields.Many2one('pos.customer.card', 'Package Card', readonly=True)
    order_id = fields.Many2one('pos.order', 'Redeemed for Order Ref', readonly=True)
    order_line_id = fields.Many2one('pos.order.line', 'Redeemed for Order Line Ref', readonly=True)
    customer_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    redeemed_date = fields.Date('Redeemed Date', readonly=True)
    combo_id = fields.Many2one('product.product', 'Combo Pack', required=True, readonly=True)
    product_id = fields.Many2one('product.product', 'Item', required=True, readonly=True)
    price = fields.Float('Offer Price', readonly=True)
    original_price = fields.Float('Actual Price', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], string='Status',
                             index=True, readonly=True, copy=False, default='draft')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('combo.session')
        return super(ComboSession, self).create(vals)