# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    consultation = fields.Integer('Consultation', compute='_compute_consultation')
    update_date = fields.Date('Update Date')
    f1 = fields.Char("1 -What is your main goal for today treatment ?")
    f2 = fields.Char("2-What is your skin care routine?")
    f3 = fields.Char("3 -what skin care products are you using?")
    f4 = fields.Char("4 -Are you Wearing Eyelashes?")
    f5 = fields.Selection([('yes', 'Yes'),
                           ('no', 'No')], 'Have you Ever your skin care had a facial before?')
    f51 = fields.Char("Notes")
    f6 = fields.Selection([('yes', 'Yes'),
                           ('no', 'No')], 'Do you have any special skin problems?')
    f61 = fields.Char("Notes")
    f7 = fields.Selection([('yes', 'Yes'),
                           ('no', 'No')], 'Have you ever take any chemical peels?')
    f71 = fields.Char("Notes")
    f8 = fields.Selection([('yes', 'Yes'),
                           ('no', 'No')], 'Have you even used an acne medicine?')
    f81 = fields.Char("Notes")
    f9 = fields.Selection([('break', 'Break out/Ache'),
                           ('black', 'Black/white Heads'),
                           ('dry', 'Dryness'),
                           ('relax', 'Relaxations')], 'What concern do you have regarding your skin?')
    f10 = fields.Boolean('Sensitivity')
    f11 = fields.Boolean('Eczema')
    f12 = fields.Boolean('Pigmentations')
    f13 = fields.Boolean('Melasma')
    f14 = fields.Boolean('Flabby Face')
    f15 = fields.Boolean('Burns')
    f16 = fields.Boolean('Pregnant')
    f17 = fields.Boolean('Acne')
    f18 = fields.Selection([
        ('Normal', 'Normalعادية'),
        ('Oily', 'Oily دهنية'),
        ('Dry', 'Dryجافة'),
        ('Mixed', 'Mixedمختلطة'),
        ('VeryDry', 'Very dryجافة جدا'),
        ('DrySensitive', 'Dry and sensitiveجافة و حساسة')], 'Skin typeنوع البشرة')
    f19 = fields.Selection([('yes', 'Yes'),
                            ('no', 'No')], string="Have you cleaned the skin?هل قمت بتنظيف البشرة؟")
    f20 = fields.Selection([('yes', 'Yes'),
                            ('no', 'No')], 'Have you peeling the skin?هل قمت بتقشير البشرة؟')
    f21 = fields.Selection([('yes', 'Yes'),
                            ('no', 'No')],
                           'Did you use sweetness, wax, or floss for the face? هل قمت باستخدام الحلاوة, الشمع او الخيط للوجه؟')
    f22 = fields.Selection([('yes', 'Yes'),
                            ('no', 'No')], 'Have you used face laser? هل قمت باستخدام الليزر للوجه؟')
    f23 = fields.Text("Treatment stages and steps مراحل العلاج و الخطوات")
    f24 = fields.Selection([('1session', '1 sessionجلسة واحدة'),
                            ('3session', '3 sessions3 جلسات'),
                            ('4session', '4 sessions4 جلسات'),
                            ('6session', '6 sessions5 جلسات')], 'Number of sessionsعدد الجلسات المقررة')
    f34 = fields.Char("Notes:ملاحظات: ")
    survey = fields.Selection([('word', 'Word of mouth'),
                               ('media', 'Social Media'),
                               ('walkby', 'Walk by'),
                               ('website', 'Our Website')], "How did you hear about us?")
    customer_signature = fields.Binary(string='Customer Signature')
    salon_signature = fields.Binary(string='Administrative Signature')

    @api.model
    def _compute_consultation(self):
        for customer in self:
            customer_ids = self.env['consent.facial'].search([('customer_id', '=', customer.id)])
            customer.consultation = len(customer_ids)

    def show_consultation(self):
        orders = []
        order_ids = self.env['consent.facial'].search([('customer_id', '=', self.id)])
        for ord in order_ids:
            orders.append(ord.id)
        action = self.env.ref('ssquared_consent_management.action_consent_facial_normal').read()[0]
        if orders:
            action['domain'] = [('id', 'in', orders)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
