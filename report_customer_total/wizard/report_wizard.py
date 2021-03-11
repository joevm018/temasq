from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta



class CustomerTotalReport(models.TransientModel):
	_name = 'customer.total.report'

	start_date = fields.Date(required=True, default=fields.Date.context_today)
	end_date = fields.Date(required=True, default=fields.Date.context_today)
	is_detailed = fields.Boolean('Detailed')

	@api.onchange('start_date')
	def _onchange_start_date(self):
		if self.start_date and self.end_date and self.end_date < self.start_date:
			self.end_date = self.start_date

	@api.onchange('end_date')
	def _onchange_end_date(self):
		if self.end_date and self.end_date < self.start_date:
			self.start_date = self.end_date

	@api.multi
	def generate_report(self):
		data = {'date_start': self.start_date, 'date_stop': self.end_date, 'is_detailed':self.is_detailed}
		return self.env['report'].get_action([], 'report_customer_total.customer_total_report', data=data)


class ReportCustomerTotal(models.AbstractModel):
	_name = 'report.report_customer_total.customer_total_report'

	@api.model
	def get_sale_details(self, date_start=False, date_stop=False, is_detailed=False):
		now_date_start_obj = datetime.strptime(date_start, '%Y-%m-%d')
		now_date_end_obj = datetime.strptime(date_stop, '%Y-%m-%d')
		now_ord_date_start = now_date_start_obj.strftime("%Y-%m-%d 00:00:00")
		now_ord_date_stop = now_date_end_obj.strftime("%Y-%m-%d 23:59:59")
		now_ord_date_start = datetime.strptime(now_ord_date_start, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
		now_ord_date_stop = datetime.strptime(now_ord_date_stop, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
		order_ids = self.env['pos.order'].search([('date_order', '>=', str(now_ord_date_start)),
			('date_order', '<=', str(now_ord_date_stop)),('state','in',('paid','done','invoiced'))])
		customer_list = []
		count_list = []
		for order in order_ids:
			if order.partner_id not in customer_list:
				customer = order.partner_id
				customer_list.append(customer)
		for customer in customer_list:
			total_cust_amount = 0.0
			total_cust_sales = 0.0
			list_order = []
			for order in order_ids:
				if customer == order.partner_id:
					total_cust_amount += order.amount_total
					total_cust_sales += 1
					list_order.append(order)
			customer_phone = ""
			if not customer:
				customer_name = 'No Customer'
			else:
				customer_name = customer.name
				customer_phone = customer.phone
			count_list.append({ 'customer' : customer_name,
								'customer_phone': customer_phone,
								'total_cust_amount':total_cust_amount,
								'total_cust_sales':total_cust_sales,
								'list_order':list_order,
								})
		customerr_list = {
					'count_list': sorted(count_list, key=lambda l: l['customer']),
					'date_start': date_start,
					'date_stop' : date_stop,
					'is_detailed' : is_detailed,
					}
		return customerr_list

	@api.multi
	def render_html(self, docids, data=None):
		data = dict(data or {})
		result = self.get_sale_details(data['date_start'], data['date_stop'], data['is_detailed'])
		data.update(result)
		return self.env['report'].render('report_customer_total.customer_total_report', data)