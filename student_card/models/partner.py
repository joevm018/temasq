# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime
from odoo import SUPERUSER_ID
import time,  pytz,base64
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date


class Partner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean('Is Student')
    qatar_university_id = fields.Char('Qatar university ID')
    university_expiry_date = fields.Date('Expiry Date')