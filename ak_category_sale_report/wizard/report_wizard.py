from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import base64


class ProductCategoryReport(models.TransientModel):
	_name = 'product.category.report'

	start_date = fields.Date(required=True, default=fields.Date.context_today)
	end_date = fields.Date(required=True, default=fields.Date.context_today)
	is_detailed = fields.Boolean('Detailed')
	product_type = fields.Selection([('consu', 'Consumable'),('service', 'Service'),('product', 'Retail')],
							string='Type')
	owner_email = fields.Char(string='Owner Email')

	@api.multi
	def generate_report(self):
		data = {'date_start': self.start_date, 'date_stop': self.end_date, 'is_detailed':self.is_detailed,
				'product_type':self.product_type}
		return self.env['report'].get_action([], 'ak_category_sale_report.category_sale_report', data=data)

	@api.multi
	def email_report(self):
		to_email = self.owner_email
		if not to_email:
			raise UserError(_("Enter Email Id."))
		data = {'date_start': self.start_date, 'date_stop': self.end_date, 'is_detailed': self.is_detailed,
				'product_type': self.product_type}
		pdf = self.env['report'].get_pdf([], 'ak_category_sale_report.category_sale_report', data=data)
		start_date = self.start_date
		end_date = self.end_date
		attachment_id = self.env['ir.attachment'].create({
			'name': 'Category Sales Report: ' + str(start_date) + " To " + str(end_date),
			'type': 'binary',
			'datas': base64.encodestring(pdf),
			'datas_fname': 'Category Sales Report.pdf',
			'mimetype': 'application/x-pdf'
		})
		mail_values = {
			# 'email_from': to_email,
			'reply_to': to_email,
			'email_to': to_email,
			'subject': 'Category Sales Report: ' + str(start_date) + ' To ' + str(end_date),
			'body_html': """<div>
								<p>Hello,</p>
								<p>This email was created automatically by Odoo Beauty Manager. Please find the attached Category Sales Report.</p>
							</div>
							<div>Thank You</div>""",
			'attachment_ids': [(4, attachment_id.id)]
		}
		result = self.env['mail.mail'].create(mail_values).send()
		if result:
			message = "Category Sales Report is sent by Mail !!"
			self.env.user.notify_info(message, title='Email Sent', sticky=False)


class ReportProductCategory(models.AbstractModel):
	_name = 'report.ak_category_sale_report.category_sale_report'

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
		product_category = []
		count_list = []
		order_list = []
		for rec in order_lines:
			if rec.order_id not in order_list:
				order_list.append(rec.order_id)
			if rec.product_id.pos_categ_id not in product_category:
				pro_categ = rec.product_id.pos_categ_id
				product_category.append(pro_categ)
		for order_here in order_list:
			if order_here.partner_id:
				if order_here.partner_id not in clients_list:
					clients_list.append(order_here.partner_id)
			else:
				no_clients_added += 1
		for categ in product_category:
			total_sale_amount = 0.0
			total_sales = 0.0
			list_order_lines = []
			for ord_line in order_lines:
				if categ == ord_line.product_id.pos_categ_id:
					total_sale_amount += (ord_line.qty * ord_line.price_unit)
					total_sales += 1
					list_order_lines.append(ord_line)
			if not categ:
				categ = 'Others'
			else:
				categ = categ.name
			count_list.append({ 'category' : categ,
								'total_sale_amount':total_sale_amount,
								'total_sales':total_sales,
								'list_order_lines':list_order_lines,
								})
		categ_list = {
					'count_list': sorted(count_list, key=lambda i: i['category']),
					'date_start': date_start,
					'date_stop' : date_stop,
					'is_detailed' : is_detailed,
					'product_type' : product_type,
					'product_type_name' : product_type_name,
					'clients_count' : len(clients_list)+ no_clients_added ,
					'remove_total_old_advance' : remove_total_old_advance ,
					'add_total_today_advance_amt' : add_total_today_advance_amt ,
					}
		return categ_list

	@api.multi
	def render_html(self, docids, data=None):
		data = dict(data or {})
		result = self.get_sale_details(data['date_start'], data['date_stop'], data['is_detailed'], data['product_type'])
		data.update(result)
		return self.env['report'].render('ak_category_sale_report.category_sale_report', data)