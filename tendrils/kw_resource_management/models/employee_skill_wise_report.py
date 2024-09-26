from odoo import models, fields, api
from odoo import tools


class EmpSkillWiseReport(models.Model):
    _name = "employee_skill_wise_report"
    _description = "Skill Wise Report Of Employees"
    _auto = False

    skill_id = fields.Many2one('kw_skill_master',string = "Skill")
    employee_roll = fields.Many2one('kwmaster_role_name',string = "Employee Role")
    total_employee = fields.Integer(string = "Total Present")


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        query = f""" CREATE or REPLACE VIEW {self._table} as (
          
                SELECT row_number() over() AS id, 
            primary_skill_id as skill_id,
			emp_role as employee_roll,
            COUNT(id) as total_employee 
            FROM hr_employee
            GROUP BY primary_skill_id,emp_role
            
        )"""
        self.env.cr.execute(query)

