from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
import pytz
import base64


class BiStockMove(models.TransientModel):
	_name = 'stock.move.report'
	
	def _get_start_time(self):
		start_time = datetime.now()
		start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
		start_time = start_time - timedelta(hours=3)
		return start_time


	def _get_end_time(self):
		start_time = datetime.now()
		end_time = start_time.replace(hour=20, minute=59, second=59, microsecond=0)
		return end_time

	start_date = fields.Datetime(required=True, default=_get_start_time)
	end_date = fields.Datetime(required=True, default=_get_end_time)
	product_id = fields.Many2many('product.product', string="Product", domain=[('type', 'in', ['product', 'consu','service'])])
	

	
	@api.multi
	def generate_report(self):
		
		product_id = False
		list_product_id = []
		name_product_id = ""
		if self.product_id:
			for prod in self.product_id:
				list_product_id.append(prod.id)
				if name_product_id != "":
					name_product_id += ", "
				name_product_id += prod.name
			product_id = [list_product_id]
		data = {'date_start': self.start_date, 'date_stop': self.end_date, 'product_id': product_id}

		return self.env['report'].get_action([], 'ak_stock_move_report.stock_move_report', data=data)



class ReportStockTransfer(models.AbstractModel):
	_name = 'report.ak_stock_move_report.stock_move_report'

	@api.model
	def get_transfer_details(self, date_start=False, date_stop=False, product_id=False):
		product_list = []
		count_list = []

		if product_id:
			# move as per the given data
			move_ids = self.env['stock.move'].search([('date', '>=', date_start),
				('date', '<=', date_stop),('state','=','done'),('product_id','in',product_id[0])])

			if not move_ids:
				raise UserError(_('There is no Data to Display'))

		# appennding each product to a move_list
			
			for product in move_ids:
				if product.product_id not in product_list:
					product_list.append(product.product_id)
			
		# appending  counts 		
			for prod_id in product_list:
				total_sale_count = 0
				total_purchase_count = 0
				# current stock
				total_current_stock = prod_id.qty_available
				for product in move_ids:
					if prod_id.id == product.product_id.id:
						if product.location_dest_id.usage == 'customer' or product.picking_type_id.code == 'outgoing':
							total_sale_count += product.product_uom_qty
						if product.picking_type_id.code == 'incoming':
							total_purchase_count += product.product_uom_qty	

				count_list.append({ 'product' : prod_id.name,
									'total_sale_count':total_sale_count,
									'total_purchase_count':total_purchase_count,
									'total_current_stock':total_current_stock,
									})
				
				move_list = {	'date_start':date_start,
								'date_end':date_stop,
								'count_list': count_list,
								'product_list': product_list,
							 }

		else:
			# move as per the given data
			move_ids = self.env['stock.move'].search([('date', '>=', date_start),
		('date', '<=', date_stop),('state','=','done')])
			if not move_ids:
				raise UserError(_('There is no Data to Display'))

		# appennding each product to a move_list
			
			for product in move_ids:
				if product.product_id not in product_list:
					product_list.append(product.product_id)
			
		# appending  counts 		
			for prod_id in product_list:
				total_sale_count = 0
				total_purchase_count = 0
				# current stock
				total_current_stock = prod_id.qty_available
				for product in move_ids:
					if prod_id.id == product.product_id.id:
						if product.location_dest_id.usage == 'customer' or product.picking_type_id.code == 'outgoing':
							total_sale_count += product.product_uom_qty
						if product.picking_type_id.code == 'incoming':
							total_purchase_count += product.product_uom_qty	

		# return products





				count_list.append({ 'product' : prod_id.name,
									'total_sale_count':total_sale_count,
									'total_purchase_count':total_purchase_count,
									'total_current_stock':total_current_stock,
									})

				
				move_list = {	'date_start':date_start,
								'date_end':date_stop,
								'count_list': count_list,
								'product_list': product_list,
							 }


		return move_list



	@api.multi
	def render_html(self, docids, data=None):
		data = dict(data or {})
		result = self.get_transfer_details(data['date_start'],
										  data['date_stop'],
										  data['product_id'])
		data.update(result)

		return self.env['report'].render('ak_stock_move_report.stock_move_report', data)



	