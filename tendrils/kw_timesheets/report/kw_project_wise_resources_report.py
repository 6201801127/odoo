from odoo import models, fields, api, tools
from datetime import date


class ProjectwiseResourceReport(models.Model):
    _name = "kw_project_resource_report"
    _description = "Timesheet Project Resource taging report"
    _auto = False
    
    # project_name = fields.Char("Project Name")
    employee_name = fields.Char("Employee Name")
    employee_code = fields.Char("Employee Code")
    department = fields.Char("Department")
    designation = fields.Char('Designation')
    employee_id     = fields.Many2one('hr.employee', string="Employee")
    project_id        = fields.Many2one('project.project', string="Project")
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # print("***** Called *****")
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select 	rt.id,rt.project_id,
            p.active as active_project,
            rt.emp_id as employee_id,
            emp.emp_code as employee_code,
            emp.name as employee_name,
            d.name as department,
            j.name as designation
            
            from kw_project_resource_tagging rt
            join project_project p on p.id = rt.project_id
            left join hr_employee emp on emp.id = rt.emp_id
            left join hr_department d on d.id = emp.department_id
            left join hr_job j on emp.job_id = j.id
            
            where rt.active = True and p.active = True
            order by p.name asc
            )""" % (self._table))
   