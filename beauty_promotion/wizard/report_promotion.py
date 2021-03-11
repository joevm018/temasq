# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class PromotionDetails(models.TransientModel):
    _name = 'promotion.report.wizard'
    _description = 'Promotion Summary Report'

    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string="Customer")
    service_id = fields.Many2one('product.product', string="Services", domain=[('type', '=', 'service')])


    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        data = {'start_date':self.start_date, 'end_date':self.end_date, 'partner_id': self.partner_id.id, 'service_id': self.service_id.id}
        return self.env['report'].get_action([], 'beauty_promotion.report_promotion', data=data)


class ReportSaleDetails(models.AbstractModel):
    _name = 'report.beauty_promotion.report_promotion'

    @api.model
    def get_promotion_details(self, start_date=False, end_date=False, partner_id=False, service_id=False):
        date_start_obj = datetime.strptime(start_date, '%Y-%m-%d')
        date_end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        ord_date_start = date_start_obj.strftime("%Y-%m-%d 00:00:00")
        ord_date_stop = date_end_obj.strftime("%Y-%m-%d 23:59:59")
        ord_date_start = datetime.strptime(ord_date_start, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
        ord_date_stop = datetime.strptime(ord_date_stop, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
        dom = [('order_id.date_order', '>=', str(ord_date_start)), ('order_id.date_order', '<=', str(ord_date_stop)),
                      ('state', 'in', ['paid', 'invoiced', 'done']),
                      ('is_order_line_promotion', '=', True),
                      ('promotion_line_id', '!=', False)]
        if partner_id:
            dom.append(('partner_id', '=', partner_id))
        if service_id:
            dom.append(('product_id', '=', service_id))
        pos_order_line = self.env['pos.order.line'].search(dom)
        info_ord_line = []
        for ord_line in pos_order_line:
            info_ord_line.append(ord_line)
        partner_name = ""
        if partner_id:
            partner_name = self.env['res.partner'].browse(partner_id).name
        service_name = ""
        if service_id:
            service_name = self.env['product.product'].browse(service_id).name
        return {
            'partner_name': partner_name,
            'date_from': start_date,
            'date_to': end_date,
            'service_name': service_name,
            'info_ord_line': info_ord_line,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_promotion_details(data['start_date'], data['end_date'],data['partner_id'], data['service_id']))
        return self.env['report'].render('beauty_promotion.report_promotion', data)
