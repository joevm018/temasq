from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz
from odoo import SUPERUSER_ID


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.depends('lines')
    def _compute_display_name(self):
        for order in self:
            name_string = ""
            if order.name:
                name_string = name_string + "Order:" + order.name
            if order.lines:
                for line in order.lines:
                    if line.product_id.type == 'service':
                        name_string = name_string + ","
                        name_string = name_string + line.product_id.name
                    if line.staff_assigned_id:
                        name_string = name_string + "--" + line.staff_assigned_id.name
                    if line.room_id:
                        name_string = name_string + "--" + line.room_id.name
            order.display_name = name_string

    @api.onchange('lines')
    def check_room_availability(self):
        pos_obj = self.env['pos.order.line']
        for order in self:
            for line in order.lines:
                if line.room_id and line.procedure_start and line.procedure_stop:
                    line_procedure_stop = datetime.strptime(line.procedure_stop, '%Y-%m-%d %H:%M:%S')
                    line_procedure_stop = line_procedure_stop - timedelta(minutes=5)
                    line_procedure_stop = line_procedure_stop.strftime('%Y-%m-%d %H:%M:%S')
                    line_procedure_start = datetime.strptime(line.procedure_start, '%Y-%m-%d %H:%M:%S')
                    line_procedure_start = line_procedure_start + timedelta(minutes=5)
                    line_procedure_start = line_procedure_start.strftime('%Y-%m-%d %H:%M:%S')
                    pos_search = pos_obj.search([('room_id', '=', line.room_id.id)])
                    for record in pos_search:
                        if record.procedure_start <= line_procedure_start <= record.procedure_stop:
                            msg = line.room_id.name + ' is not available at the selected time.'
                            line.room_id = False
                            warning = {
                                'title': ' Warning !!!',
                                'message': msg
                            }
                            return {'warning': warning}
                        elif record.procedure_start <= line_procedure_stop <= record.procedure_stop:
                            msg = line.room_id.name + ' is not available at the selected time.'
                            line.room_id = False
                            warning = {
                                'title': ' Warning !!!',
                                'message': msg
                            }
                            return {'warning': warning}
                        elif line_procedure_start <= record.procedure_start and record.procedure_stop <= line_procedure_stop:
                            msg = line.room_id.name + ' is not available at the selected time.'
                            line.room_id = False
                            warning = {
                                'title': ' Warning !!!',
                                'message': msg
                            }
                            return {'warning': warning}


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    room_id = fields.Many2one('salon.room', 'Room')

    @api.onchange('product_id')
    def onchange_procedure_id(self):
        if not self.product_id:
            self.room_id = False
