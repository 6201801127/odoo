from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.http import request


class res_users(models.AbstractModel):
    _inherit = 'res.users'

    def _get_employee_code(self):
        for user in self:
            records = self.env['hr.employee'].search([('user_id', '=', user.id)])
            if records:
                user.emp_code = records[0].emp_code
                user.emp_job_id = records[0].job_id.id if records[0].job_id else False
                user.emp_department_id = records[0].department_id.id if records[0].department_id else False

    # emp_id            = fields.One2many('hr.employee', 'user_id', string="Employee Code")
    # emp_code          = fields.Char(related='emp_id.emp_code', store=True)
    emp_code = fields.Char('Employee Code', compute='_get_employee_code')
    emp_job_id = fields.Many2one('hr.job', string='Designation', compute='_get_employee_code')
    emp_department_id = fields.Many2one('hr.department', string='Department', compute='_get_employee_code')
