# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError


class CalendarConfig(models.Model):
    _inherit = 'calender.config'

    @api.model
    def fetch_calendar_extras(self):
        res = super(CalendarConfig, self).fetch_calendar_extras()
        cr = self._cr
        cr.execute("SELECT pt.name, pp.id,pt.id as product_template_id "
                   "FROM product_product pp "
                   "JOIN product_template pt "
                   "ON (pp.product_tmpl_id = pt.id) where pp.active and pt.type='service' ORDER BY pt.name")
        services = cr.dictfetchall()
        new_services = []
        for serv in services:
            serv['staff_ids'] = self.env['product.template'].browse(serv['product_template_id']).staff_ids.ids
            if not self.env['product.template'].browse(serv['product_template_id']).combo_pack:
                new_services.append(serv)
        res[1] = new_services
        return res
