from odoo import api, fields, models

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    # overridden from addons to resolve the error
    @api.multi
    def _compute_recruitment_stats(self):
        job_data = self.env['hr.job'].read_group(
            [('department_id', 'in', self.ids)],
            ['no_of_hired_employee', 'department_id'], ['department_id'])
        new_emp = dict((data['department_id'][0], data['no_of_hired_employee']) for data in job_data)
        # expected_emp = dict((data['department_id'][0], data['no_of_recruitment']) for data in job_data)
        job_department_data = self.env['hr.job'].search([('department_id','=',self.ids)])
        for department in self:
            department.new_hired_employee = new_emp.get(department.id, 0)
            # department.expected_employee = expected_emp.get(department.id, 0)
            department.expected_employee = sum(job_department_data.filtered(lambda r:r.department_id == department).mapped('no_of_recruitment'))