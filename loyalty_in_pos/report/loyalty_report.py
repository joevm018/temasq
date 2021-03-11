# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


# from odoo.report.report_xlsx import ReportXlsx


class LoyaltyReport(models.TransientModel):
    _name = 'loyalty.report'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    partner_id = fields.Many2one('res.partner', string="Customer")

    def generate_report(self):
        data = {'start_date': self.start_date, 'end_date': self.end_date}
        if self.partner_id:
            data['partner_id'] = [self.partner_id.id, self.partner_id.name]
        else:
            data['partner_id'] = False
        return self.env['report'].get_action(self, report_name='loyalty_in_pos.report_loyalty_pdf', data=data)


class ReportLoyalty(models.AbstractModel):
    _name = 'report.loyalty_in_pos.report_loyalty_pdf'

    @api.model
    def get_pos_details(self, start_date=False, end_date=False, partner_id=False):
        lst_search = [('state', 'in', ['paid', 'invoiced', 'done']), ('partner_id', '!=', False)]
        if start_date:
            lst_search.append(('date_order', '>=', start_date))
        if end_date:
            lst_search.append(('date_order', '<=', end_date))
        records = {}
        if partner_id:
            part = self.env['res.partner'].browse(partner_id[0])
            records[part] = []
            lst_search.append(('partner_id', '=', partner_id[0]))
        orders = self.env['pos.order'].search(lst_search)

        for o in orders:
            if o.partner_id not in records.keys():
                records[o.partner_id] = [o]
            else:
                records[o.partner_id].append(o)
        return {
            'records': records,
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(
            self.get_pos_details(data['start_date'], data['end_date'], data['partner_id']))
        return self.env['report'].render('loyalty_in_pos.report_loyalty_pdf', data)
