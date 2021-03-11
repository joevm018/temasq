from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.multi
    def open_ui(self):
        raise UserError(_("You cannot do this action !!!"))
        assert len(self.ids) == 1, "you can open only one session at a time"
        return {
            'type': 'ir.actions.act_url',
            'url': '/pos/web/',
            'target': 'self',
        }

    @api.multi
    def open_session_cb(self):
        raise UserError(_("You cannot do this action !!!"))
        assert len(self.ids) == 1, "you can open only one session at a time"
        if not self.current_session_id:
            self.current_session_id = self.env['pos.session'].create({
                'user_id': self.env.uid,
                'config_id': self.id
            })
            if self.current_session_id.state == 'opened':
                return self.open_ui()
            return self._open_session(self.current_session_id.id)
        return self._open_session(self.current_session_id.id)

    @api.multi
    def open_existing_session_cb(self):
        raise UserError(_("You cannot do this action !!!"))
        assert len(self.ids) == 1, "you can open only one session at a time"
        return self._open_session(self.current_session_id.id)


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.multi
    def open_frontend_cb(self):
        raise UserError(_("You cannot do this action !!!"))

        if not self.ids:
            return {}
        for session in self.filtered(lambda s: s.user_id.id != self.env.uid):
            raise UserError(_("You cannot use the session of another users. This session is owned by %s. "
                              "Please first close this one to use this point of sale.") % session.user_id.name)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/pos/web/',
        }
