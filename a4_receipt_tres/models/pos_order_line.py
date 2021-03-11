# -*- coding: utf-8 -*-
import logging
from odoo import fields, api, models
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    no_response = fields.Boolean('No Response')


class NewPosLines(models.Model):
    _inherit = "pos.order.line"

    executed_staff_id = fields.Many2one('hr.employee', 'Executed By')
