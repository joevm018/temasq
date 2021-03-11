# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, timedelta


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_session_user_image = fields.Binary(
        string="User Image", compute='_compute_current_user_image')
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        required=True,
        index=True,
        readonly=True,
        states={'opening_control': [('readonly', False)]},
        default=lambda self: self.env.uid)
    today_amount = fields.Float(
        string="Total", compute='_compute_amount')
    cash_amount = fields.Float(
        string="Cash", compute='_compute_amount')
    bank_amount = fields.Float(
        string="Bank", compute='_compute_amount')
    retail_amount = fields.Float(
        string="Retail Income", compute='_compute_amount')
    service_amount = fields.Float(
        string="Service Income", compute='_compute_amount')
    clients = fields.Integer(
        string="Service Income", compute='_compute_client')
    emp_of_month = fields.Many2one(
        'hr.employee', string='Employee of the month',
        compute='_compute_emp_of_month')
    emp_name_of_month = fields.Char(
        related='emp_of_month.name', string='Employee of the month')

    @api.multi
    def _compute_emp_of_month(self):
        now = datetime.today()
        last = date(
            now.year, now.month, 1) - timedelta(1)
        first = last.replace(day=1)
        first_day = fields.Date.to_string(first)
        last_day = fields.Date.to_string(last)
        for pos_config in self:
            orders = self.env['pos.order'].search_read([
                ('date_order', '>=', first_day),
                ('date_order', '<=', last_day)
            ], ['lines', 'date_order'])
            employees_last_month = {}
            order_lines = []
            for order in orders:
                order_lines += order.get('lines')
            pos_order_lines = self.env['pos.order.line'].browse(order_lines)
            employees = []
            emp_id = False
            emp_value = 0
            for pos_line in pos_order_lines:
                if pos_line.staff_assigned_id:
                    if pos_line.staff_assigned_id.id not in employees:
                        employees_last_month.update({
                            pos_line.staff_assigned_id.id: 0
                        })
                    for key, val in employees_last_month.items():
                        employees.append(key)
                        if key == pos_line.staff_assigned_id.id:
                            new_val = val + pos_line.price_subtotal_incl
                            employees_last_month.update({key: new_val})
                            if emp_value < new_val:
                                emp_value = new_val
                                emp_id = key
            pos_config.emp_of_month = self.env['hr.employee'].browse(emp_id)

    @api.depends('session_ids')
    def _compute_client(self):
        for pos_config in self:
            pos_config.clients = self.env['res.partner'].search_count([
                ('customer', '=', True)])

    @api.depends('session_ids')
    def _compute_current_user_image(self):
        for pos_config in self:
            session = pos_config.session_ids.filtered(
                lambda s: s.state == 'opened' and '(RESCUE FOR' not in s.name)
            pos_config.pos_session_user_image = session and session[0].user_id.image_medium or False

    @api.depends('session_ids')
    def _compute_amount(self):
        for pos_config in self:
            total_amount = False
            total_cash_amount = False
            total_bank_amount = False
            total_service_amount = False
            total_retail_amount = False
            for session in pos_config.session_ids:
                for order in session.order_ids.filtered(
                    lambda s: datetime.strptime(
                        s.date_order, '%Y-%m-%d %H:%M:%S'
                    ).date() == date.today()
                ):
                    total_amount += order.amount_total
                    total_cash_amount += sum([
                        stmnt.amount for stmnt in order.statement_ids.filtered(
                            lambda o: o.journal_id.type == 'cash')])
                    total_bank_amount += sum([
                        stmnt.amount for stmnt in order.statement_ids.filtered(
                            lambda o: o.journal_id.type == 'bank')])
                    total_service_amount += sum([
                        li.price_subtotal_incl for li in order.lines.filtered(
                            lambda o: o.product_id.type == 'service')])
                    total_retail_amount += sum([
                        li.price_subtotal_incl for li in order.lines.filtered(
                            lambda o: o.product_id.type == 'product')])
                    # for stmnt in order.statement_ids:
                    #     if stmnt.journal_id.type == 'cash':
                    #         total_cash_amount += stmnt.amount
                    #     elif stmnt.journal_id.type == 'bank':
                    #         total_bank_amount += stmnt.amount
            pos_config.today_amount = total_amount
            pos_config.cash_amount = total_cash_amount
            pos_config.bank_amount = total_bank_amount
            pos_config.retail_amount = total_retail_amount
            pos_config.service_amount = total_service_amount
            self.env['pos.top.service']._compute_service_product()
