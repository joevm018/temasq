from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    badge_expiry_date = fields.Date('Badge Expiry Date')
    is_hair_consultation = fields.Boolean('Is Hair Consultation?')
    image_website = fields.Binary(string='Image', attachment=True)