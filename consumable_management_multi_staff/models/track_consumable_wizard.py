# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class TrackConsumableWizard(models.TransientModel):
    _inherit = "track.consumable.wizard"
    _description = "Change Product Quantity"

    staff_ids = fields.Many2many('hr.employee', string='Employee')

    @api.multi
    def change_product_qty(self):
        """ Changes the Product Quantity by making a Physical Inventory. """
        Inventory = self.env['stock.inventory']
        consumption_obj = self.env['consumption.record']
        for wizard in self:
            product = wizard.product_id.with_context(location=wizard.location_id.id, lot_id=wizard.lot_id.id)
            line_data = wizard._prepare_inventory_line()

            if wizard.product_id.id and wizard.lot_id.id:
                inventory_filter = 'none'
            elif wizard.product_id.id:
                inventory_filter = 'product'
            else:
                inventory_filter = 'none'

            date_obj = datetime.strptime(wizard.date, DATE_FORMAT)
            date = date_obj.strftime("%Y-%m-%d 00:00:00")
            staff_ids = []
            for line in wizard.staff_ids:
                staff_ids.append(line.id)
            inventory = Inventory.create({
                'name': _('INV: %s') % tools.ustr(wizard.product_id.name),
                'filter': inventory_filter,
                'product_id': wizard.product_id.id,
                'location_id': wizard.location_id.id,
                'lot_id': wizard.lot_id.id,
                'date': date,
                'line_ids': [(0, 0, line_data)],
            })
            inventory.action_done()
            for i in inventory.move_ids:
                i.consumed = True
            consumption_obj.create({
                'name': self.env['ir.sequence'].next_by_code('consumption.record'),
                'product_id': wizard.product_id.id,
                'product_tmpl_id': wizard.product_tmpl_id.id,
                'product_variant_count': wizard.product_variant_count,
                'new_quantity': wizard.new_quantity,
                'lot_id': wizard.lot_id.id,
                'location_id': wizard.location_id.id,
                'barcode': wizard.barcode,
                'staff_ids': [(6, 0, staff_ids)],
                'user_id': self.env.uid,
                'note': wizard.note,
                'date': wizard.date,
                'inventory_id': inventory.id
            })
        return {'type': 'ir.actions.act_window_close'}
