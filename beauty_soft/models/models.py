# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

    
class ResCompany(models.Model):
    _inherit = "res.company"

    wifi_pswd = fields.Char("Wifi Password")


class beauty_soft(models.Model):
    _inherit = "res.partner"
    _name = "res.partner"

    notes = fields.Text()
    file_no = fields.Char()
    arabic_name = fields.Char()
    identity_no = fields.Char()
    dob = fields.Date(index=True, String='Date Of Birth')
    sex = fields.Selection(string='Sex', selection=[('m', 'Male'), ('f', 'Female')])
    sale_warn = fields.Selection(WARNING_MESSAGE, 'Sales Order', default='no-message', help=WARNING_HELP)
    purchase_warn = fields.Selection(WARNING_MESSAGE, 'Purchase Order', help=WARNING_HELP, default="no-message")

    # @api.model
    # def create(self, vals):
    #    print ("vvvvvv", vals)
    #    rec = super(beauty_soft, self).create(vals)
    #    rec.file_no = self.env['ir.sequence'].next_by_code('FILENO')
    #    return rec


class staff_master(models.Model):
    _inherit = "hr.employee"

    work_time = fields.Char('Work Location')
    employee_no = fields.Char('Employee ID')
    is_beautician = fields.Boolean('Show in Scheduler')
    service_ids = fields.Many2many('product.template', 'service_staff_relation', 'staff_id', 'service_id',
                                   string='Services', domain=[('type', '=', 'service')])

# class SaleOrder(models.Model):
#     _inherit = "sale.order"
#     _name = "sale.order"
#     file_no = fields.Char()
#     journal_id = fields.Many2one('account.journal', domain=[('type', '=', 'cash')], string='Cash Journal',
#         help="The accounting journal corresponding to this bank account.")
#     cash_amount = fields.Float('Cash Amount', required=True, default=0.0)
#     bank_amount = fields.Float('Bank Amount', required=True,  default=0.0)
#
#     bank_journal_id = fields.Many2one('account.journal', domain=[('type', '=', 'bank')], string='Bank Journal',
#         help="The accounting journal corresponding to this bank account.")
#
#     @api.onchange('partner_id')
#     def set_file_number(self):
#         if self.partner_id:
#             self.file_no = self.partner_id.file_no
#         pass
#
#     @api.onchange('file_no')
#     def set_partner(self):
#         if self.file_no:
#             self.partner_id = self.env['res.partner'].search([('file_no','=', self.file_no )])
#         pass
#     pass
#
#
#     def get_payment_vals(self):
#         """ Hook for extension """
#         return {
#             'journal_id': self.journal_id.id,
#             'payment_method_id': self.payment_method_id.id,
#             'payment_date': self.payment_date,
#             'communication': self.communication,
#             'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices()],
#             'payment_type': self.payment_type,
#             'amount': self.amount,
#             'currency_id': self.currency_id.id,
#             'partner_id': self.partner_id.id,
#             'partner_type': self.partner_type,
#         }
#     @api.model
#     def action_confirm(self):
#         rec = super(SaleOrder, self).action_confirm()
#         active_order_ids = [order.id for order in self]
#         vals = {'advance_payment_method':'all'}
#         new_wizard = self.env["sale.advance.payment.inv"].with_context(active_ids=active_order_ids).create(vals)
#         invoice_obj = new_wizard.create_invoices()
#         invoice_ids = self.env['sale.order'].browse(active_order_ids).invoice_ids
#         invoice_ids.action_invoice_open()
# #        self.env['account.payment'].create(self.get_payment_vals())
# #        import pdb;pdb                .set_trace()
#         active_id = invoice_ids.id
#         ctx = {'default_invoice_ids': [(4, active_id, None)]}
# #        for order_ids in active_order_ids:
# #            order_ids.invoice_ids.action_invoice_open()
# #            pass
# #        invoice_obj.validate()
#         ir_model_data = self.env['ir.model.data']
#         try:
#             compose_form_id = ir_model_data.get_object_reference('account', 'view_account_payment_invoice_form')[1]
#         except ValueError:
#             compose_form_id = False
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'account.payment',
#             'views': [(compose_form_id, 'form')],
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }
#         return rec
#         pass
#     pass
#
#
# class sale_order_line(models.Model):
#     _inherit = "sale.order.line"
#     _name = "sale.order.line"
#     staff_id = fields.Many2one("hr.employee", string='Staff')
#     pass

    


    