from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.multi
    def write(self, vals):
        if 'partner_id' in vals:
            if self.purchased_gift_card_ids or self.purchased_package_card_ids:
                raise UserError('Cant change Customer,Already Purchased cards for this Order!!')
        return super(PosOrder, self).write(vals)

    @api.model
    def get_discount_gift_card_product(self):
        return self.env.ref('discount_gift_card.product_product_discount_gift_card').id

    purchased_gift_card_ids = fields.One2many('pos.customer.card', 'gift_order_id',string='Purchased Gift Cards')
    purchased_student_card_ids = fields.One2many('pos.customer.card', 'student_order_id',string='Purchased Student Card')
    purchased_package_card_ids = fields.One2many('pos.customer.card', 'package_order_id',string='Purchased Package Card')
    redeemed_gift_id = fields.Many2one('pos.customer.card', 'Redeemed Gift Card')
    redeemed_package_id = fields.Many2one('pos.customer.card', 'Redeemed Package Card')
    redeemed_amount = fields.Float(string='Redeemed Amount')
    amt_before_redeem = fields.Float(compute='_compute_amount_all', string='Before Redeem', default=0.0)
    redeemed_student_id = fields.Many2one('pos.customer.card', 'Redeemed Student Card')

    def get_package_used_session(self):
        used_session = {}
        for p_lines in self.lines:
            if p_lines.is_redeemed:
                if not used_session.get(p_lines.product_id):
                    used_session[p_lines.product_id] = {}
                    used_session[p_lines.product_id]['count'] = int(p_lines.qty)
                    used_session[p_lines.product_id]['amt'] = p_lines.price_subtotal_incl
                else:
                    count = used_session.get(p_lines.product_id)['count']
                    amt = used_session.get(p_lines.product_id)['amt']
                    used_session[p_lines.product_id]['count'] = count + int(p_lines.qty)
                    used_session[p_lines.product_id]['amt'] = amt + p_lines.price_subtotal_incl
        return used_session

    def get_package_remaining_session(self):
        rem_session = {}
        if self.redeemed_package_id:
            for sess_ids in self.redeemed_package_id.combo_session_ids:
                if sess_ids.state == 'draft':
                    if not rem_session.get(sess_ids.product_id):
                        rem_session[sess_ids.product_id] = {}
                        rem_session[sess_ids.product_id]['count'] = 1
                    else:
                        count = rem_session.get(sess_ids.product_id)['count']
                        rem_session[sess_ids.product_id]['count'] = count + 1
        return rem_session

    @api.multi
    def action_cancel_appt(self):
        for order in self:
            if order.purchased_student_card_ids:
                raise UserError('You Cannot cancel order for which a Student card is Purchased')
            if order.purchased_gift_card_ids:
                raise UserError('You Cannot cancel order for which a Gift card is Purchased')
            if order.purchased_package_card_ids:
                raise UserError('You Cannot cancel order for which a Package card is Purchased')
            if order.redeemed_gift_id:
                raise UserError('You Cannot cancel order that is redeemed using Gift card')
            if order.redeemed_package_id:
                raise UserError('You Cannot cancel order that is redeemed using Package card')
            if order.redeemed_student_id:
                raise UserError('You Cannot cancel order that is redeemed using Student card')
        return super(PosOrder, self).action_cancel_appt()


    @api.multi
    def buy_discount_gift_card(self):
        if not self.partner_id:
            raise UserError('Select Customer!!')
        return {
            'name': _('Buy Cards'),
            'view_id': self.env.ref('discount_gift_card.view_buy_gift_card_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'buy.gift.card.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def redeem_discount_gift_card(self):
        if not self.partner_id:
            raise UserError('Select Customer!!')
        return {
            'name': _('Redeem Cards'),
            'view_id': self.env.ref('discount_gift_card.view_redeem_gift_card_wizard').id,
            'type': 'ir.actions.act_window',
            'res_model': 'redeem.gift.card.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount', 'lines.discount_fixed',
                 'discount_total', 'discount_percent', 'redeemed_gift_id', 'redeemed_amount')
    def _compute_amount_all(self):
        super(PosOrder, self)._compute_amount_all()
        for order in self:
            ord_amount_total =  order.amount_total
            order.amt_before_redeem = ord_amount_total
            order.amount_total = ord_amount_total - order.redeemed_amount

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
                    key = ('product', values['partner_id'],
                           (values['product_id'], tuple(values['tax_ids'][0][2]), values['name']),
                           values['analytic_account_id'], values['debit'] > 0)
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
                        current_value['quantity'] = current_value.get('quantity', 0.0) + values.get('quantity',
                                                                                                    0.0)
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
                taxes = line.tax_ids_after_fiscal_position.filtered(
                    lambda t: t.company_id.id == current_company.id)
                if not taxes:
                    continue
                for tax in taxes.compute_all(line.price_unit * (100.0 - line.discount) / 100.0, cur, line.qty)[
                    'taxes']:
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
                    if disc_perc != 0:
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
            # ...........................................new code start...........................................
            if order.redeemed_amount:
                disc_gift_card_product = self.env.ref('discount_gift_card.product_product_discount_gift_card')
                if disc_gift_card_product.property_account_income_id.id:
                    disc_gift_card_income_account = disc_gift_card_product.property_account_income_id.id
                elif disc_gift_card_product.categ_id.property_account_income_categ_id.id:
                    disc_gift_card_income_account = disc_gift_card_product.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income account for this product: "%s" (id:%d).')
                                    % (disc_gift_card_product.name, disc_gift_card_product.id))
                insert_data('counter_part', {
                                'name': _(disc_gift_card_product.name),  # order.name,
                                'account_id': disc_gift_card_income_account,
                                'credit': ((order.redeemed_amount < 0) and -order.redeemed_amount) or 0.0,
                                'debit': ((order.redeemed_amount > 0) and order.redeemed_amount) or 0.0,
                                'partner_id': partner_id
                            })
            # ...........................................new code end...........................................

            order.write({'state': 'done', 'account_move': move.id})

        all_lines = []
        for group_key, group_data in grouped_data.iteritems():
            for value in group_data:
                all_lines.append((0, 0, value), )
        if move:  # In case no order was changed
            move.sudo().write({'line_ids': all_lines})
            move.sudo().post()
        return True

    def _prepare_invoice(self):
        res = super(PosOrder, self)._prepare_invoice()
        if self.redeemed_gift_id:
            res['redeemed_gift_id'] = self.redeemed_gift_id.id
            res['redeemed_amount'] = self.redeemed_amount
        return res


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    combo_session_id = fields.Many2one('combo.session', string='Redeemed Combo session', readonly=True)
    package_card_id = fields.Many2one('pos.customer.card', 'Redeemed Using Package Card', readonly=True)
    is_redeemed = fields.Boolean('Package Card applied', readonly=True)
    student_card_id = fields.Many2one('pos.customer.card', 'Redeemed Using Student Card', readonly=True)
    is_student_card_redeemed = fields.Boolean('Student Card applied', readonly=True)

    @api.multi
    def unlink(self):
        for order_line in self:
            if order_line.order_id.purchased_gift_card_ids:
                if self.env.ref('discount_gift_card.product_product_discount_gift_card').id == order_line.product_id.id:
                    raise UserError(_("You cannot remove Discount Gift Card from Order line ."))
            if order_line.order_id.purchased_package_card_ids:
                if order_line.product_id.combo_pack:
                    raise UserError(_("You cannot remove Selected Combo Pack from Order line ."))
            if order_line.is_redeemed:
                raise UserError(_("You Cannot delete this Order line .This is redeemed using a package card."))
            if order_line.is_student_card_redeemed:
                raise UserError(_("You Cannot delete this Order line .This is redeemed using a student card."))
        res = super(PosOrderLine, self).unlink()
        return res
