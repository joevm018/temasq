from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class Partner(models.Model):
    _inherit = "res.partner"

    display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    pos_order_count = fields.Integer(compute='_compute_pos_order',
                                     help="The number of point of sale orders related to this customer",
                                     groups="point_of_sale.group_pos_user,beauty_pos.group_help_desk",
                                     )

    @api.depends('is_company', 'name', 'phone', 'parent_id.name', 'type', 'company_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    def name_get(self):
        res = []
        for record in self:
            if record.phone:
                res.append((record['id'], "[%s] %s" % (record.phone, record.name)))
            else:
                res.append((record['id'], "%s" % (record.name)))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('phone', operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):
            name = d.get('name', '')
            if len(name) > 100:
                name = name[0:100]
            # code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            # if code:
            #     name = '[%s] %s' % (code,name)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []
        for product in self.sudo():
            # display only the attributes with multiple possible values on the template
            variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped(
                'attribute_id')
            variant = product.attribute_value_ids._variant_name(variable_attributes)

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and (x.product_id == product)]
                if not sellers:
                    sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and not x.product_id]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                            variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                    }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                }
                result.append(_name_get(mydict))
        return result


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char('Name', index=True, required=True, translate=True, size=1024)
    notes_new = fields.Text('Notes')
    duration_in_min = fields.Integer('Duration(In min)')
    make_helpdesk_invisible = fields.Boolean(string="User", compute='_make_helpdesk_invisible')

    @api.depends('make_helpdesk_invisible')
    def _make_helpdesk_invisible(self):
        for order in self:
            if self.env.user.has_group('beauty_pos.group_help_desk'):
                order.make_helpdesk_invisible = False
            else:
                order.make_helpdesk_invisible = True

    @api.multi
    def name_get(self):
        result = super(ProductTemplate, self).name_get()
        res = []
        for record in self:
            if record.name:
                product_name = record.name
                if len(record.name) > 100:
                    product_name = product_name[0:100]
                res.append((record['id'], "%s" % (product_name)))
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'
    is_return = fields.Boolean('Is Return move')


