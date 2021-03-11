from odoo import api, fields, models, tools, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.combo_pack:
                pack = ''
                for i in record.pack_ids:
                    if pack == '':
                        pack += ' ' + str(i.count) + ' ' + i.product_id.name
                    else:
                        pack += '| ' + str(i.count) + ' ' + i.product_id.name
                if pack:
                    name = name + ' (' + pack + ')'

            if record.default_code:
                res.append((record['id'], '[%s] %s' % (record.default_code,name)))
            else:
                res.append((record['id'], "%s" % (name)))
        return res

#
# class ProductTemplate(models.Model):
#     _inherit = 'product.template'


