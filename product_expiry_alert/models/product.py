from odoo import api, fields, models, tools, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    with_expiry = fields.Boolean("With expiry Date ?")

    @api.onchange('with_expiry')
    def onchange_with_expiry(self):
        for pdt in self:
            if pdt.with_expiry:
                pdt.tracking = 'lot'
            else:
                pdt.tracking = 'none'


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    expiry_alert = fields.Boolean(compute='_compute_expiry', store=True)
    life_date = fields.Datetime(string='Expiry Date',
                                help='This is the date on which the goods with this Serial Number may become dangerous and must not be consumed.')

    @api.model
    @api.depends('life_date', 'alert_date', 'product_qty')
    def _compute_expiry(self):
        for lot in self:
            today_date = fields.date.today()
            if lot.life_date and lot.product_qty > 0:
                life_date = datetime.strptime(lot.life_date, '%Y-%m-%d %H:%M:%S').date()
                if today_date >= life_date:
                    lot.expiry_alert = True
                else:
                    lot.expiry_alert = False
                    ir_values_obj = self.env['ir.values']
                    expiry_day = False
                    if lot.product_id.type == 'product':
                        expiry_day = ir_values_obj.get_default('pos.config.settings',
                                                               'expiry_day')
                    elif lot.product_id.type == 'consu':
                        expiry_day = ir_values_obj.get_default('pos.config.settings',
                                                               'consu_expiry_day')
                    if not expiry_day:
                        expiry_day = 30
                    alert_date = life_date - relativedelta(days=expiry_day)
                    if today_date >= alert_date:
                        lot.expiry_alert = True
            else:
                lot.expiry_alert = False

    @api.onchange('life_date')
    def onchange_lifedate(self):
        for lot in self:
            if lot.life_date:
                life_date = datetime.strptime(lot.life_date, '%Y-%m-%d %H:%M:%S')
                ldate = life_date.strftime('%d/%m/%Y')
                lot.name = str(ldate)

    def _expiry_product_alert(self):
        pdts = []
        today_date = fields.date.today()
        ir_values_obj = self.env['ir.values']
        expiry_day = ir_values_obj.get_default('pos.config.settings',
                                               'expiry_day')
        consu_expiry_day = ir_values_obj.get_default('pos.config.settings',
                                               'consu_expiry_day')
        for lot in self.env['stock.production.lot'].search([('product_qty', '>', 0),
                                                            ('product_id.type', '=', 'product')]):
            if lot.life_date and lot.product_qty > 0:
                life_date = datetime.strptime(lot.life_date, '%Y-%m-%d %H:%M:%S').date()
                if today_date >= life_date:
                    lot.expiry_alert = True
                    pdts.append(lot)
                else:
                    alert_date = life_date - relativedelta(days=expiry_day)
                    if today_date >= alert_date:
                        lot.expiry_alert = True
                        pdts.append(lot)
            else:
                lot.expiry_alert = False
        for lot in self.env['stock.production.lot'].search([('product_qty', '>', 0),
                                                            ('product_id.type', '=', 'consu')]):
            if lot.life_date and lot.product_qty > 0:
                lot.expiry_alert = True
                life_date = datetime.strptime(lot.life_date, '%Y-%m-%d %H:%M:%S').date()
                if today_date >= life_date:
                    lot.expiry_alert = True
                    pdts.append(lot)
                else:
                    alert_date = life_date - relativedelta(days=consu_expiry_day)
                    if today_date >= alert_date:
                        lot.expiry_alert = True
                        pdts.append(lot)
            else:
                lot.expiry_alert = False
        if pdts:
            message = "Near expiry/expired items:   "
            count = 0
            for i in pdts:
                if count == 0:
                    message += " " + i.product_id.name + " (" + str(i.product_qty) + " units)"
                    count = 1
                else:
                    message += ", " + i.product_id.name + " (" + str(i.product_qty) + " units)"
            self.env.user.notify_warning(message, title='Expiry Notification !!!', sticky=True)
