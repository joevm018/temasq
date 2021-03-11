from odoo import api, fields, models, tools, _


class SalonRoom(models.Model):
    _name = "salon.room"

    name = fields.Char('Name', default='NEW')
    facilities = fields.Text('Facilities')

    @api.model
    def create(self, vals):
        if vals.get('name') == 'NEW':
            vals['name'] = self.env['ir.sequence'].next_by_code('salon.room')
        return super(SalonRoom, self).create(vals)
