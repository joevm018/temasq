from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    combo_session_ids = fields.One2many('combo.session', 'order_id', 'Packages/Offers Sessions')


class ComboLines(models.Model):
    _inherit = 'combo.lines'

    name = fields.Many2one('product.template', 'Packages/Offer')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    combo_pack = fields.Boolean('Packages/Offer ?')


class ComboSession(models.Model):
    _inherit = 'combo.session'

    combo_id = fields.Many2one('product.product', 'Packages/Offer', required=True, readonly=True)


class ComboReportWizard(models.TransientModel):
    _inherit = 'combo.report.wizard'

    product_id = fields.Many2one('product.product', string="Packages/Offer", domain=[('combo_pack', '=', True)])
