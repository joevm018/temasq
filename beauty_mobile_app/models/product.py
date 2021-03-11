from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    video_url = fields.Char('Video URL')
    product_description = fields.Html('Description')