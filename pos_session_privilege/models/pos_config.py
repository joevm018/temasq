from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    user_ids = fields.Many2many('res.users', 'user_pos_conf_rel', 'pos_conf_id', 'user_id', 'Users', copy=False)


class ResUsers(models.Model):
    _inherit = 'res.users'

    pos_config_ids = fields.Many2many('pos.config', 'user_pos_conf_rel', 'user_id', 'pos_conf_id', 'POS Conf', copy=False)