class PosOrder(models.Model):
    _inherit = "pos.order"

    partner_id = fields.Many2one('res.partner', string='Customer', change_default=True, index=True,
                                 states={'draft': [('readonly', False)], 'paid': [('readonly', False)]}, required=True)
    cashier_name = fields.Many2one('res.users', string='Cashier')

    @api.multi
    def action_set_to_paid(self):
        if self.state != 'draft':
            raise UserError('Only Draft appointments can set to Paid')
        self.write({'state': 'paid'})
        self.cashier_name = self.env.user.id
        self.action_pos_order_paid()

    def _prepare_bank_statement_line_payment_values(self, data):
        args_pos_pay = super(PosOrder, self)._prepare_bank_statement_line_payment_values(data)
        if data.get('is_advance'):
            args_pos_pay['is_advance'] = data['is_advance']
        return args_pos_pay

    @api.model
    def _order_fields(self, ui_order):
        order_pos = super(PosOrder, self)._order_fields(ui_order)
        order_pos['cashier_name'] = ui_order['user_id'] or False,
        return order_pos

    def _default_pricelist(self):
        if self._default_session().config_id.pricelist_id:
            return self._default_session().config_id.pricelist_id
        else:
            return self.env['product.pricelist'].search([], limit=1)

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, states={
        'draft': [('readonly', False)]}, readonly=True, default=_default_pricelist)
    phone = fields.Char('Phone')
    show_name = fields.Char('Display Name', compute='_compute_display_name')
    date_order = fields.Datetime(string='Order Date', readonly=False, index=True, default=fields.Datetime.now)
    # date_start = fields.Datetime(string='Start Time')
    ref_date_start = fields.Datetime(string='Ref Start Time')
    # date_stop = fields.Datetime(string='End Time')
    staff_ids = fields.Many2many('hr.employee', 'order_staff_rel', string='Related Staff', compute='_compute_staff_ids')
    state = fields.Selection(
        [('draft', 'Appointment'),
         ('cancel', 'Cancelled'),
         ('paid', 'Paid'),
         ('done', 'Posted'),
         ('invoiced', 'Invoiced')],
        'Status', readonly=True, copy=False, default='draft')
    appointment = fields.Boolean('Appointment', readonly=True)
    is_reversed = fields.Boolean('Reversed Order', readonly=True)
    negative_entry = fields.Boolean('Negative Entry', readonly=True)
    reverse_id = fields.Many2one('pos.order', 'Reverse Entry', copy=False)
    checkin = fields.Boolean('Customer Present?', readonly=True)
    helpdesk_flag = fields.Boolean('Helpdesk User ?', compute='_compute_helpdesk_flag')
    make_helpdesk_invisible = fields.Boolean(string="User", compute='_make_helpdesk_invisible')
    total_paid = fields.Float(compute='_compute_amount_paid', string='Total Paid', digits=0)
    total_balance = fields.Float(compute='_compute_amount_balance', string='Total Balance', digits=0)
    total_advance = fields.Float(compute='_compute_amount_advance', string='Total Advance', digits=0)
    amount_due = fields.Float('Amount Due', compute='_compute_due')

    @api.model
    @api.depends('partner_id', 'state', 'checkin')
    def _compute_due(self):
        for order in self:
            due = 0
            if order.partner_id:
                order_ids = self.env['pos.order'].search([('partner_id', '=', order.partner_id.id),
                                                          ('state', 'in', ['draft', 'paid', 'invoiced', 'done'])])
                for ord in order_ids:
                    if ord.state == 'draft':
                        if ord.checkin or ord.total_paid > 0:
                            due += ord.total_balance
                    else:
                        due += ord.total_balance
                order.amount_due = due
            else:
                order.amount_due = due

    def show_due(self):
        orders = []
        order_ids = self.env['pos.order'].search([('partner_id', '=', self.partner_id.id),
                                                  ('state', 'in', ['draft', 'paid', 'invoiced', 'done'])])
        for ord in order_ids:
            if ord.state == 'draft':
                if ord.checkin or ord.total_paid > 0:
                    orders.append(ord.id)
            else:
                orders.append(ord.id)
        action = self.env.ref('point_of_sale.action_pos_pos_form').read()[0]
        if orders:
            action['domain'] = [('id', 'in', orders)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.depends('statement_ids', 'statement_ids.is_advance')
    def _compute_amount_advance(self):
        for order in self:
            amt_total_advance = 0.0
            for ord_line in order.statement_ids:
                if ord_line.is_advance:
                    amt_total_advance += ord_line.amount
            order.total_advance = amt_total_advance

    @api.depends('statement_ids')
    def _compute_amount_paid(self):
        for order in self:
            order.total_paid = sum(payment.amount for payment in order.statement_ids)

    @api.depends('statement_ids')
    def _compute_amount_balance(self):
        for order in self:
            order.total_balance = order.amount_total - order.total_paid

    @api.depends('make_helpdesk_invisible')
    def _make_helpdesk_invisible(self):
        for order in self:
            if self.env.user.has_group('beauty_pos.group_help_desk'):
                order.make_helpdesk_invisible = False
            else:
                order.make_helpdesk_invisible = True

    @api.depends('helpdesk_flag')
    def _compute_helpdesk_flag(self):
        for order in self:
            admin_grp_condition = order.state in ['done', 'paid', 'invoiced'] and \
                                  not self.env.user.has_group('beauty_pos.group_user_saloon_admin')
            helpdesk_grp_condition = order.checkin and self.env.user.has_group('beauty_pos.group_help_desk') \
                                     and not self.env.user.has_group('beauty_pos.group_scheduler_manager')
            if helpdesk_grp_condition or admin_grp_condition:
                order.helpdesk_flag = True
            else:
                order.helpdesk_flag = False

    @api.multi
    def reverse(self):
        """Create a copy of order  for refund order"""
        PosOrder = self.env['pos.order']
        current_session = self.env['pos.session'].search([('state', '!=', 'closed'), ('user_id', '=', self.env.uid)],
                                                         limit=1)
        if not current_session:
            raise UserError(
                _('To return product(s), you need to open a session that will be used to register the refund.'))
        for order in self:
            clone = order.copy({
                # ot used, name forced by create
                'name': 'Rev: ' + order.name,
                'session_id': current_session.id,
                'date_order': order.date_order,
                'pos_reference': order.pos_reference,
            })
            order.reverse_id = clone.id
            PosOrder += clone
        for clone in PosOrder:
            for order_line in clone.lines:
                order_line.write({'qty': -order_line.qty})
            for order in self:
                for pay in order.statement_ids:
                    clone.add_payment({
                        'amount': -1 * pay.amount,
                        'payment_date': pay.date,
                        'payment_name': _('return'),
                        'journal': pay.journal_id.id,
                    })
                order.write({'is_reversed': True})
                if order.picking_id:
                    self.pos_delivery_cancel(order.picking_id)
                    order.write({'picking_id': False})
            clone.write({'state': 'paid', 'is_reversed': True, 'negative_entry': True})
        # return {
        #     'name': _('Return Products'),
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'pos.order',
        #     'res_id': PosOrder.ids[0],
        #     'view_id': False,
        #     'context': self.env.context,
        #     'type': 'ir.actions.act_window',
        #     'target': 'current',
        # }

    @api.multi
    def unlink(self):
        for order in self:
            if not self.env.user.has_group('beauty_pos.group_user_saloon_supervisor'):
                raise UserError(_('Only Supervisor can delete Appointments.'))
            if order.state == 'draft' and order.statement_ids:
                raise UserError(_('You can not delete the record with Payment lines.'))
        return super(PosOrder, self).unlink()

    @api.multi
    def generate_pos_reference(self, session_id):
        def _zero_padding(num, size):
            s = "" + str(num)
            while (len(s) < size):
                s = "0" + s
            return s

        return _zero_padding(session_id.id, 5) + '-' + _zero_padding(session_id.login_number, 3) + '-' + \
               _zero_padding(session_id.sequence_number, 4);

    @api.model
    def create(self, vals):
        name_defined = ''
        if vals.get('name'):
            name_defined = vals.get('name')
        decrem_sequence = False
        if "Rev: " in name_defined:
            decrem_sequence = True
        if not vals.get('pos_reference'):
            session = vals.get('session_id')
            session = self.env['pos.session'].search([('id', '=', session)])
            vals['sequence_number'] = session.sequence_number + 1
            if self._context.get('default_appointment') == 1:
                vals['pos_reference'] = self.env['ir.sequence'].next_by_code('appontment.salon')
            else:
                reference = self.generate_pos_reference(session)
                reference = "A - Order " + reference
                vals['pos_reference'] = reference
                seq = session.sequence_number + 1
                session.write({'sequence_number': seq})
        if vals.get('date_start'):
            date_start = vals.get('date_start')
        else:
            vals['date_start'] = datetime.now()
            date_start = datetime.now()
            date_start = date_start.replace(second=0, microsecond=0)
        if not vals.get('date_stop'):
            date_start = datetime.strptime(str(date_start), '%Y-%m-%d %H:%M:%S')
            vals['date_stop'] = date_start + timedelta(minutes=15)
        res = super(PosOrder, self).create(vals)
        if decrem_sequence:
            if res.session_id:
                # set name based on the sequence specified on the config
                session = res.session_id
                number_next_actual = session.config_id.sequence_id.number_next_actual
                session.config_id.sequence_id.write({'number_next_actual': number_next_actual - 1})
                res.write({'name': name_defined})
            else:
                # fallback on any pos.order sequence
                sequence_id = self.env['ir.sequence'].search([('code', '=', 'pos.order')])
                if sequence_id:
                    sequence = self.env['ir.sequence'].browse(sequence_id[0])
                    number_next_actual = sequence.number_next_actual
                    sequence.write({'number_next_actual': number_next_actual - 1})
                    res.write({'name': name_defined})
        return res

    @api.depends('lines')
    def _compute_display_name(self):
        for order in self:
            name_string = ""
            if order.name:
                name_string = name_string + "Order:" + order.name
            if order.lines:
                for line in order.lines:
                    if line.product_id:
                        name_string = name_string + ", "
                        name_string = name_string + line.product_id.name
                    if line.staff_assigned_id:
                        name_string = name_string + "--" + line.staff_assigned_id.name
            order.show_name = name_string

    @api.depends('lines')
    def _compute_staff_ids(self):
        for order in self:
            staff_ids = []
            for line in order.lines:
                if line.staff_assigned_id:
                    staff_ids.append(line.staff_assigned_id.id)
            order.staff_ids = staff_ids

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for order in self:
            if order.partner_id and order.partner_id.phone:
                order.phone = order.partner_id.phone

    @api.onchange('phone')
    def onchange_phone(self):
        for order in self:
            if order.partner_id and order.phone:
                order.partner_id.write({'phone': order.phone})
            if order.phone:
                if order.partner_id:
                    phone_cust = self.env['res.partner'].search([('phone', '=', order.phone),
                                                                 ('id', '!=', order.partner_id.id)])
                else:
                    phone_cust = self.env['res.partner'].search([('phone', '=', order.phone)])
                if phone_cust:
                    cust_name = ""
                    for i in phone_cust:
                        if cust_name != "":
                            cust_name = cust_name + ", "
                        cust_name = cust_name + i.name
                    raise UserError(_('Existing customer(%s) with same phone number') % cust_name)

    @api.multi
    def _appointment_reminder(self):
        from_time = datetime.now() + timedelta(minutes=30)
        to_time = from_time + timedelta(minutes=1)
        appointments = self.search(
            [('checkin', '=', False), ('date_start', '>=', from_time.strftime('%Y-%m-%d %H:%M:%S')),
             ('date_start', '<', to_time.strftime('%Y-%m-%d %H:%M:%S'))])
        for appointment in appointments:
            start_time = ""
            if appointment.date_start:
                user = self.env['res.users'].browse(SUPERUSER_ID)
                tz = pytz.timezone(user.partner_id.tz) or pytz.utc
                start_time = pytz.utc.localize(
                    datetime.strptime(appointment.date_start, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
                start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
            if appointment.partner_id:
                message = appointment.partner_id.name + " have appointment " + appointment.name + " at " + start_time + " ."
            else:
                message = "The appointment " + appointment.name + " is booked at " + start_time + " ."
            self.env.user.notify_info(message, title='Appointment Reminder', sticky=True)
            # self.env.user.notify_warning(message,title='appointment Reminder',sticky=True)

    @api.onchange('lines')
    def check_staff_availability(self):
        pos_obj = self.env['pos.order.line']
        for order in self:
            pass
            # for line in order.lines:
            #     if line.staff_assigned_id and line.procedure_start and line.procedure_stop:
            #         line_procedure_stop = datetime.strptime(line.procedure_stop, '%Y-%m-%d %H:%M:%S')
            #         line_procedure_stop = line_procedure_stop - timedelta(minutes=6)
            #         line_procedure_stop = line_procedure_stop.strftime('%Y-%m-%d %H:%M:%S')
            #         line_procedure_start = datetime.strptime(line.procedure_start, '%Y-%m-%d %H:%M:%S')
            #         line_procedure_start = line_procedure_start + timedelta(minutes=6)
            #         line_procedure_start = line_procedure_start.strftime('%Y-%m-%d %H:%M:%S')
            #         pos_search = pos_obj.search([('staff_assigned_id', '=', line.staff_assigned_id.id)])
            #         warn = 0
            #         for record in pos_search:
            #             if record.procedure_start <= line_procedure_start <= record.procedure_stop:
            #                 warn = 1
            #             elif record.procedure_start <= line_procedure_stop <= record.procedure_stop:
            #                 warn = 1
            #             elif line_procedure_start <= record.procedure_start and record.procedure_stop <= line_procedure_stop:
            #                 warn = 1
            #             if warn == 1:
            #                 user = self.env['res.users'].browse(SUPERUSER_ID)
            #                 tz = pytz.timezone(user.partner_id.tz) or pytz.utc
            #                 todayy = pytz.utc.localize(datetime.strptime(record.procedure_start, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
            #                 start_today = todayy.replace(hour=0, minute=0, second=0)
            #                 end_today = start_today + timedelta(days=1)
            #                 start_today = start_today.strftime('%Y-%m-%d %H:%M:%S')
            #                 end_today = end_today.strftime('%Y-%m-%d %H:%M:%S')
            #                 ids_today = []
            #                 for rec in pos_search:
            #                     if rec.procedure_start and rec.procedure_stop:
            #                         procedure_start = pytz.utc.localize(datetime.strptime(rec.procedure_start, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
            #                         procedure_start = procedure_start.strftime('%Y-%m-%d %H:%M:%S')
            #                         if procedure_start >= start_today and procedure_start <= end_today:
            #                             if rec not in ids_today:
            #                                 ids_today.append(rec)
            #                         if rec.procedure_stop <= end_today and rec.procedure_stop >= start_today:
            #                             if rec not in ids_today:
            #                                 ids_today.append(rec)

            # msg = line.staff_assigned_id.name + ' is not available at the selected time. He/she will be unavailable at following timings, '
            # for rec_id in ids_today:
            #     start = pytz.utc.localize(datetime.strptime(rec_id.procedure_start, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
            #     stop = pytz.utc.localize(datetime.strptime(rec_id.procedure_stop, '%Y-%m-%d %H:%M:%S')).astimezone(tz)
            #     start = start.replace(tzinfo=None)
            #     stop = stop.replace(tzinfo=None)
            #     msg = msg + "\n \t" + str(start) + " To " + str(stop)

            # line.staff_assigned_id = False
            # warning = {
            #     'title': ' Warning !!!',
            #     'message': msg
            # }
            # return {'warning': warning}

    @api.model
    @api.onchange('date_start')
    def onchange_start_time(self):
        if self.date_start:
            self.ref_date_start = self.date_start
            self.date_order = self.date_start

    @api.onchange('lines', 'date_start', 'date_stop')
    def onchange_procedure_lines(self):
        for order in self:
            stop_times = []
            start_times = []
            for line in order.lines:
                if line.procedure_stop:
                    stop_times.append(line.procedure_stop)
                if line.procedure_start:
                    start_times.append(line.procedure_start)
            if stop_times:
                max_stop_time = max(stop_times)
                order.ref_date_start = max_stop_time
                if max_stop_time > order.date_stop:
                    order.date_stop = max_stop_time
            if start_times:
                min_start_time = min(start_times)
                if min_start_time < order.date_start:
                    order.date_start = min_start_time

    @api.multi
    def action_check_in(self):
        for order in self:
            order.write({'checkin': True})

    @api.multi
    def action_cancel_appt(self):
        for order in self:
            if order.state != 'draft':
                raise UserError('Only Draft Orders can Cancelled')
            if order.statement_ids:
                raise UserError('You Cannot cancel orders that is already paid')
            order.write({'state': 'cancel'})

    @api.multi
    def print_bill(self):
        return self.env['report'].get_action(self.id, 'beauty_pos.report_pos_receipt')


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    make_helpdesk_invisible = fields.Boolean(string="User", compute='_make_helpdesk_invisible')

    @api.depends('make_helpdesk_invisible')
    def _make_helpdesk_invisible(self):
        for order in self:
            if self.env.user.has_group('beauty_pos.group_help_desk'):
                order.make_helpdesk_invisible = False
            else:
                order.make_helpdesk_invisible = True

    def show_order_form(self):
        return {
            'name': _('Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': self.order_id.id,
            'view_id': False,
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    partner_id = fields.Many2one('res.partner', 'Customer', related='order_id.partner_id', store=True)
    state = fields.Selection(
        [('draft', 'Appointment'),
         ('cancel', 'Cancelled'),
         ('paid', 'Paid'),
         ('done', 'Posted'),
         ('invoiced', 'Invoiced')],
        'Status', readonly=True, copy=False, default='draft', related='order_id.state')
    checkin = fields.Boolean('Customer Present?', readonly=True, compute='_compute_checkin')

    @api.multi
    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise UserError(
                    _("You cannot delete the records not in draft state."))
        res = super(PosOrderLine, self).unlink()
        return res

    @api.depends('order_id', 'order_id.checkin')
    def _compute_checkin(self):
        for order in self:
            if order.order_id:
                order.checkin = order.order_id.checkin
            else:
                order.checkin = False

    @api.onchange('product_id', 'procedure_start')
    def onchange_procedure(self):
        if self.state != 'draft':
            raise UserError(
                _("New Procedure lines are allowed only in Appointment Status."))
        # if self.procedure_start and not self.procedure_stop and self.product_id and self.product_id.type == 'service':
        if self.procedure_start and self.product_id:
            start_time = datetime.strptime(self.procedure_start, '%Y-%m-%d %H:%M:%S')
            # self.procedure_stop = start_time + timedelta(minutes=30)
            duration = 0
            product = self.product_id
            if product.type == 'service':
                if product.duration_in_min:
                    duration = product.duration_in_min
                else:
                    duration = 30
            self.procedure_stop = start_time + timedelta(minutes=duration)

        if self.procedure_start and self.procedure_stop and self.procedure_start > self.procedure_stop:
            self.procedure_stop = False
            warning = {
                'title': ' Warning !!!',
                'message': 'End Time must be after Time Start. Reset procedure time properly.'
            }
            return {'warning': warning}
