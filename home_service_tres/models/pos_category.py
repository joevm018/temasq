# -*- coding: utf-8 -*-
import logging
from odoo import fields, api, models
_logger = logging.getLogger(__name__)


class PosCategory(models.Model):
    _inherit = "pos.category"

    is_home_service = fields.Boolean('Home Service')
