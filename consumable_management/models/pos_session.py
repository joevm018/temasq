from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', required=True)


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def action_pos_session_closing_control(self):
        res = super(PosSession, self).action_pos_session_closing_control()
        pending = ''
        for ord in self.order_ids:
            if ord.picking_id.state != 'done':
                try:
                    ord.picking_id.action_done()
                except:
                    pass
        pickings = self.order_ids.mapped('picking_id').filtered(lambda x: x.state != 'done')
        for i in pickings:
            pending += i.name + '\n'
        if pending:
            raise UserError(_('Please check the following records and validate manually \n\n' + pending))
        return res
