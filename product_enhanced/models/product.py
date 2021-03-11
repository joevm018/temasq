from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_nbr_reordering_rules(self):
        read_group_res = self.env['stock.warehouse.orderpoint'].read_group(
            [('product_id', 'in', self.ids)],
            ['product_id', 'product_min_qty', 'product_max_qty'],
            ['product_id'])
        res = {i: {} for i in self.ids}
        for data in read_group_res:
            res[data['product_id'][0]]['nbr_reordering_rules'] = int(data['product_id_count'])
            res[data['product_id'][0]]['reordering_min_qty'] = data['product_min_qty']
            res[data['product_id'][0]]['reordering_max_qty'] = data['product_max_qty']
        for product in self:
            product.nbr_reordering_rules = res[product.id].get('nbr_reordering_rules', 0)
            product.reordering_min_qty = res[product.id].get('reordering_min_qty', 0)
            product.reordering_max_qty = res[product.id].get('reordering_max_qty', 0)
            if product.qty_available < product.reordering_min_qty:
                product.min_alert = True
            else:
                product.min_alert = False

    min_alert = fields.Boolean(compute='_compute_nbr_reordering_rules', store=True)

    def _min_product_alert(self):
        pdts = []
        for pdt in self.env['product.template'].search([('type', '!=', 'service'), ('min_alert', '=', True)]):
            pdts.append(pdt.name)
        if pdts:
            message = "Low balance items:   "
            count = 0
            for i in pdts:
                if count == 0:
                    message += " " + i
                    count = 1
                else:
                    message += ", " + i
            self.env.user.notify_warning(message, title='Low Stock Alert !!!', sticky=True)


