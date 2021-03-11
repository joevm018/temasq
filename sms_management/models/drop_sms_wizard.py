from odoo import fields, models, api, _
from xlrd import open_workbook
from odoo.exceptions import UserError
import requests


class DropSmsWizard(models.TransientModel):
    _name = "drop.sms"

    selection = fields.Selection([('customers', 'All Customers'),
                                  ('specific_customers', 'Specific Customers'),
                                  ('excel', 'Using Excel File'),
                                  ('numbers', 'Specific Numbers')], 'Choose option', required=True, default='customers')
    customer_ids = fields.Many2many('res.partner', 'cust_sms_rel', 'cust_sms_id', 'partner_id',
                                   string='Customers', domain=[('customer', '=', True)])
    mobiles = fields.Text('Mobile Numbers')
    mobile_numbers = fields.Text('Numbers', compute='_get_numbers')
    file = fields.Binary('Choose excel file')
    message = fields.Text('Message', required=True)

    @api.onchange('selection')
    def onchange_selection(self):
        if self.selection != 'specific_customers':
            self.customer_ids = False

    @api.depends('selection', 'file', 'mobiles')
    def _get_numbers(self):
        if self.selection == 'excel':
            if self.file:
                file_data = self.file.decode('base64')
                wb = open_workbook(file_contents=file_data)
                sheet = wb.sheet_by_index(0)
                num_rows = sheet.nrows
                num_cols = sheet.ncols
                result_data = ""
                for curr_row in range(0, num_rows, 1):
                    for curr_col in range(0, num_cols, 1):
                        data = sheet.cell_value(curr_row, curr_col)  # Read the data in the current cell
                        if type(data) == float:
                            data = int(data)
                            data = str(data)
                            if data:
                                result_data = result_data + data + ","
                        elif type(data) == unicode:
                            pass
                        else:
                            raise UserError(_("Please check file contents."))
                self.mobile_numbers = result_data
            else:
                self.mobile_numbers = False
        elif self.selection == 'numbers':
            self.mobile_numbers = self.mobiles
        else:
            pass

    def drop_sms(self):
        gateway_obj = self.env['gateway.setup'].search([], limit=1)
        if gateway_obj:
            url = eval(gateway_obj.gateway_url)
            params = eval(gateway_obj.parameter)
            if self.selection == 'customers':
                qry = "select name as customer, phone, id from res_partner where phone <> ''"
                self.env.cr.execute(qry)
                result = self.env.cr.fetchall()
                track_obj = self.env['sms.track']
                for res in result:
                    customer_name = res[0]
                    customer_name = customer_name.upper()
                    message = self.message
                    message = message.replace('{customer}', customer_name)
                    mobile = res[1]
                    if mobile and mobile.isdigit():
                        if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974'):
                            if len(mobile) == 8:
                                mobile = '974' + mobile
                            if gateway_obj.name == 'vodafone':
                                params['text'] = message
                                params['destination'] = mobile
                            else:
                                params['smsText'] = message
                                params['recipientPhone'] = mobile
                            response = requests.get(url, params=params)
                            status_code = response.status_code
                            value = {
                                'model_id': 'drop.sms-res.partner',
                                'res_id': res[2],
                                'mobile': mobile,
                                'customer_id': res[2],
                                'message': message,
                                'response': status_code,
                                'gateway_id': gateway_obj.id,

                            }
                            track_obj.create(value)
            elif self.selection == 'specific_customers':
                for custom in self.customer_ids:
                    if not custom.phone:
                        raise UserError(_("No mobile number found for %s!!")% (custom.name))
                qry = "select name as customer, phone, id from res_partner where phone <> '' and id in %s"
                self.env.cr.execute(qry, (tuple(self.customer_ids.ids), ))
                result = self.env.cr.fetchall()
                track_obj = self.env['sms.track']
                for res in result:
                    customer_name = res[0]
                    customer_name = customer_name.upper()
                    message = self.message
                    message = message.replace('{customer}', customer_name)
                    mobile = res[1]
                    if mobile and mobile.isdigit():
                        if len(mobile) == 8 or (len(mobile) == 11 and mobile[:3] == '974'):
                            if len(mobile) == 8:
                                mobile = '974' + mobile
                            if gateway_obj.name == 'vodafone':
                                params['text'] = message
                                params['destination'] = mobile
                            else:
                                params['smsText'] = message
                                params['recipientPhone'] = mobile
                            response = requests.get(url, params=params)
                            status_code = response.status_code
                            value = {
                                'model_id': 'drop.sms-res.partner',
                                'res_id': res[2],
                                'mobile': mobile,
                                'customer_id': res[2],
                                'message': message,
                                'response': status_code,
                                'gateway_id': gateway_obj.id,

                            }
                            track_obj.create(value)
            else:
                mobile = self.mobile_numbers
                if not mobile:
                    raise UserError(_("No mobile number found !!"))
                mobiles = mobile.split(',')
                mobs = []
                for i in mobiles:
                    if i and i.isdigit():
                        if len(i) == 8 or (len(i) == 11 and i[:3] == '974'):
                            num = i
                            if len(i) == 8:
                                num = '974' + i
                            mobs.append(num)
                message = self.message
                model = 'drop.sms'
                res_id = 1
                gateway_obj.send_sms(mobs, message, model, res_id)
        else:
            raise UserError(_("Please setup Gateway properly!!!"))
