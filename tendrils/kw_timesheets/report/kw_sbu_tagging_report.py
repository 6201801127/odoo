from odoo import models, fields, api, tools
from datetime import date


class TimesheetSbuTagReport(models.Model):
    _name = "kw_sbu_tagging_report"
    _description = "Timesheet SBU taging report Summary"
    _auto = False
    
    employee_name = fields.Char("Employee Name")
    department = fields.Char("Department")
    designation = fields.Char('Designation')
    sbu_name = fields.Char('SBU Name')
    project_tag_status = fields.Boolean('Project Tag Status')
    employee_code =  fields.Char('Employee Code')
    



    @api.model_cr
    def init(self):
        self.env.cr.execute("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")

        tools.drop_view_if_exists(self.env.cr, self._table)
        view_query = f"""CREATE OR REPLACE VIEW {self._table} AS (
            select emp.id,emp.emp_code as employee_code,emp.name as employee_name, d.name as department,j.name as designation, emp.sbu_master_id as sbu_id,sbu.name as sbu_name,
            (select active from kw_project_resource_tagging where emp_id = emp.id  and active = True limit 1) as project_tag_status from hr_employee emp
            left join hr_department d on d.id = emp.department_id
            left join hr_job j on emp.job_id = j.id
            left join kw_sbu_master sbu on emp.sbu_master_id =sbu.id
            where emp.active = True and
            emp.sbu_type in ('sbu', 'horizontal')
            )
        """
        self.env.cr.execute(view_query)



   