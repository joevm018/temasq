# -*- coding: utf-8 -*-
import logging
from odoo import fields, api, models


class NewPosLines(models.Model):
    _inherit = "pos.order.line"

    sold_staff_id = fields.Many2one('hr.employee', 'Sold By')
    staff_assigned_id = fields.Many2one('hr.employee', string='Served By', domain=[('is_beautician', '=', True)])
