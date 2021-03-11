# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class ConsentLashes(models.Model):
    _name = 'consent.lashes'

    lash_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    consent_id = fields.Many2one('consent.facial', 'Consent')
    lash_length = fields.Char('Lash length & weight طول ووزن الرموش المستخدمة')
    adhesive = fields.Char('Adhesive used اللاصق المستخدم')
    comments = fields.Char('Special comments ( new installation or maintenance) ملاحظات خاصة: (تركيب جديد أو تصليح)')
