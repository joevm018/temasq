from odoo import api, fields, models, tools, _


class ComboSession(models.Model):
    _inherit = 'combo.session'

    @api.model
    def create(self, vals):
        res = super(ComboSession, self).create(vals)
        if res.customer_id:
            res.customer_id.is_combo = True
        return res


class Partner(models.Model):
    _inherit = "res.partner"

    is_combo = fields.Boolean(
        string='Have combo',
        compute="check_have_combo",
        search="search_have_combo")

    def name_get(self):
        res = []
        for record in self:
            if record.phone:
                res.append((record['id'], "%s %s" % (record.phone, record.name)))
            else:
                res.append((record['id'], "%s" % (record.name)))
        return res

    def check_have_combo(self):
        for rec in self:
            combo = self.env['combo.session'].search([
                ('state', '=', 'draft'),
                ('customer_id', '=', rec.id)])
            booked = self.env['pos.order.line'].search([
                ('combo_session_id', 'in', combo.ids)])
            booked = booked and booked.mapped('combo_session_id').ids or []
            available = combo.filtered(lambda c: c.id not in booked)
            rec.is_combo = available and True or False

    @api.multi
    def search_have_combo(self, operator, value):
        combo = self.env['combo.session'].search([('state', '=', 'draft')])
        booked = self.env['pos.order.line'].search([
            ('combo_session_id', 'in', combo.ids)])
        booked = booked and booked.mapped('combo_session_id').ids or []
        available = combo.filtered(lambda c: c.id not in booked)
        customer_domain = [
            ('id', 'in', combo and available.mapped('customer_id').ids or [])]
        return customer_domain
