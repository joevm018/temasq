from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class Users(models.Model):
    _inherit = "res.users"

    pos_supervisor_card_pin = fields.Char('Supervisor PIN', required=False,
                                          help='A Supervisor PIN used to change price and discount in the POS')
