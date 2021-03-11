from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class PackageDetailsReport(models.TransientModel):
	_name = 'package.details.report'

	start_date = fields.Date(default=fields.Date.context_today)
	end_date = fields.Date(default=fields.Date.context_today)
	partner_id = fields.Many2one('res.partner', string="Customer")
	is_detailed = fields.Boolean('Detailed')
	package_type = fields.Selection([('purchased', 'Purchased details'), ('redeemed', 'Redeemed details'),
									 ('both', 'Purchased and Redeemed details')], string='Type',required=True,
									default='both')

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
		partner_id = False
		if self.partner_id:
			partner_id = [self.partner_id.id, self.partner_id.name]
		data = {'date_start': self.start_date, 'date_stop': self.end_date, 'partner_id':partner_id,
				'is_detailed': self.is_detailed, 'package_type': self.package_type}
		return self.env['report'].get_action([], 'report_package_details.package_details_report', data=data)


class ReportPackageDetails(models.AbstractModel):
	_name = 'report.report_package_details.package_details_report'

	@api.model
	def get_package_details(self, date_start=False, date_stop=False, partner_id=False, is_detailed=False,
							package_type=False):
		package_type_name = ''
		dom_purchased = [('package_card_id', '!=', False)]
		dom_redeemed = [('package_card_id', '!=', False)]
		if package_type == 'purchased':
			package_type_name = 'Purchased details'
			dom_purchased.append(('state', 'in', ['draft', 'done']))
			dom_redeemed.append(('state', 'in', ['draft', 'done']))
		elif package_type == 'redeemed':
			package_type_name = 'Redeemed details'
			dom_purchased.append(('state', '=', 'done'))
			dom_redeemed.append(('state', '=', 'done'))
		else:
			dom_purchased.append(('state', 'in', ['draft', 'done']))
			dom_redeemed.append(('state', 'in', ['draft', 'done']))
			package_type_name = 'Purchased and Redeemed details'
		if partner_id:
			dom_purchased.append(('customer_id', '=', partner_id[0]))
			dom_redeemed.append(('customer_id', '=', partner_id[0]))
		if date_start:
			now_date_start_obj = datetime.strptime(date_start, '%Y-%m-%d')
			now_ord_date_start = now_date_start_obj.strftime("%Y-%m-%d 00:00:00")
			# now_ord_date_start = datetime.strptime(now_ord_date_start, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
			dom_purchased.append(('package_card_id.purchased_date', '>=', str(now_ord_date_start)))
			dom_redeemed.append(('redeemed_date', '>=', str(now_ord_date_start)))
		if date_stop:
			now_date_end_obj = datetime.strptime(date_stop, '%Y-%m-%d')
			now_ord_date_stop = now_date_end_obj.strftime("%Y-%m-%d 23:59:59")
			# now_ord_date_stop = datetime.strptime(now_ord_date_stop, '%Y-%m-%d %H:%M:%S') - timedelta(hours=3)
			dom_purchased.append(('package_card_id.purchased_date', '<=', str(now_ord_date_stop)))
			dom_redeemed.append(('redeemed_date', '<=', str(now_ord_date_stop)))
		if package_type == 'purchased':
			purchased_combo_session_lines = self.env['combo.session'].search(dom_purchased)
			combo_session_lines = purchased_combo_session_lines
		elif package_type == 'redeemed':
			redeemed_combo_session_lines = self.env['combo.session'].search(dom_redeemed)
			combo_session_lines = redeemed_combo_session_lines
		else:
			purchased_combo_session_lines = self.env['combo.session'].search(dom_purchased)
			redeemed_combo_session_lines = self.env['combo.session'].search(dom_redeemed)
			combo_session_lines = purchased_combo_session_lines + redeemed_combo_session_lines
		partner_name = ''
		if partner_id:
			partner_name = partner_id[1]
		card_lines_list = []
		for comb_lines in combo_session_lines:
			if comb_lines not in card_lines_list:
				card_lines_list.append(comb_lines)
		card_list = []
		for i in card_lines_list:
			if i.package_card_id not in card_list:
				card_list.append(i.package_card_id)
		emp_list = {
					'combo_session_lines': card_lines_list,
					'card_list': card_list,
					'date_start': date_start,
					'date_stop' : date_stop,
					'partner_name' : partner_name,
					'is_detailed' : is_detailed,
					'package_type_name' : package_type_name,
					}
		return emp_list

	@api.multi
	def render_html(self, docids, data=None):
		data = dict(data or {})
		result = self.get_package_details(data['date_start'], data['date_stop'], data['partner_id'],
										  data['is_detailed'], data['package_type'])
		data.update(result)
		return self.env['report'].render('report_package_details.package_details_report', data)