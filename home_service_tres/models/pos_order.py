# -*- coding: utf-8 -*-
import logging
from odoo import fields, api, models
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    have_home_service = fields.Boolean('Home Service', compute='_get_home_service', store=True)

    @api.model
    @api.depends('lines', 'partner_id')
    def _get_home_service(self):
        for i in self:
            home_serv = False
            for j in i.lines:
                if j.product_id.pos_categ_id:
                    if j.product_id.pos_categ_id.is_home_service:
                        home_serv = True
            i.have_home_service = home_serv
            if i.partner_id and not i.partner_id.is_home_service:
                i.partner_id.is_home_service = home_serv
