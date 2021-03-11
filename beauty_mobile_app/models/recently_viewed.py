from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class WebsiteRecentlyViewed(models.Model):
    _name = 'website.recently.viewed'
    _description = 'Website Recently Viewed'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Customer',required=True, domain=[('customer', '=', True)])
    recently_viewed_line = fields.One2many('website.recently.viewed.line', 'recently_viewed_id',
                                           string='Recently Viewed Lines', copy=True)


class WebsiteRecentlyViewedLine(models.Model):
    _name = 'website.recently.viewed.line'
    _description = 'Website Recently Viewed Line'
    _rec_name = 'product_id'

    recently_viewed_id = fields.Many2one('website.recently.viewed', string='Recently Viewed Reference', required=True,
                                         ondelete='cascade', copy=False)
    date_order = fields.Datetime(string='Date', required=True, copy=False, default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', string='Product', required=True)
