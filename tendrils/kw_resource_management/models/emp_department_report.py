from odoo import models, fields, api
from odoo import tools


class EmpDepartment(models.Model):
    _name = "employee_deparment_count_report"
    _description = "Employee Department Count Report "
    _auto = False
    
    department_id = fields.Many2one('hr.department', string="Department")
    emp_role = fields.Many2one('kwmaster_role_name',string="Employee Role")
    total_no = fields.Integer(string="Total No")
    
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT max( hr.id) AS id,
            max(pp.id) as department_id, 
            count(hr.id) as total_no,
			max(rl.id) as emp_role 
            from hr_employee as hr
            left join kwmaster_role_name as rl on hr.emp_role = rl.id
            left join hr_department as pp on hr.department_id = pp.id
            group by pp.id

        )"""
        self.env.cr.execute(query)