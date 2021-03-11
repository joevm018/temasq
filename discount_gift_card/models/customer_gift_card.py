from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class CustomerGiftCard(models.Model):
    _name = "pos.customer.card"

    @api.multi
    @api.depends('type', 'name', 'remaining_amount', 'combo_session_ids.state', 'combo_session_ids',
                 'university_expiry_date', 'partner_id.university_expiry_date')
    def _compute_is_zero_card(self):
        for card in self:
            val_is_zero_card = False
            if card.state == 'active':
                if card.type == 'type_discount_gift_card':
                    if not card.remaining_amount:
                        val_is_zero_card = True
                if card.type == 'type_package_card':
                    remain_session = any([session.state == 'draft' for session in card.combo_session_ids])
                    if not remain_session:
                        val_is_zero_card = True
                if card.type == 'type_student_card':
                    if card.university_expiry_date < fields.Date.today():
                        val_is_zero_card = True
            card.is_zeroo_card = val_is_zero_card

    # Mandatory (New-All)
    name = fields.Char('Name', required=True, readonly=True, default='/')
    card_no = fields.Char('Card No', required=True, readonly=True, states={'new': [('readonly', False)]})
    state = fields.Selection([('new', 'New'), ('active', 'Active'), ('cancel', 'Cancelled')], string='Status',
                             index=True, readonly=True, copy=False, default='new', required=True)
    type = fields.Selection([('type_discount_gift_card', 'Discount Gift Card'), ('type_package_card', 'Package Card'),
                             ('type_student_card', 'Student Card')], string='Type', required=True)
    # Mandatory (Active-All)
    purchased_date = fields.Date(string='Purchased on', readonly=True, required=False, states={'active': [('required', True)]})
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)], readonly=True, required=False, states={'active': [('required', True)]})
    transaction_orders = fields.Many2many('pos.order', string='Gift Card Transaction details', readonly=True)
    # Mandatory (All)
    is_zeroo_card = fields.Boolean('Zero card', compute='_compute_is_zero_card', store=True)
    # Mandatory (Active-Discount Gift Card)
    discount_gift_card_amount = fields.Float('Gift Amount', readonly=True)
    remaining_amount = fields.Float('Balance Amount', readonly=True)
    gift_order_id = fields.Many2one('pos.order', 'Gift card Purchased from Order', required=False)
    # Mandatory (Active-Package Card)
    package_card_amount = fields.Float('Amount', readonly=True)
    package_combo_item = fields.Many2one('product.product', string="Combo Pack", domain=[('combo_pack', '=', True)], readonly=False)
    is_wellness_card = fields.Boolean('WELLNESS AND INDULGENCE')
    package_combo_wellness_ids= fields.Many2many('product.product', string="Combo Packs", domain=[('combo_pack', '=', True)])
    combo_session_ids = fields.One2many('combo.session', 'package_card_id', 'Combo sessions', readonly=True)
    package_order_id = fields.Many2one('pos.order', 'Package Purchased from Order', required=False)
    transaction_package_orders = fields.One2many('pos.order.line', 'package_card_id',string='Package Card Transaction details', readonly=True)
    # Mandatory (Active-Student Card)
    student_order_id = fields.Many2one('pos.order', 'Student card Purchased from Order', required=False)
    qatar_university_id = fields.Char(related='partner_id.qatar_university_id', string='Qatar university ID')
    university_expiry_date = fields.Date(related='partner_id.university_expiry_date', string='Expiry Date')
    transaction_student_orders = fields.One2many('pos.order.line', 'student_card_id', string='Student Card Transaction details', readonly=True)

    _sql_constraints = [
        ('name', 'unique(name)', 'Card Name must be unique.'),
        ('card_no', 'unique( card_no)', 'Card Number must be unique.'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('type') == 'type_package_card' or self._context['default_type'] == 'type_package_card':
            if not vals.get('package_combo_item') or vals.get('package_combo_item')==False:
                raise UserError('For Package Card, Need to mention Combo pack')
        vals['name'] = self.env['ir.sequence'].next_by_code('pos.customer.card')
        return super(CustomerGiftCard, self).create(vals)

    @api.multi
    def action_cancel(self):
        for session in self.combo_session_ids:
            session.write({'state': 'cancel'})
        self.state = 'cancel'
