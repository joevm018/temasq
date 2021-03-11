from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta



class StaffSummaryReport(models.TransientModel):
	_name = 'staff.summary.report'

	start_date = fields.Date(required=True, default=fields.Date.context_today)
	end_date = fields.Date(required=True, default=fields.Date.context_today)
	is_detailed = fields.Boolean('Detailed')
	product_type = fields.Selection([('consu', 'Consumable'),('service', 'Service'),('product', 'Retail')],
							string='Type')

	@api.multi
	def generate_report(self):
		data = {'date_start': self.start_date, 'date_stop': self.end_date, 'is_detailed':self.is_detailed,
				'product_type':self.product_type}
		return self.env['report'].get_action([], 'report_staff_summary.staff_summary_report', data=data)


class ReportStaffSummary(models.AbstractModel):
	_name = 'report.report_staff_summary.staff_summary_report'

	@api.model
	def get_sale_details(self, date_start=False, date_stop=False, is_detailed=False, product_type=False):
		product_type_name = False
		if product_type == 'consu':
			product_type_name = 'Consumable'
		if product_type == 'service':
			product_type_name = 'Service'
		if product_type == 'product':
			product_type_name = 'Retail'

		d_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
		d_date_stop = datetime.strptime(date_stop, '%Y-%m-%d').date()
		days_dif = (d_date_stop - d_date_start).days
		days_list = []
		for i in range(days_dif + 1):
			day = d_date_start + timedelta(days=i)
			days_list.append(str(day))
		add_total_today_advance_amt = 0.0
		remove_total_old_advance = 0.0
		for each_days in days_list:
			date_start_obj = datetime.strptime(each_days, '%Y-%m-%d')
			date_end_obj = datetime.strptime(each_days, '%Y-%m-%d')
			ord_date_start = date_start_obj.strftime("%Y-%m-%d 00:00:00")
			ord_date_stop = date_end_obj.strftime("%Y-%m-%d 23:59:59")
			ord_date_start = datetime.strptime(ord_date_start, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
			ord_date_stop = datetime.strptime(ord_date_stop, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
			adv_payment_search = [('date', '=', each_days), ('is_advance', '=', True)]
			advance_payments = self.env['account.bank.statement.line'].search(adv_payment_search)
			add_advance_amt = 0.0
			for adv_statement in advance_payments:
				add_advance_amt += adv_statement.amount
			add_total_today_advance_amt += add_advance_amt

			lst_search = [('date_order', '>=', str(ord_date_start)), ('date_order', '<=', str(ord_date_stop)),
						  ('state', 'in', ['paid', 'invoiced', 'done'])]
			normal_orders = self.env['pos.order'].search(lst_search)
			old_adv_remove = 0.0
			for pos_order in normal_orders:
				for statem in pos_order.statement_ids.filtered(lambda s: s.is_advance == True and s.date != each_days):
					old_adv_remove += statem.amount
			remove_total_old_advance += old_adv_remove

		now_date_start_obj = datetime.strptime(date_start, '%Y-%m-%d')
		now_date_end_obj = datetime.strptime(date_stop, '%Y-%m-%d')
		now_ord_date_start = now_date_start_obj.strftime("%Y-%m-%d 00:00:00")
		now_ord_date_stop = now_date_end_obj.strftime("%Y-%m-%d 23:59:59")
		now_ord_date_start = datetime.strptime(now_ord_date_start, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
		now_ord_date_stop = datetime.strptime(now_ord_date_stop, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
		order_ids = self.env['pos.order'].search([('date_order', '>=', str(now_ord_date_start)),
			('date_order', '<=', str(now_ord_date_stop)),('state','in',('paid','done','invoiced'))])
		order_lines = []
		clients_list = []
		no_clients_added = 0
		for order in order_ids:
			for line  in order.lines:
				if (product_type and line.product_id.type == product_type) or not product_type:
					order_lines.append(line)
			if order.partner_id:
				if order.partner_id not in clients_list:
					clients_list.append(order.partner_id)
			else:
				no_clients_added += 1
		employee_list = []
		count_list = []
		for order_l in order_lines:
			if order_l.staff_assigned_id not in employee_list:
				employee = order_l.staff_assigned_id
				employee_list.append(employee)
		total_package_sales = 0.0
		for emp in employee_list:
			total_staff_amount = 0.0
			total_staff_sales = 0.0
			total_staff_package_sales = 0.0
			total_staff_consumables = 0.0
			total_staff_retails = 0.0
			total_staff_services = 0.0
			list_order_lines = []
			for ord_line in order_lines:
				if emp == ord_line.staff_assigned_id:
					if ord_line.combo_session_id:
						order_amt = ord_line.combo_session_id.price
						total_staff_package_sales += order_amt
						total_staff_amount += order_amt
					else:
						order_amt = ord_line.qty * ord_line.price_unit
						total_staff_amount += order_amt
					total_staff_sales += 1
					if ord_line.product_id.type == 'consu':
						total_staff_consumables += order_amt
					if ord_line.product_id.type == 'product':
						total_staff_retails += order_amt
					if ord_line.product_id.type == 'service':
						total_staff_services += order_amt
					list_order_lines.append(ord_line)
			if not emp:
				emp = 'No Staff'
			else:
				emp = emp.name
			total_package_sales += total_staff_package_sales
			count_list.append({ 'employee' : emp,
								'total_staff_amount':total_staff_amount,
								'total_staff_package_sales':total_staff_package_sales,
								'total_staff_sales':total_staff_sales,
								'total_staff_consumables':total_staff_consumables,
								'total_staff_retails':total_staff_retails,
								'total_staff_services':total_staff_services,
								'list_order_lines':list_order_lines,
								})

		emp_list = {
					'total_package_sales': total_package_sales,
					'count_list': count_list,
					'date_start': date_start,
					'date_stop' : date_stop,
					'is_detailed' : is_detailed,
					'product_type_name' : product_type_name,
					'clients_count' : len(clients_list)+ no_clients_added ,
					'remove_total_old_advance' : remove_total_old_advance ,
					'add_total_today_advance_amt' : add_total_today_advance_amt ,
					}
		return emp_list




	@api.multi
	def render_html(self, docids, data=None):
		data = dict(data or {})
		result = self.get_sale_details(data['date_start'], data['date_stop'], data['is_detailed'], data['product_type'])
		data.update(result)
		return self.env['report'].render('report_staff_summary.staff_summary_report', data)