from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class BuyGiftCardWizard(models.TransientModel):
    _name = "buy.gift.card.wizard"

    discount_gift_card_amount = fields.Float('Amount', required=False)
    card_no = fields.Char('Card No', required=True)
    type = fields.Selection([('type_discount_gift_card', 'Discount Gift Card'), ('type_package_card', 'Package Card'),
                            ('type_student_card', 'Student Card')], string='Type', required=True)
    package_combo_item = fields.Many2one('product.product', string="Combo Pack", domain=[('combo_pack', '=', True)])
    package_card_amount = fields.Float('Amount',related='package_combo_item.list_price', readonly=True)

    @api.onchange('card_no')
    def onchange_card_no(self):
        if self.card_no:
            gift_card_here = self.env['pos.customer.card'].search([('card_no', 'ilike', self.card_no),
                                                                   ('state', '=', 'new')])
            if len(gift_card_here) > 1:
                return {
                    'warning': {'title': _('Warning'), 'message': _('More Cards found'), },
                }
            if not gift_card_here:
                self.type = ''
                self.discount_gift_card_amount = ''
                self.card_no = ''
                self.package_card_amount = ''
                self.package_combo_item = False
                return {
                    'warning': {'title': _('Warning'), 'message': _('There is no active card with this Card No'), },
                }
            self.type = gift_card_here.type
            if gift_card_here.type in ['type_discount_gift_card', 'type_student_card']:
                self.package_combo_item = False
            if gift_card_here.type in ['type_package_card', 'type_student_card']:
                # self.package_combo_item = gift_card_here.package_combo_item
                self.discount_gift_card_amount = 0.00
                if gift_card_here.is_wellness_card:
                    return {'domain':{'package_combo_item':[('id', 'in', gift_card_here.package_combo_wellness_ids.ids)]}}
                else:
                    return {'domain':{'package_combo_item':[('id', '=', gift_card_here.package_combo_item.id)]}}
        else:
            self.type = ''
            self.discount_gift_card_amount = ''
            self.package_card_amount = ''
            self.package_combo_item = False

    @api.multi
    def action_confirm(self):
        order = False
        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['pos.order'].browse(active_id)
            partner_id = order.partner_id
            if self.type == 'type_discount_gift_card':
                if self.discount_gift_card_amount <= 100:
                    raise UserError('Amount should be greater than 100')
                if order:
                    gift_card_exists = self.env['pos.customer.card'].search([('card_no', 'ilike', self.card_no),
                                                                             ('state', '=', 'new'),
                                                                             ('type', '=', self.type)],
                                                                            limit=1)
                    if len(gift_card_exists) > 1:
                        raise UserError('More Gift Cards found!!')
                    if not gift_card_exists:
                        raise UserError('No Gift Card Exists with this Card No!!')
                    disc_gift_card_vals = {
                        'purchased_date':  fields.Date.today(),
                        'partner_id':  partner_id.id,
                        'gift_order_id':  order.id,
                        'state':  'active',
                        'discount_gift_card_amount':  self.discount_gift_card_amount,
                        'remaining_amount':  self.discount_gift_card_amount,
                    }
                    gift_card_exists.write(disc_gift_card_vals)
                    order_list = []
                    for line in order.lines:
                        order_list.append(line.id)
                    product_discount_gift_card = self.env.ref('discount_gift_card.product_product_discount_gift_card')
                    order_list.append(self.env['pos.order.line'].create({
                        'name': product_discount_gift_card.name,
                        'product_id': product_discount_gift_card.id,
                        'price_unit': self.discount_gift_card_amount,
                    }).id)
                    order['lines'] = [(6, 0, order_list)]
            if self.type == 'type_package_card':
                if order:
                    package_card_exists = self.env['pos.customer.card'].search([('card_no', 'ilike', self.card_no),
                                                                             ('state', '=', 'new'),
                                                                             ('type', '=', self.type)],
                                                                            limit=1)
                    if len(package_card_exists) > 1:
                        raise UserError('More Package Cards found!!')
                    if not package_card_exists:
                        raise UserError('No Package Card Exists with this Card No!!')
                    combo_item = self.package_combo_item
                    if not package_card_exists.is_wellness_card and combo_item.id != package_card_exists.package_combo_item.id:
                        raise UserError('Selected combo pack doesnt belong to this package card')
                    if not combo_item.pack_ids:
                        raise UserError('Define Combo items to Combo pack')
                    package_card_vals = {
                        'purchased_date':  fields.Date.today(),
                        'partner_id':  partner_id.id,
                        'package_order_id':  order.id,
                        'state':  'active',
                        'package_combo_item':  combo_item.id,
                        'package_card_amount':  self.package_card_amount,
                    }
                    package_card_exists.write(package_card_vals)
                    session_obj = self.env['combo.session']
                    vals = {
                        'package_card_id': package_card_exists.id,
                        'customer_id': partner_id.id,
                        'combo_id': combo_item.id,
                        'date': False,
                        'state': 'draft',
                    }
                    for combo_line in combo_item.pack_ids:
                        countt = 0
                        vals['product_id'] = combo_line.product_id.id
                        vals['price'] = combo_line.price
                        vals['original_price'] = combo_line.product_id.list_price
                        while countt < combo_line.count:
                            session_obj.create(vals)
                            countt += 1
                    # count += 1
                    order_list = []
                    for line in order.lines:
                        order_list.append(line.id)
                    order_list.append(self.env['pos.order.line'].create({
                        'name': combo_item.name,
                        'product_id': combo_item.id,
                        'price_unit': self.package_card_amount,
                    }).id)
                    order['lines'] = [(6, 0, order_list)]
        if self.type == 'type_student_card':
            if not partner_id.is_student:
                raise UserError('Only students are allowed to purchase this card !!')
            if not partner_id.qatar_university_id:
                raise UserError('This card is only available for Qatar university students')
            if not partner_id.university_expiry_date:
                raise UserError('Please mention Expiry date of Qatar university ID')
            if partner_id.university_expiry_date< fields.Date.today():
                raise UserError('Qatar university ID Expired')
            if order:
                student_card_exists = self.env['pos.customer.card'].search([('card_no', 'ilike', self.card_no),
                                                                         ('state', '=', 'new'),
                                                                         ('type', '=', self.type)],
                                                                        limit=1)
                if len(student_card_exists) > 1:
                    raise UserError('More Student Cards found!!')
                if not student_card_exists:
                    raise UserError('No Student Card Exists with this Card No!!')
                disc_student_card_vals = {
                    'purchased_date': fields.Date.today(),
                    'partner_id': partner_id.id,
                    'student_order_id': order.id,
                    'state': 'active',
                }
                student_card_exists.write(disc_student_card_vals)
                order_list = []
                for line in order.lines:
                    order_list.append(line.id)
                product_discount_gift_card = self.env.ref('discount_gift_card.product_product_student_card')
                order_list.append(self.env['pos.order.line'].create({
                    'name': product_discount_gift_card.name,
                    'product_id': product_discount_gift_card.id,
                    'price_unit': self.discount_gift_card_amount,
                }).id)
                order['lines'] = [(6, 0, order_list)]