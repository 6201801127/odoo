from odoo import api, fields, models,_
from datetime import date


class SendTdsReminder(models.TransientModel):
    _name = 'create.appraisal'
    _description = 'Send Reminder'

    @api.model
    def default_get(self, field_list):
        result = super(SendTdsReminder, self).default_get(field_list)
        todays_date = date.today()
        char_yr = str(todays_date.year)
        emp_contract = self.env['date.range'].search(
                    [('name', '=', char_yr)],limit=1)
        result['abap_period'] = emp_contract.id
        return result

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    abap_period = fields.Many2one('date.range', string='APAR Period')

    @api.onchange('abap_period')
    def _onchange_abap_period(self):
        todays_date = date.today()
        char_yr = str(todays_date.year)
        return {'domain': {'abap_period': [('type_id.name', '=', 'Calendar Year'),('name', '=', char_yr)]}}

    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        branches_all = self.env.user.branch_ids
        return {'domain': {'employee_ids': [('branch_id', '=', branches_all.ids )]}}

    def create_appraisal_action_button(self):
        for rec in self:
            for employee in rec.employee_ids:
                emp_contract = self.env['hr.contract'].search(
                    [('employee_id', '=', employee.id), ('state', '=', 'open')], limit=1)
                self.env['appraisal.main'].create({
                    'state': 'draft',
                    'employee_id': employee.id,
                    'abap_period': rec.abap_period.id,
                    'branch_id': employee.branch_id.id,
                    'category_id': employee.category.id,
                    'dob': employee.birthday,
                    'job_id': employee.job_id.id,
                    'struct_id': emp_contract.struct_id.id,
                    'pay_level_id': emp_contract.pay_level_id.id,
                    'pay_level': emp_contract.pay_level.id,
                    'template_id': emp_contract.pay_level_id.template_id.id,
                })