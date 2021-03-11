# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class DocumentType(models.Model):
    _name = 'document.type'

    name = fields.Char('Description', required=True)
    remind_x_day_before = fields.Integer('Expiry alert Before (In days)')


class EmployeeDocument(models.Model):
    _name = 'employee.document'

    name = fields.Char('ID', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    document_type = fields.Many2one('document.type', string='Description', required=True)
    docs = fields.Binary(string='File', required=False)
    file_name = fields.Char(string='Document Name')
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expires On')
    remind_x_day_before = fields.Integer('Expiry alert Before (In days)')

    @api.onchange('document_type')
    def onchange_document_type(self):
        self.remind_x_day_before = self.document_type.remind_x_day_before



