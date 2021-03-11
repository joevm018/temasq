# -*- coding: utf-8 -*-

import logging

from odoo import SUPERUSER_ID
from odoo import fields, api, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class PosConfigNew(models.Model):
    _inherit = 'pos.config'

    service_charge_account = fields.Many2one('account.account', string="VIP Treatment Account", required=True, help="Type of account should be Income")


class NewPosOrder(models.Model):
    _inherit = "pos.order"

    vip_treatment = fields.Boolean('VIP Treatment')
    amt_service_charge = fields.Float(compute='_compute_amount_all', string='VIP Treatment Amt', default=0.0)
    service_charge_percent = fields.Float(string='VIP Treatment(%)', default=0.0)

    @api.onchange('vip_treatment')
    def change_vip_treatment(self):
        if self.vip_treatment:
            self.service_charge_percent = 25
        else:
            self.service_charge_percent = 0

    @api.onchange('service_charge_percent')
    def change_service_charge_percent(self):
        if self.service_charge_percent < 0:
            warning = {
                'title': ' Warning !!!',
                'message': 'Percentage should not be negative!'
            }
            return {'warning': warning, 'value': {'service_charge_percent': ''}}
        if self.service_charge_percent > 100:
            warning = {
                'title': ' Warning !!!',
                'message': 'Percentage should not be greater than 100!'
            }
            return {'warning': warning, 'value': {'service_charge_percent': ''}}

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount', 'lines.discount_fixed',
                 'discount_total', 'discount_percent', 'service_charge_percent')
    def _compute_amount_all(self):
        super(NewPosOrder, self)._compute_amount_all()
        for order in self:
            # order_amount_total = order.amount_total
            order_amount_total = order.amt_before_discount
            if order.service_charge_percent > 0:
                order.amt_service_charge = (order_amount_total * order.service_charge_percent / 100)
                order.amount_total += (order_amount_total * order.service_charge_percent / 100)

    @api.model
    def _order_fields(self, ui_order):
        service_charge = super(NewPosOrder, self)._order_fields(ui_order)
        if ui_order.get('vip_percent'):
            service_charge['service_charge_percent'] = ui_order['vip_percent']
        return service_charge

    def _create_account_move_line(self, session=None, move=None):
        # Tricky, via the workflow, we only have one id in the ids variable
        """Create a account move line of order grouped by products or not."""
        IrProperty = self.env['ir.property']
        ResPartner = self.env['res.partner']

        if session and not all(session.id == order.session_id.id for order in self):
            raise UserError(_('Selected orders do not have the same session!'))

        grouped_data = {}
        have_to_group_by = session and session.config_id.group_by or False
        rounding_method = session and session.config_id.company_id.tax_calculation_rounding_method

        for order in self.filtered(lambda o: not o.account_move or order.state == 'paid'):
            current_company = order.sale_journal.company_id
            account_def = IrProperty.get(
                'property_account_receivable_id', 'res.partner')
            order_account = order.partner_id.property_account_receivable_id.id or account_def and account_def.id
            partner_id = ResPartner._find_accounting_partner(order.partner_id).id or False
            if move is None:
                # Create an entry for the sale
                journal_id = self.env['ir.config_parameter'].sudo().get_param(
                    'pos.closing.journal_id_%s' % current_company.id, default=order.sale_journal.id)
                move = self._create_account_move(
                    order.session_id.start_at, order.name, int(journal_id), order.company_id.id)

            def insert_data(data_type, values):
                # if have_to_group_by:
                values.update({
                    'partner_id': partner_id,
                    'move_id': move.id,
                })

                if data_type == 'product':
                    key = ('product', values['partner_id'], (values['product_id'], tuple(values['tax_ids'][0][2]), values['name']), values['analytic_account_id'], values['debit'] > 0)
                elif data_type == 'tax':
                    key = ('tax', values['partner_id'], values['tax_line_id'], values['debit'] > 0)
                elif data_type == 'counter_part':
                    key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
                else:
                    return

                grouped_data.setdefault(key, [])

                if have_to_group_by:
                    if not grouped_data[key]:
                        grouped_data[key].append(values)
                    else:
                        current_value = grouped_data[key][0]
                        current_value['quantity'] = current_value.get('quantity', 0.0) + values.get('quantity', 0.0)
                        current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit', 0.0)
                        current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
                else:
                    grouped_data[key].append(values)

            # because of the weird way the pos order is written, we need to make sure there is at least one line,
            # because just after the 'for' loop there are references to 'line' and 'income_account' variables (that
            # are set inside the for loop)
            # TOFIX: a deep refactoring of this method (and class!) is needed
            # in order to get rid of this stupid hack
            assert order.lines, _('The POS order must have lines when calling this method')
            # Create an move for each order line
            cur = order.pricelist_id.currency_id
            for line in order.lines:
                amount = line.price_subtotal

                # Search for the income account
                if line.product_id.property_account_income_id.id:
                    income_account = line.product_id.property_account_income_id.id
                elif line.product_id.categ_id.property_account_income_categ_id.id:
                    income_account = line.product_id.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income '
                                      'account for this product: "%s" (id:%d).')
                                    % (line.product_id.name, line.product_id.id))

                name = line.product_id.name
                if line.notice:
                    # add discount reason in move
                    name = name + ' (' + line.notice + ')'

                # Create a move for the line for the order line
                insert_data('product', {
                    'name': name,
                    'quantity': line.qty,
                    'product_id': line.product_id.id,
                    'account_id': income_account,
                    'analytic_account_id': self._prepare_analytic_account(line),
                    'credit': ((amount > 0) and amount) or 0.0,
                    'debit': ((amount < 0) and -amount) or 0.0,
                    'tax_ids': [(6, 0, line.tax_ids_after_fiscal_position.ids)],
                    'partner_id': partner_id
                })

                # Create the tax lines
                taxes = line.tax_ids_after_fiscal_position.filtered(lambda t: t.company_id.id == current_company.id)
                if not taxes:
                    continue
                for tax in taxes.compute_all(line.price_unit * (100.0 - line.discount) / 100.0, cur, line.qty)['taxes']:
                    insert_data('tax', {
                        'name': _('Tax') + ' ' + tax['name'],
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                        'account_id': tax['account_id'] or income_account,
                        'credit': ((tax['amount'] > 0) and tax['amount']) or 0.0,
                        'debit': ((tax['amount'] < 0) and -tax['amount']) or 0.0,
                        'tax_line_id': tax['id'],
                        'partner_id': partner_id
                    })

            # round tax lines per order
            if rounding_method == 'round_globally':
                for group_key, group_value in grouped_data.iteritems():
                    if group_key[0] == 'tax':
                        for line in group_value:
                            line['credit'] = cur.round(line['credit'])
                            line['debit'] = cur.round(line['debit'])


            if order.discount_total:
                if not order.session_id.config_id.discount_account:
                    raise UserError(_('Define Discount account for the POS under configuration!'))
                insert_data('counter_part', {
                    'name': 'Discount',
                    'account_id': order.session_id.config_id.discount_account.id,
                    'credit': ((order.discount_total < 0) and -order.discount_total) or 0.0,
                    'debit': ((order.discount_total > 0) and order.discount_total) or 0.0,
                    'partner_id': partner_id
                })
            elif order.discount_percent:
                if not order.session_id.config_id.discount_account:
                    raise UserError(_('Define Discount account for the POS under configuration!'))
                discount = order.amt_discount
                insert_data('counter_part', {
                    'name': 'Discount',
                    'account_id': order.session_id.config_id.discount_account.id,
                    'credit': ((discount < 0) and -discount) or 0.0,
                    'debit': ((discount > 0) and discount) or 0.0,
                    'partner_id': partner_id
                })
            if order.service_charge_percent:
                if not order.session_id.config_id.service_charge_account:
                    raise UserError(_('Define VIP Treatment account for the POS under configuration!'))
                service_charge = order.amt_service_charge
                insert_data('counter_part', {
                    'name': 'VIP Treatment',
                    'account_id': order.session_id.config_id.service_charge_account.id,
                    'debit': ((service_charge < 0) and -service_charge) or 0.0,
                    'credit': ((service_charge > 0) and service_charge) or 0.0,
                    'partner_id': partner_id
                })
            # counterpart
            order_amount_total = order.amount_total
            insert_data('counter_part', {
                'name': _("Trade Receivables"),  # order.name,
                'account_id': order_account,
                'credit': ((order_amount_total < 0) and -order_amount_total) or 0.0,
                'debit': ((order_amount_total > 0) and order_amount_total) or 0.0,
                'partner_id': partner_id
            })

            order.write({'state': 'done', 'account_move': move.id})

        all_lines = []
        for group_key, group_data in grouped_data.iteritems():
            for value in group_data:
                all_lines.append((0, 0, value),)
        if move:  # In case no order was changed
            move.sudo().write({'line_ids': all_lines})
            move.sudo().post()
        return True


