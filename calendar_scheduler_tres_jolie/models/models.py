# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('scheduler', "Scheduler")])


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('scheduler', "Scheduler")])


class CalenderSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    schedule_start = fields.Char(string="Schedule start")
    schedule_end = fields.Char(string="Schedule end")


class CalendarConfig(models.Model):
    _name = 'calender.config'

    @api.multi
    def restrict_done_appt_modif_non_admin(self, appt_state):
        pos_order = self.env['pos.order.line'].browse(self.id).order_id
        if not self.env.user.has_group('beauty_pos.group_user_saloon_admin')\
                and appt_state in ['done', 'paid', 'invoiced']:
            return True
        if self.env['res.users'].has_group('beauty_pos.group_help_desk') and pos_order.checkin:
            return True
        return False

    @api.model
    def update_calendar_schedule(self, time_slot):
        values_obj = self.env['ir.values']
        values_obj.set_default('res.config.settings',
                               'schedule_start',
                               str(time_slot[0]))
        values_obj.set_default('res.config.settings',
                               'schedule_end',
                               str(time_slot[1]))
        return True

    @api.model
    def fetch_calendar_extras(self):
        """Fetches extra details required for calender"""
        values_obj = self.env['ir.values']
        #  fetching time schedule
        time_schedule =  {
            'schedule_start': values_obj.get_default('res.config.settings',
                                                     'schedule_start'),
            'schedule_end': values_obj.get_default('res.config.settings',
                                                   'schedule_end')
        }

        cr = self._cr
        # fetch services(products) -start
        cr.execute("SELECT pt.name, pp.id,pt.id as product_template_id "
                   "FROM product_product pp "
                   "JOIN product_template pt "
                   "ON (pp.product_tmpl_id = pt.id) where pp.active and pt.type='service' ORDER BY pt.name")
        services = cr.dictfetchall()
        for serv in services:
            serv['staff_ids'] = self.env['product.template'].browse(serv['product_template_id']).staff_ids.ids
        # fetch services(products) -end

        # fetch customers - start
        cr.execute("SELECT id, CONCAT  (name, ' ', phone) as name "
                   "FROM res_partner ")
        customers = cr.dictfetchall()
        # fetch customers -end

        ir_values_obj = self.env['ir.values']
        default_config_staff_type = ir_values_obj.get_default('pos.config.settings', 'default_config_staff_type')
        config_staff_type = ''
        if default_config_staff_type:
            config_staff_type = 'service_based_staff'
        return [time_schedule,
                services,
                customers,
                config_staff_type
                ]

    @api.model
    def add_appointment(self, data):
        if not data.get('partner_id'):
            if data.get('customer_new_name') and data.get('customer_new_phone'):
                customer = self.env['res.partner'].create({'name': data.get('customer_new_name'),
                                                           'phone': data.get('customer_new_phone'),
                                                           'dob_month': data.get('customer_new_dob_month'),
                                                           'dob_day': data.get('customer_new_dob_day'),
                                                           })
                data['partner_id'] = customer.id
                data['phone'] = data.get('customer_new_phone')
        if not data.get('partner_id'):
            raise UserError('Set Customer')
        if data:
            for d_lines in data['lines']:
                d_lines[2]['checkin'] = False
                d_lines[2]['price_unit'] = self.env['product.product'].browse(d_lines[2]['product_id']).lst_price
            data['checkin'] = False
            order_id = self.env['pos.order'].create(data)
        return order_id.lines.ids


class OrderExtend(models.Model):
    _inherit = 'pos.order'

    @api.multi
    def action_cancel_order_js(self, appt_state):
        for order in self:
            self._cr.execute('UPDATE pos_order SET state=%s, state_appt=%s WHERE id=%s',
                             (appt_state, 'Cancelled', order.id))
            return True

    @api.model
    def create(self, vals):
        if not vals.get('session_id'):
            session = self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)],
                                                     limit=1)
            if session:
                vals['session_id'] = session.id
            else:
                raise UserError(_("There is no open session right now. You have to open one session to create bill!!!"))
        return super(OrderExtend, self).create(vals)

    @api.model
    def get_current_session(self):
        session = self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)
        if session:
            return True
        else:
            return False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_duration_in_min(self, servicesValue):
        servicesValue = int(servicesValue)
        duration = 0
        product = self.env['product.product'].browse(servicesValue)
        if product.type == 'service':
            if product.duration_in_min:
                duration = product.duration_in_min
            else:
                duration = 30
        return duration


class OrderLineExtend(models.Model):
    _inherit = 'pos.order.line'

    statement_ids = fields.One2many('account.bank.statement.line', string='Payments',related='order_id.statement_ids', readonly=1)
    note = fields.Text(related='order_id.note', string='Internal Notes', readonly=1)

