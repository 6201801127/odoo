from odoo import models, fields, api
from odoo import tools


class ProjectReport(models.Model):
    _name = "employee_count_report_project"
    _description = "Employee Count Report Project"
    _auto = False
    
    project_id = fields.Many2one('project.project', string="Project")
    project_stage = fields.Char(string="Project Stage")
    employee_count = fields.Integer(string="At Present")
    
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT row_number() over() AS id,
            pp.id as project_id, 
            count(hr.id) as employee_count,
            '' as project_stage
            from project_project as pp
            left join crm_lead as cl on pp.crm_id = cl.id
            left join hr_employee as hr on hr.emp_project_id = cl.id
            group by pp.id

        )"""
        self.env.cr.execute(query)