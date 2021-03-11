from odoo import api, fields, models, tools, _


class Partner(models.Model):
    _inherit = "res.partner"

    have_home_service = fields.Boolean('Home Service', compute='_get_home_service', store=False)
    is_home_service = fields.Boolean('Home Service')

    @api.model
    def _get_home_service(self):
        order_obj = self.env['pos.order']
        for i in self.env['res.partner'].search([]):
            orders = order_obj.search([('have_home_service', '=', True), ('partner_id', '=', i.id)])
            if orders:
                i.have_home_service = True
                i.sudo().write({'is_home_service': True})
            else:
                i.have_home_service = False
                i.sudo().write({'is_home_service': False})
