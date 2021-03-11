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
    discount_account = fields.Many2one('account.account', string="Discount Account", required=True)


class NewPosOrder(models.Model):
    _inherit = "pos.order"

    amt_before_discount = fields.Float(compute='_compute_amount_all', string='Before Discount', default=0.0)
    amt_discount = fields.Float(compute='_compute_amount_all', string='Discount Amt', default=0.0)
    discount_total = fields.Float(string='Total Discount(Fixed)', default=0.0)
    discount_percent = fields.Float(string='Total Discount(%)', default=0.0)

    @api.onchange('discount_percent')
    def change_discount_fixed(self):
        if self.discount_percent:
            self.discount_total = 0.0

    @api.onchange('discount_total')
    def change_discount_percent(self):
        if self.discount_total:
            self.discount_percent = 0.0

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount', 'lines.discount_fixed','discount_total','discount_percent')
    def _compute_amount_all(self):
        super(NewPosOrder, self)._compute_amount_all()
        for order in self:
            currency = order.pricelist_id.currency_id
            amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
            order.amount_total = order.amount_tax + amount_untaxed
            if order.discount_total:
                order.amount_total -= order.discount_total
                order.amt_discount = order.discount_total
            if order.discount_percent > 0:
                order.amount_total -= ((order.amount_tax + amount_untaxed) * order.discount_percent / 100)
                order.amt_discount = ((order.amount_tax + amount_untaxed) * order.discount_percent / 100)
            order.amt_before_discount = order.amount_tax + amount_untaxed

    @api.multi
    def reverse(self):
        reverse_order = super(NewPosOrder, self).reverse()
        reversed_id = self.reverse_id
        if reversed_id.discount_total:
            reversed_id.write({'discount_total': -reversed_id.discount_total})
        return reverse_order

    def _prepare_invoice(self):
        res = super(NewPosOrder, self)._prepare_invoice()
        if self.discount_total:
            res['discount_total'] = self.discount_total
        if self.discount_percent:
            res['discount_percent'] = self.discount_percent
        return res

    @api.model
    def _order_fields(self, ui_order):
        new_discount = super(NewPosOrder, self)._order_fields(ui_order)
        new_discount['discount_total'] = ui_order['discount_total']
        new_discount['discount_percent'] = ui_order['discount_percent']
        return new_discount

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
                if 100 - order.discount_percent:
                    currency = order.pricelist_id.currency_id
                    amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
                    discount = ((order.amount_tax + amount_untaxed) * order.discount_percent / 100)
                else:
                    disc_perc = (100 - order.discount_percent)
                    if disc_perc !=0 :
                        discount = (100 * order.amount_total) / disc_perc
                    else:
                        discount = 100 * order.amount_total
                    discount -= order.amount_total
                insert_data('counter_part', {
                    'name': 'Discount',
                    'account_id': order.session_id.config_id.discount_account.id,
                    'credit': ((discount < 0) and -discount) or 0.0,
                    'debit': ((discount > 0) and discount) or 0.0,
                    'partner_id': partner_id
                })
            # counterpart
            insert_data('counter_part', {
                'name': _("Trade Receivables"),  # order.name,
                'account_id': order_account,
                'credit': ((order.amount_total < 0) and -order.amount_total) or 0.0,
                'debit': ((order.amount_total > 0) and order.amount_total) or 0.0,
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

    @api.multi
    def _after_global_disc_subtotal(self):
        for order_line in self:
            # simply added this field. Taking same value of  price_subtotal_incl. modifying value in global discount module.
            # Also this field is used in 3 reports. can use this field instead on modifying parser functions
            amount_total = order_line.order_id.amount_total
            amt_before_discount = order_line.order_id.amt_before_discount
            if amt_before_discount:
                div_value = amount_total / amt_before_discount
                order_line.after_global_disc_subtotal = round(order_line.price_subtotal_incl * div_value, 2)
            else:
                order_line.after_global_disc_subtotal = 0.0

    discount_fixed = fields.Float('Discount Fixed', default = 0.0)
    discountStr = fields.Char('discountStr')


    @api.onchange('discount_fixed')
    def change_discount_fixed_line(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.onchange('discount')
    def change_discount_line(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange('qty')
    def change_qty_line(self):
        self._compute_amount_line_all()

    @api.onchange('price_unit')
    def change_price_unit_line(self):
        self._compute_amount_line_all()

    @api.depends('price_unit', 'tax_ids', 'qty', 'discount', 'discount_fixed', 'product_id')
    def _compute_amount_line_all(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            taxes = line.tax_ids.filtered(lambda tax: tax.company_id.id == line.order_id.company_id.id)
            fiscal_position_id = line.order_id.fiscal_position_id
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(taxes)
# =============== finding subtotal for each orderline=========================================================
            if line.discount_fixed != 0:
                price = line.price_unit
                line.price_subtotal = line.price_subtotal_incl = price * line.qty - line.discount_fixed
            else:
                price = line.price_unit
                line.price_subtotal = line.price_subtotal_incl = (price * line.qty) - (price * line.qty * (line.discount or 0.0) / 100)
            if taxes:
                taxes = taxes.compute_all(price, currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                line.price_subtotal = taxes['total_excluded']
                line.price_subtotal_incl = taxes['total_included']
            line.price_subtotal = currency.round(line.price_subtotal)
            line.price_subtotal_incl = currency.round(line.price_subtotal_incl)


class AccountMoveLineExtra(models.Model):
    _inherit = 'account.move.line'

    _sql_constraints = [
        ('credit_debit1', 'CHECK (credit*debit=0)', 'Wrong credit or debit value in accounting entry !'),
        ('credit_debit2', 'CHECK (credit*debit=0)', 'Wrong credit or debit value in accounting entry !'),
    ]

    @api.multi
    def _update_check(self):
        """ This module is overwritten, to avoid the warning raised when we edit the journal entries"""
        move_ids = set()
        for line in self:
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.id not in move_ids:
                move_ids.add(line.move_id.id)
            self.env['account.move'].browse(list(move_ids))._check_lock_date()
        return True

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        """ This function is overwritten to remove some warnings"""
        # Perform all checks on lines
        company_ids = set()
        all_accounts = []
        partners = set()
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.account_id.internal_type in ('receivable', 'payable')):
                partners.add(line.partner_id.id)
            if line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries!'))
        if not all_accounts[0].reconcile:
            raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (
            all_accounts[0].name, all_accounts[0].code))
        # reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        # if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
            # add writeoff line to reconcile algo and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
            return writeoff_to_reconcile
        return True


class AccountMoveNew(models.Model):
    _inherit = 'account.move'

    @api.multi
    def assert_balanced(self):
        """Overwritten to remove the warning raised.(For editing the journal entry)"""
        if not self.ids:
            return True
        prec = self.env['decimal.precision'].precision_get('Account')

        self._cr.execute("""\
                SELECT      move_id
                FROM        account_move_line
                WHERE       move_id in %s
                GROUP BY    move_id
                HAVING      abs(sum(debit) - sum(credit)) > %s
                """, (tuple(self.ids), 10 ** (-max(5, prec))))
        return True












