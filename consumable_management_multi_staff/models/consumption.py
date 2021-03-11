# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools, _


class ConsumptionRecord(models.Model):
    _inherit = "consumption.record"
    _description = "Consumption Record"

    staff_ids = fields.Many2many('hr.employee', string='Employee', readonly=True)
