from odoo import models, fields, api
from odoo.exceptions import ValidationError



class HrPayslipProfTax(models.Model):
	_name = 'hr_payslip_prof_tax'
	_description = "Professional Tax"

	state_id = fields.Many2one('res.country.state', 'State', domain="[('country_id.code', '=', 'IN')]")
	gross_from = fields.Float('Gross Range From')
	gross_to = fields.Float('Gross Range To')
	prof_monthly_deduct = fields.Float('Monthly Deduction')
	prof_last_month_deduct = fields.Float('Last Month Deduction')

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	@api.multi
	def _compute_payslip_count(self):
		to_date = fields.Date.today().replace(day=1)
		for employee in self:
			employee.payslip_count = len(employee.slip_ids.filtered(lambda x: x.date_to <= to_date))


	payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count', groups="base.group_user")

	def show_payslips(self):
		tree_view_id = self.env.ref('hr_payroll.view_hr_payslip_tree').id
		form_view_id = self.env.ref('hr_payroll.view_hr_payslip_form').id
		slip_visible_day = self.env['ir.config_parameter'].sudo().get_param('hr_payslip.slip_visible_day')
		if not slip_visible_day:
			raise ValidationError('Please set slip visible day in settings.')
		to_date = fields.Date.today().replace(day=int(slip_visible_day))
		return {
				'type': 'ir.actions.act_window',
				'views': [(tree_view_id, 'tree'), (form_view_id,'form')],
				'view_mode': 'tree,form',
				'view_type': 'form',
				'name': ('Payslips'),
				'res_model': 'hr.payslip',
				'domain':[('date_to', '<=', to_date)],
				'context': {'search_default_employee_id': [self.id], 'default_employee_id': self.id},
				'target': 'main',
			}