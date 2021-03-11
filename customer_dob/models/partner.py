# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime
from odoo import SUPERUSER_ID
import time,  pytz,base64
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_day_dob(self):
        lst = []
        for i in range(31):
            lst.append((str(i+1), i+1))
        return lst

    dob_month = fields.Selection([('January', 'January'), ('February', 'February'), ('March', 'March'),
                                             ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'),
                                               ('August', 'August'), ('September', 'September'), ('October', 'October')
                                                  , ('November', 'November'), ('December', 'December')],
                                            string='Birth Month')
    dob_day = fields.Selection(get_day_dob, string='Birth day')