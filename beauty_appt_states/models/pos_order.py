# -*- coding: utf-8 -*-
import logging
from odoo import fields, api, models, SUPERUSER_ID
from datetime import datetime
import pytz
import requests

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    no_response = fields.Boolean('No Response')
    is_confirmed = fields.Boolean('Confirmed')
    is_executed = fields.Boolean('Executed')
    state_appt = fields.Selection([
        ('Booked', 'Booked'),
        ('Confirmed', 'Confirmed'),
        ('No Response', 'No Response'),
        ('Cancelled', 'Cancelled'),
        ('Executed', 'Executed')
    ], 'Appt state', readonly=True, track_visibility='onchange', copy=False, default='Booked')
    state = fields.Selection(inverse='_inverse_state')

    @api.multi
    def action_cancel_appt(self):
        res = super(PosOrder, self).action_cancel_appt()
        for order in self:
            order.write({'state_appt': 'Cancelled'})
        return res

    @api.multi
    def _inverse_state(self):
        for order in self:
            if order.state and order.state == 'paid':
                order.write({'state_appt': 'Executed'})
                order.write({'is_executed': True})
            if order.state and order.state == 'cancel':
                order.write({'state_appt': 'Cancelled'})

    @api.multi
    def apply_confirm(self):
        for order in self:
            order.write({'state_appt': 'Confirmed'})
            order.write({'is_confirmed': True})

    @api.multi
    def apply_execute(self):
        for order in self:
            order.write({'state_appt': 'Executed'})
            order.write({'is_executed': True})

    def send_sms_noresponse(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        reminder = self.env.ref('beauty_appt_states.appointment_no_response')
        message = reminder.message
        company_phone = ''
        if self.env.user.company_id.phone:
            company_phone = str(self.env.user.company_id.phone)
        gateway_obj = self.env['gateway.setup'].search([], limit=1)
        self.no_response = True
        self.state_appt = 'No Response'
        if gateway_obj:
            url = eval(gateway_obj.gateway_url)
            params = eval(gateway_obj.parameter)
            track_obj = self.env['sms.track']
            date_order = datetime.strptime(self.date_order, '%Y-%m-%d %H:%M:%S')
            user = self.env['res.users'].browse(SUPERUSER_ID)
            tz = pytz.timezone(user.partner_id.tz) or pytz.utc
            date_order = pytz.utc.localize(date_order).astimezone(tz)
            date_order = date_order.strftime('%d/%m/%Y %I:%M %p')
            appt_date = date_order[:10]
            appt_time = date_order[11:]
            salon = self.env.user.company_id.name
            salon = salon.upper()
            if self.partner_id.phone:
                mobile = self.partner_id.phone
                if mobile and mobile.isdigit():
                    if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974'):
                        if len(mobile) == 8:
                            mobile = '974' + mobile
                        customer_name = self.partner_id.name
                        customer_name = customer_name.upper()
                        message = message.replace('{customer}', customer_name).replace('{salon}', salon). \
                            replace('{appt_date}', appt_date).replace('{appt_time}', appt_time). \
                            replace('{company_phone}', company_phone)
                        mobile = str(mobile)
                        if gateway_obj.name == 'vodafone':
                            params['text'] = message
                            params['destination'] = mobile
                        else:
                            params['smsText'] = message
                            params['recipientPhone'] = mobile
                        response = requests.get(url, params=params)
                        status_code = response.status_code
                        value = {
                            'model_id': 'pos.order',
                            'res_id': self.id,
                            'mobile': mobile,
                            'customer_id': self.partner_id.id,
                            'message': message,
                            'response': status_code,
                            'gateway_id': gateway_obj.id,
                        }
                        track_obj.create(value)
            else:
                print ("No mobile number found!!!")
        else:
            print ("Please setup Gateway properly!!!")


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    state_appt = fields.Selection([
        ('Booked', 'Booked'),
        ('Confirmed', 'Confirmed'),
        ('No Response', 'No Response'),
        ('Cancelled', 'Cancelled'),
        ('Executed', 'Executed')
    ], 'Appt state', readonly=True, track_visibility='onchange', copy=False, related='order_id.state_appt')
