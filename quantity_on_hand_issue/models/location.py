from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _update_parent_left_right(self):
        self.env['product.category']._parent_store_compute()
        self.env['stock.location']._parent_store_compute()
        self.env['res.partner.category']._parent_store_compute()
        self.env['ir.ui.menu']._parent_store_compute()
        self.env['stock.quant.package']._parent_store_compute()
