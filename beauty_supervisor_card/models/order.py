from odoo import api, fields, models, _


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    active_for_supervisor = fields.Boolean('Active for supervisor')
    wizard_pin_update = fields.Boolean()
    discount_test = fields.Float("Discount Temp", readonly=False)
    price_unit_test = fields.Float("Unit price Temp", readonly=False)

    @api.onchange('discount')
    def get_discount_value(self):
        self.discount_test = self.discount

    @api.onchange('price_unit')
    def get_price_unit_value(self):
        self.price_unit_test = self.price_unit

    @api.model
    def create(self, vals):
        if vals.has_key('discount_test') and vals.has_key('is_order_line_foc'):
            vals['discount'] = vals['discount_test']
        if vals.has_key('price_unit_test') and vals['price_unit_test']>0:
            vals['price_unit'] = vals['price_unit_test']
        res = super(PosOrderLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.has_key('discount_test') and vals.has_key('is_order_line_foc'):
            vals['discount'] = vals['discount_test']
        if vals.has_key('price_unit_test'):
            vals['price_unit'] = vals['price_unit_test']
        res = super(PosOrderLine, self).write(vals)
        return res


class PosOrder(models.Model):
    _inherit = "pos.order"

    active_for_supervisor = fields.Boolean('Active for supervisor')
    wizard_pin_update = fields.Boolean()
    discount_percent_test = fields.Float("Total Discount(%) Temp", readonly=False)

    @api.onchange('discount_percent')
    def get_discount_percent_value(self):
        self.discount_percent_test = self.discount_percent

    @api.model
    def create(self, vals):
        if vals.has_key('discount_percent_test'):
            vals['discount_percent'] = vals['discount_percent_test']
        res = super(PosOrder, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.has_key('is_order_foc') and vals.has_key('discount_percent_test'):
            vals['discount_percent'] = vals['discount_percent_test']
        wizard_pin_update = vals.has_key('wizard_pin_update')
        if not wizard_pin_update:
            vals['active_for_supervisor'] = False
        res = super(PosOrder, self).write(vals)
        if not wizard_pin_update:
            for line in self.lines:
                line.write({'active_for_supervisor':False})
        return res

    def action_swipe_card_discount_order(self):
        return {
            'name': _('Change Price/Discount'),
            'view_id': self.env.ref('beauty_supervisor_card.view_change_price_discount_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'change.price.discount.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }