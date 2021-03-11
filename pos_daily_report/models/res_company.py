from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
from email.utils import formataddr
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    owner_email = fields.Char(string='Owner Email')


class Message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _get_default_from(self):
        if self.env.user.email:
            return formataddr(("Beauty Manager", self.env.user.email))
            # return formataddr((self.env.user.name, self.env.user.email))
        raise UserError(_("Unable to send email, please configure the sender's email address."))

    email_from = fields.Char(
        'From', default=_get_default_from,
        help="Email address of the sender. This field is set when no matching partner is found and replaces the author_id field in the chatter.")


