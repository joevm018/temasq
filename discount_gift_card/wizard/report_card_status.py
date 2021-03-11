# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class CardDetails(models.TransientModel):
    _name = 'card.status.wizard'
    _description = 'Card Details Report'

    card_type = fields.Selection([('type_discount_gift_card', 'Discount Gift Card'), ('type_package_card', 'Package Card'),
                             ('type_student_card', 'Student Card')], string='Type')
    status = fields.Selection([('new', 'New'), ('active', 'Active'), ('finished', 'Finished'), ('cancel', 'Cancelled')]
                              , string='Status')

    @api.multi
    def generate_report(self):
        data = {'card_type': self.card_type, 'status': self.status}
        return self.env['report'].get_action([], 'discount_gift_card.report_card_status', data=data)


class ReportSaleDetails(models.AbstractModel):
    _name = 'report.discount_gift_card.report_card_status'

    @api.model
    def get_card_details(self, card_type=False, status=False):
        dom = [('type', '!=', False)]
        if card_type:
            dom.append(('type', '=', card_type))
        status_name = ""
        if status:
            if status == 'new':
                dom.append(('state', '=', 'new'))
                status_name = "New"
            if status == 'cancel':
                dom.append(('state', '=', 'cancel'))
                status_name = "Cancelled"
            if status == 'active':
                status_name = "Active"
                dom.append(('state', '=', 'active'))
                dom.append(('is_zeroo_card', '=', False))
            if status == 'finished':
                status_name = "Finished"
                dom.append(('state', '=', 'active'))
                dom.append(('is_zeroo_card', '=', True))
        pos_card = self.env['pos.customer.card'].search(dom)
        info_card = {'content': []}
        for ord in pos_card:
            info_card['content'].append(ord)
        return {
            'card_type': card_type,
            'status': status_name,
            'info_card': info_card,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_card_details(data['card_type'], data['status']))
        return self.env['report'].render('discount_gift_card.report_card_status', data)
