from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_state = fields.Selection([('Packing', 'Packing'), ('On the Way', 'On the Way'), ('Delivered', 'Delivered')],
                             string='Order Status')
