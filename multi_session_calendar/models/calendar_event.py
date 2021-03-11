from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    @api.model
    def _default_partners(self):
        """ When active_model is res.partner, the current partners should be attendees """
        return []

    name = fields.Char('Reference', required=True, default="NEW", readonly=True)
    phone = fields.Char('Phone')
    partner_ids = fields.Many2many('res.partner', 'calendar_event_res_partner_rel', string='Attendees',
                                   states={'done': [('readonly', True)]}, default=_default_partners)

    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)
    staff_id = fields.Many2one('hr.employee', string='Staff')
    checkin = fields.Boolean('Customer Present?', readonly=True)

    @api.onchange('stop_datetime')
    def _compute_stop(self):
        for order in self:
            if order.stop_datetime and order.start_datetime:
                duration = order._get_duration(order.start_datetime, order.stop_datetime)
                order.duration = duration

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('gym')
        return super(CalendarEvent, self).create(vals)

    @api.multi
    def unlink(self):
        checkin = 0
        del_ids = []
        for record in self:
            if record.checkin:
                checkin = 1
            else:
                if record.id not in del_ids:
                    del_ids.append(record.id)
        if len(del_ids) > 0:
            del_ids = self.browse(del_ids)
            return super(CalendarEvent, del_ids).unlink()
        if checkin == 1:
            raise UserError(_('The appointments for which customer already checkin can not be deleted !'))

    @api.multi
    def unlink_reccurent(self):
        delete_ids = []
        for record in self:
            if record.id not in delete_ids:
                delete_ids.append(record.id)
        for rcd in self:
            for recd in self.search([('name', '=', rcd.name)]):
                if recd.id not in delete_ids:
                    delete_ids.append(recd.id)
        unl_ids = []
        checkin = 0
        for i in self.browse(delete_ids):
            if i.checkin == True:
                checkin = 1
            else:
                if i.id not in unl_ids:
                    unl_ids.append(i.id)
        if checkin == 1:
            self.env.user.notify_info("The appointments for which customer already checkin can not be deleted !",
                                      title='Note', sticky=True)
        unlink_ids = self.browse(unl_ids)
        return super(CalendarEvent, unlink_ids).unlink()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for order in self:
            order.partner_ids = []
            if order.partner_id and order.partner_id.phone:
                order.phone = order.partner_id.phone

    @api.onchange('phone')
    def onchange_phone(self):
        for order in self:
            if order.partner_id:
                order.partner_id.write({'phone': order.phone})

    @api.multi
    def action_check_in(self):
        for order in self:
            order.write({'checkin': True})
