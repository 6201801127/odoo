from odoo import models, fields, api


class Users(models.Model):
    _inherit = 'res.users'

    emp_code = fields.Char(compute='_get_employee_code', string='Employee Code')
    job_id = fields.Many2one('hr.job', compute='_get_employee_dept', string='Designation')
    dept_id = fields.Many2one('hr.department', compute='_get_employee_dept', string='Department')
    division_id = fields.Many2one('hr.department', compute='_get_employee_dept', string='Division')
    section_id = fields.Many2one('hr.department', compute='_get_employee_dept', string='Practise')
    practise_id = fields.Many2one('hr.department', compute='_get_employee_dept', string='Section')

    @api.model
    def _get_employee_dept(self):
        for user in self:
            records = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
            if records:
                user.dept_id = records.department_id.id
                user.division_id = records.division.id
                user.section_id = records.section.id
                user.practise_id = records.practise.id
                user.job_id = records.job_id.id

    @api.model
    def _get_employee_code(self):
        for user in self:
            records = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
            if records:
                user.emp_code = records.emp_code

    # @api.model
    # def _get_employee_job(self):
    #     for job in self:
    #         record = self.env['hr.employee'].sudo().search([('user_id', '=', job.id)])
    #         if record:
    #             job.job_id = record.job_id.name
