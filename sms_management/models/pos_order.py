# -*- coding: utf-8 -*-
from odoo import fields, models, api, _,SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import pytz
from ast import literal_eval
from odoo import SUPERUSER_ID
import pytz


class PosOrder(models.Model):
    _inherit = "pos.order"

    def send_sms_cancel(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        reminder = self.env.ref('sms_management.appointment_cancel')
        message = reminder.message
        company_phone = ''
        if self.env.user.company_id.phone:
            company_phone = str(self.env.user.company_id.phone)
        gateway_obj = self.env['gateway.setup'].search([], limit=1)
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

    def send_appointment_sms(self, appt):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        reminder = self.env.ref('sms_management.appointment_reminder')
        message = reminder.message
        company_phone = ''
        if self.env.user.company_id.phone:
            company_phone = str(self.env.user.company_id.phone)
        gateway_obj = self.env['gateway.setup'].search([], limit=1)
        if gateway_obj:
            url = eval(gateway_obj.gateway_url)
            params = eval(gateway_obj.parameter)
            track_obj = self.env['sms.track']
            date_order = datetime.strptime(appt.date_order, '%Y-%m-%d %H:%M:%S')
            user = self.env['res.users'].browse(SUPERUSER_ID)
            tz = pytz.timezone(user.partner_id.tz) or pytz.utc
            date_order = pytz.utc.localize(date_order).astimezone(tz)
            date_order = date_order.strftime('%d/%m/%Y %I:%M %p')
            appt_date = date_order[:10]
            appt_time = date_order[11:]
            salon = self.env.user.company_id.name
            salon = salon.upper()
            if appt.partner_id.phone:
                mobile = appt.partner_id.phone
                if mobile and mobile.isdigit():
                    if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974'):
                        if len(mobile) == 8:
                            mobile = '974' + mobile
                        customer_name = appt.partner_id.name
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
                            'res_id': appt.id,
                            'mobile': mobile,
                            'customer_id': appt.partner_id.id,
                            'message': message,
                            'response': status_code,
                            'gateway_id': gateway_obj.id,
                        }
                        track_obj.create(value)
            else:
                print ("No mobile number found!!!")
        else:
            print ("Please setup Gateway properly!!!")

    # @api.model
    # def create(self, values):
    #     res = super(PosOrder, self).create(values)
    #     res.send_appointment_sms(res)
    #     return res

    @api.multi
    def resend_sms_from_appt(self):
        self.send_appointment_sms(self)

    def _tomorrow_appointment_reminder(self):
        date_today = datetime.now()
        date_today = date_today.replace(hour=0, minute=0, second=0, microsecond=0)
        date_today = datetime.strptime(str(date_today), '%Y-%m-%d %H:%M:%S')
        date_tomorrow = date_today + relativedelta(days=1)
        tomorrow_end = date_tomorrow + relativedelta(days=2)
        appointments = self.env['pos.order'].search([('date_order', '>=', str(date_tomorrow)),
                                                     ('date_order', '<', str(tomorrow_end)),
                                                     ('state', '=', 'draft'),
                                                     ('partner_id', '!=', False),
                                                     ('checkin', '=', False)])
        reminder = self.env.ref('sms_management.appointment_reminder')
        company_phone = self.env.user.company_id.phone

        gateway_obj = self.env['gateway.setup'].search([], limit=1)
        if gateway_obj:
            url = eval(gateway_obj.gateway_url)
            params = eval(gateway_obj.parameter)
            track_obj = self.env['sms.track']
            for appt in appointments:
                date_order = datetime.strptime(appt.date_order, '%Y-%m-%d %H:%M:%S')
                user = self.env['res.users'].browse(SUPERUSER_ID)
                tz = pytz.timezone(user.partner_id.tz) or pytz.utc
                date_order = pytz.utc.localize(date_order).astimezone(tz)
                date_order = date_order.strftime('%d/%m/%Y %I:%M %p')
                appt_date = date_order[:10]
                appt_time = date_order[11:]
                salon = self.env.user.company_id.name
                salon = salon.upper()
                if appt.partner_id.phone:
                    mobile = appt.partner_id.phone
                    if mobile and mobile.isdigit():
                        if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974'):
                            if len(mobile) == 8:
                                mobile = '974' + mobile
                            customer_name = appt.partner_id.name
                            customer_name = customer_name.upper()
                            message = reminder.message
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
                                'res_id': appt.id,
                                'mobile': mobile,
                                'customer_id': appt.partner_id.id,
                                'message': message,
                                'response': status_code,
                                'gateway_id': gateway_obj.id,
                            }
                            track_obj.create(value)
                else:
                    print ("No mobile number found!!!")
        else:
            print ("Please setup Gateway properly!!!")

    def _today_appointment_reminder(self):
        user = self.env['res.users'].browse(SUPERUSER_ID)
        time_now = datetime.now()
        time_now = time_now.replace(second=0, microsecond=0)
        time_now = datetime.strptime(str(time_now), '%Y-%m-%d %H:%M:%S')
        ir_values_obj = self.env['ir.values']
        minutes = ir_values_obj.sudo().get_default('sms.config.settings', "appointment_alert")
        time_now = time_now + relativedelta(minutes=minutes)
        time_end = time_now + relativedelta(minutes=1)
        appointments = self.env['pos.order'].search([('date_order', '>=', str(time_now)),
                                                     ('date_order', '<', str(time_end)),
                                                     ('state', '=', 'draft'),
                                                     ('partner_id', '!=', False),
                                                     ('checkin', '=', False)])
        reminder = self.env.ref('sms_management.appointment_reminder')
        message = reminder.message
        company_phone = self.env.user.company_id.phone

        gateway_obj = self.env['gateway.setup'].search([], limit=1)
        if gateway_obj:
            url = eval(gateway_obj.gateway_url)
            params = eval(gateway_obj.parameter)
            track_obj = self.env['sms.track']
            for appt in appointments:
                date_order = datetime.strptime(appt.date_order, '%Y-%m-%d %H:%M:%S')
                user = self.env['res.users'].browse(SUPERUSER_ID)
                tz = pytz.timezone(user.partner_id.tz) or pytz.utc
                date_order = pytz.utc.localize(date_order).astimezone(tz)
                date_order = date_order.strftime('%d/%m/%Y %I:%M %p')
                appt_date = date_order[:10]
                appt_time = date_order[11:]
                salon = self.env.user.company_id.name
                salon = salon.upper()
                if appt.partner_id.phone:
                    mobile = appt.partner_id.phone
                    if mobile and mobile.isdigit():
                        if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974'):
                            if len(mobile) == 8:
                                mobile = '974' + mobile
                            customer_name = appt.partner_id.name
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
                                'res_id': appt.id,
                                'mobile': mobile,
                                'customer_id': appt.partner_id.id,
                                'message': message,
                                'response': status_code,
                                'gateway_id': gateway_obj.id,
                            }
                            track_obj.create(value)
                else:
                    print ("No mobile number found!!!")
        else:
            print ("Please setup Gateway properly!!!")
