from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    after_global_disc_subtotal = fields.Float(string='Total after global disc', compute='_after_global_disc_subtotal')

    @api.multi
    def _after_global_disc_subtotal(self):
        for order_line in self:
            # simply added this field. Taking same value of  price_subtotal_incl. modifying value in global discount module.
            # Also this field is used in 3 reports. can use this field instead on modifying parser functions
            order_line.after_global_disc_subtotal = round(order_line.price_subtotal_incl, 2)


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _compute_credit_cash_amt(self):
        for order in self:
            cash_amt = 0.0
            credit_amt = 0.0
            for statement in order.statement_ids:
                if statement.journal_id.type == 'cash':
                    cash_amt += statement.amount
                if statement.journal_id.type == 'bank':
                    credit_amt += statement.amount
            order.credit_amt = credit_amt
            order.cash_amt = cash_amt

    credit_amt = fields.Float('Card Amount', digits=dp.get_precision('Product Price'), compute='_compute_credit_cash_amt')
    cash_amt = fields.Float('Cash Amount', digits=dp.get_precision('Product Price'), compute='_compute_credit_cash_amt')