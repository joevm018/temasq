# -*- coding: utf-8 -*-
import logging
from odoo import fields, api, models
_logger = logging.getLogger(__name__)


class NewPosLines(models.Model):
    _inherit = "pos.order.line"

    referral_staff_id = fields.Many2one('hr.employee', 'Referred By')