class NewPosLines(models.Model):
    _inherit = "pos.order.line"

    after_global_disc_subtotal = fields.Float(string='Total after global disc', compute='_after_global_disc_subtotal')
    after_vip_subtotal = fields.Float(string='Total after global disc', compute='_after_vip_subtotal')

    @api.multi
    def _after_global_disc_subtotal(self):
        for order_line in self:
            # simply added this field. Taking same value of  price_subtotal_incl. modifying value in global discount module and vip module.
            # Also this field is used in 3 reports. can use this field instead on modifying parser functions
            amount_total = order_line.order_id.amount_total - order_line.order_id.amt_service_charge
            amt_before_discount = order_line.order_id.amt_before_discount
            if amt_before_discount:
                div_value = amount_total / amt_before_discount
                order_line.after_global_disc_subtotal = round(order_line.price_subtotal_incl * div_value, 2)
            else:
                order_line.after_global_disc_subtotal = 0.0

    @api.multi
    def _after_vip_subtotal(self):
        for order_line in self:
            amount_total = order_line.order_id.amt_service_charge
            amt_before_vip = order_line.order_id.amt_before_discount
            if amt_before_vip:
                div_value = amount_total / amt_before_vip
                order_line.after_vip_subtotal = round(order_line.price_subtotal_incl * div_value, 2)
            else:
                order_line.after_vip_subtotal = 0.0