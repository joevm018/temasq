from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class RedeemGiftCardWizard(models.TransientModel):
    _name = "redeem.gift.card.wizard"

    card_no = fields.Char('Card No', required=True)
    type = fields.Selection([('type_discount_gift_card', 'Discount Gift Card'), ('type_package_card', 'Package Card'),
                            ('type_student_card', 'Student Card')], string='Type', required=True)
    balance_line_ids = fields.One2many('package.card.balance', 'redeem_wizard', string='Balance sessions')

    # @api.onchange('type')
    # def onchange_type(self):
    #     self.card_no = ''

    def check_if_card_exists(self, type):
        if self.card_no:
            gift_card = self.env['pos.customer.card'].search([('state', '=', 'active'),
                                                              ('card_no', 'ilike', self.card_no),
                                                              ('type', '=', type)])
            if len(gift_card) > 1:
                raise UserError('More Cards found!!')
            if not gift_card:
                raise UserError('There is no active card with this Card No')
            return gift_card[0]

    @api.onchange('card_no')
    def onchange_card_no(self):
        list_balance = []
        if self.card_no:
            gift_card_here = self.env['pos.customer.card'].search([('state', '=', 'active'),
                                                              ('card_no', 'ilike', self.card_no),
                                                                   ])
            if len(gift_card_here) > 1:
                self.card_no = ''
                self.type = ''
                return {
                    'warning': {'title': _('Warning'), 'message': _('More Cards found!!'), },
                }
            if not gift_card_here:
                self.card_no = ''
                self.type = ''
                self.balance_line_ids = [(6, 0, [])]
                return {
                    'warning': {'title': _('Warning'), 'message': _('There is no active card with this Card No'), },
                }
            self.type = gift_card_here.type
            if gift_card_here.type == 'type_package_card':
                gift_card = False
                if self.card_no:
                    gift_card = self.env['pos.customer.card'].search([('state', '=', 'active'),
                                                                      ('card_no', 'ilike', self.card_no),
                                                                      ('type', '=', gift_card_here.type)])
                    if len(gift_card) > 1:
                        raise UserError('More Cards found!!')
                    if gift_card:
                        for session in gift_card.combo_session_ids:
                            if session.state == 'draft':
                                bal_rec = self.env['package.card.balance'].create({
                                    'name': session.name,
                                    'product_id': session.product_id.id,
                                    'price': session.price,
                                })
                                list_balance.append(bal_rec.id)
            return {'value': {'balance_line_ids': list_balance}}
        else:
            self.card_no = ''
            self.type = ''
            self.balance_line_ids = [(6, 0, [])]

    @api.multi
    def action_show_balance(self):
        gift_card = self.check_if_card_exists(self.type)
        if self.type == 'type_discount_gift_card':
            raise UserError(_('Remaining balance of this card is %s') % (gift_card.remaining_amount))

    @api.multi
    def action_confirm(self):
        order = False
        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['pos.order'].browse(active_id)
            partner_id = order.partner_id
            if self.type == 'type_discount_gift_card':
                if order.redeemed_gift_id:
                    raise UserError('Already redeemed using a Discount gift card')
                gift_card = self.check_if_card_exists(self.type)
                if not gift_card.remaining_amount:
                    raise UserError('There is insufficient balance in this card')
                service_amt = 0.0
                for ord_line in order.lines:
                    disc_gift_card_product = self.env.ref('discount_gift_card.product_product_discount_gift_card')
                    if ord_line.product_id.type == 'service' and ord_line.product_id.id != disc_gift_card_product.id \
                            and not ord_line.product_id.combo_pack:
                        service_amt += ord_line.price_subtotal_incl
                consider_service_total_amt = min(service_amt,order.amount_total)
                if not consider_service_total_amt:
                    raise UserError('There is no Service to redeem from this Order')
                order_list = [order.id]
                for t_orders in gift_card.transaction_orders:
                    order_list.append(t_orders.id)
                redeemed_amount = min(consider_service_total_amt, gift_card.remaining_amount)
                order.write({'redeemed_gift_id': gift_card.id,
                             'redeemed_amount': redeemed_amount})
                order._compute_amount_all()
                gift_card.write({'remaining_amount': gift_card.remaining_amount - redeemed_amount,
                                 'transaction_orders': [(6, 0, order_list)]})
                if order.test_paid():
                    order.action_pos_order_paid()
                    order.cashier_name = self.env.user.id
            if self.type == 'type_package_card':
                gift_card = self.check_if_card_exists(self.type)
                if order.redeemed_package_id:
                    if order.redeemed_package_id.id != gift_card.id:
                        raise UserError('Already redeemed using another Package card, Use same for this Order')
                remain_session = any([session.state == 'draft' for session in gift_card.combo_session_ids])
                if not remain_session:
                    raise UserError('No sessions remaining in this card')
                now_redeemed = False
                for ord_line in order.lines:
                    not_redeemed = not ord_line.is_redeemed
                    if not_redeemed:
                        session_avail = self.env['combo.session'].search(
                            [('state', '=', 'draft'),('package_card_id', '=', gift_card.id),
                             ('product_id', '=', ord_line.product_id.id)], limit=1)
                        if session_avail:
                            if ord_line.qty > 1:
                                raise UserError('In-order to redeem Using Package Card, You need to split order lines'
                                                ' with Qty: 1')
                            if ord_line.qty == 1:
                                now_redeemed = True
                                ord_line.write({
                                    'is_redeemed': True,
                                    'package_card_id': gift_card.id,
                                    'combo_session_id': session_avail.id,
                                    'price_unit': 0,
                                })
                                session_avail.write({
                                    'order_line_id': ord_line.id,
                                    'order_id': ord_line.order_id.id,
                                    'state': 'done',
                                    'redeemed_date': fields.Date.today(),
                                })
                                order.write({'redeemed_package_id':gift_card.id})
                                if order.test_paid():
                                    order.action_pos_order_paid()
                                    order.cashier_name = self.env.user.id
                if not now_redeemed:
                    raise UserError('Nothing to redeem Using Package Card')
            if self.type == 'type_student_card':
                if not partner_id.is_student:
                    raise UserError('Only students are allowed to redeem using this card !!')
                if not partner_id.qatar_university_id:
                    raise UserError('This card is only available for Qatar university students')
                if not partner_id.university_expiry_date:
                    raise UserError('Please mention Expiry date of Qatar university ID')
                if partner_id.university_expiry_date < fields.Date.today():
                    raise UserError('Qatar university ID Expired')
                student_card = self.check_if_card_exists(self.type)
                if order.redeemed_student_id:
                    if order.redeemed_student_id.id != student_card.id:
                        raise UserError('Already redeemed using another Student card, Use same for this Order')
                service_exists = False
                disc_gift_card_product = self.env.ref('discount_gift_card.product_product_discount_gift_card')
                disc_student_card_product = self.env.ref('discount_gift_card.product_product_student_card')
                for ord_line in order.lines:
                    if ord_line.product_id.type == 'service' and ord_line.product_id.id != disc_gift_card_product.id \
                            and ord_line.product_id.id != disc_student_card_product.id \
                            and not ord_line.product_id.combo_pack:
                        service_exists = True
                if not service_exists:
                    raise UserError('There is no Service to redeem using this Student Card')
                for ord_line in order.lines:
                    if ord_line.product_id.type == 'service' and ord_line.product_id.id != disc_gift_card_product.id \
                            and ord_line.product_id.id != disc_student_card_product.id \
                            and not ord_line.product_id.combo_pack:
                        ord_line.write({
                            'is_student_card_redeemed': True,
                            'student_card_id': student_card.id,
                            'discount': 15,
                        })
                        order.write({'redeemed_student_id': student_card.id})
                        if order.test_paid():
                            order.action_pos_order_paid()
                            order.cashier_name = self.env.user.id

class RedeemPackageCardBalance(models.TransientModel):
    _name = 'package.card.balance'

    redeem_wizard = fields.Many2one('redeem.gift.card.wizard', 'Redeem Wizard', required=False, readonly=True)
    name = fields.Char('Ref', readonly=True)
    product_id = fields.Many2one('product.product', 'Item', required=True, readonly=True)
    price = fields.Float('Offer Price', readonly=True)