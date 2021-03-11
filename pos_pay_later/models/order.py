# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _compute_credit_cash_amt(self):
        for order in self:
            cash_amt = 0.0
            credit_amt = 0.0
            pay_later_amt = 0.0
            invoice_due_amt = 0.0
            for statement in order.statement_ids:
                if statement.journal_id.type == 'cash':
                    cash_amt += statement.amount
                if statement.journal_id.type == 'bank':
                    if statement.journal_id.is_pay_later:
                        pay_later_amt += statement.amount
                    else:
                        credit_amt += statement.amount
            if order.state == 'invoiced' and order.invoice_id:
                invoice_due_amt = order.invoice_id.residual
            order.credit_amt = credit_amt
            order.cash_amt = cash_amt
            order.pay_later_amt = pay_later_amt
            order.invoice_due_amt = invoice_due_amt

    pay_later_amt = fields.Float('Credit Amount', digits=dp.get_precision('Product Price'), compute='_compute_credit_cash_amt')
    invoice_due_amt = fields.Float('Due Amount', digits=dp.get_precision('Product Price'), compute='_compute_credit_cash_amt')

    @api.multi
    def action_pos_order_validated_invoice(self):
        # same code of action_pos_order_invoice fucntion.
        Invoice = self.env['account.invoice']

        for order in self:
            # Force company for all SUPERUSER_ID action
            local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
            if order.invoice_id:
                Invoice += order.invoice_id
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            invoice = Invoice.new(order._prepare_invoice())
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = order.fiscal_position_id

            inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
            new_invoice = Invoice.with_context(local_context).sudo().create(inv)
            message = _(
                "This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                      order.id, order.name)
            new_invoice.message_post(body=message)
            order.write({'invoice_id': new_invoice.id, 'state': 'invoiced'})
            Invoice += new_invoice

            for line in order.lines:
                self.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

            new_invoice.with_context(local_context).sudo().compute_taxes()
            order.sudo().write({'state': 'invoiced'})
            # this workflow signal didn't exist on account.invoice -> should it have been 'invoice_open' ? (and now method .action_invoice_open())
            # shouldn't the created invoice be marked as paid, seing the customer paid in the POS?
            # new_invoice.sudo().signal_workflow('validate')

            # Extra code added................start
            if order.invoice_id:
                order.invoice_id.sudo().action_invoice_open()
                order.account_move = order.invoice_id.move_id
            # Extra code added................ end
        if not Invoice:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': Invoice and Invoice.ids[0] or False,
        }

    # if to_invoice:
    #     pos_order.action_pos_order_invoice()
    #     pos_order.invoice_id.sudo().action_invoice_open()
    #     pos_order.account_move = pos_order.invoice_id.move_id
