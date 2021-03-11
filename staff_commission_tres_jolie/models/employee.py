from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    target = fields.Float('Target Amount')
    target_ids = fields.One2many('target.slab', 'employee_id', 'Commission details')

    def compute_employee_income(self, options):
        """
        Computes the total income of the employee for the period
        :param options:
        :return: service_income, retail_income
        """
        orders = self.env['pos.order'].search([
            ('date_order', '>=', options['date_from']),
            ('date_order', '<=', options['date_to']),
            ('state', 'in', ['paid', 'invoiced', 'done'])])
        profit = 0
        referral = 0
        item_income = 0

        all_lines = orders.mapped('lines')
        service_lines = all_lines.filtered(
            lambda l: l.product_id.type == 'service')
        item_lines = all_lines.filtered(
            lambda l: l.product_id.type != 'service')
        for line in service_lines:
            if self.id == line.staff_assigned_id.id:
                profit += line.after_global_disc_subtotal
            if self.id == line.referral_staff_id.id:
                referral += line.after_global_disc_subtotal

        for line in item_lines:
            if self.id == line.staff_assigned_id.id:
                item_income += line.after_global_disc_subtotal

        referral = (referral * self.referral_percent) / 100
        return profit, referral, item_income

    def _compute_total_commission(self, service_income, retail_income):
        retail_commission = 0
        item_commission = self.env['ir.values'].get_default(
            'pos.config.settings', "default_item_commission")
        item_commission = item_commission and item_commission or 10
        retail_commission += (retail_income * item_commission) / 100

        service_commission = 0
        profit_percent = service_income * 100 / self.target
        targ_obj1 = targ_obj2 = targ_obj3 = False
        for commission in self.target_ids:
            achieved_from = commission.achieved_from
            achieved_to = commission.achieved_to
            c_between = achieved_from <= profit_percent <= achieved_to
            c_last = achieved_from <= profit_percent and not achieved_to
            c_first = not achieved_from and profit_percent <= achieved_to
            if c_last:
                targ_obj1 = commission
            elif c_between:
                targ_obj2 = commission
            elif c_first:
                targ_obj3 = commission
        commission_type = self.env['ir.values'].get_default(
            'pos.config.settings', "default_commission_type")
        commission_type = commission_type and commission_type or "fixed"
        commission = 0
        achieved_from = 0
        achieved_to = 0
        if commission_type == 'percentage':
            if targ_obj1:
                achieved_from = targ_obj1.achieved_from
                achieved_to = targ_obj1.achieved_to
                commission = targ_obj1.commission
            elif targ_obj2:
                achieved_from = targ_obj2.achieved_from
                achieved_to = targ_obj2.achieved_to
                commission = targ_obj2.commission
            elif targ_obj3:
                achieved_from = targ_obj3.achieved_from
                achieved_to = targ_obj3.achieved_to
                commission = targ_obj3.commission
            service_commission = service_income * commission / 100
        else:
            if targ_obj1:
                achieved_from = targ_obj1.achieved_from
                achieved_to = targ_obj1.achieved_to
                commission = targ_obj1.commission_fixed
            elif targ_obj2:
                achieved_from = targ_obj2.achieved_from
                achieved_to = targ_obj2.achieved_to
                commission = targ_obj2.commission_fixed
            elif targ_obj3:
                achieved_from = targ_obj3.achieved_from
                achieved_to = targ_obj3.achieved_to
                commission = targ_obj3.commission_fixed
            service_commission = commission
        return {
            'profit_percent': profit_percent,
            'commission': service_commission + retail_commission,
            'achieved_from': achieved_from,
            'achieved_to': achieved_to,
        }

    def compute_total_commission(self, options):
        """
        computes total commission of the employee for the period
        :param options:
        :return:
        """
        service_income, referral_income, retail_income = self.compute_employee_income(options)
        service_income += referral_income
        commission_final = 0
        if self.target > 0:
            commission_final += self._compute_total_commission(
                service_income, retail_income)['commission']
        return commission_final
