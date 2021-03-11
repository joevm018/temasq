from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class ChangeDiscWizard(models.TransientModel):
    _name = "change.price.discount.wizard"

    pos_supervisor_card_pin = fields.Char('Supervisor PIN', required=True)

    @api.onchange('pos_supervisor_card_pin')
    def onchange_pos_supervisor_card_pin(self):
        if self.pos_supervisor_card_pin:
            user_supervisor = self.env['res.users'].search([('pos_supervisor_card_pin',
                                                             'ilike', self.pos_supervisor_card_pin)], limit=1)
            if user_supervisor:
                if len(user_supervisor[0].pos_supervisor_card_pin) != len(self.pos_supervisor_card_pin):
                    user_supervisor = False
            if not user_supervisor:
                self.pos_supervisor_card_pin = ''
                return {
                    'warning': {'title': _('Warning'), 'message': _('There is no Supervisor card registered '
                                                                    'with this Card No'), },
                }

    @api.multi
    def action_confirm(self):
        self.onchange_pos_supervisor_card_pin()
        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['pos.order'].browse(active_id)
            vals = {
                'active_for_supervisor': True,
                'wizard_pin_update': True,
                         }
            order.write(vals)
            for line in order.lines:
                line.write(vals)