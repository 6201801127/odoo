from odoo import models, fields, api, tools
from datetime import date


class ProjectTasknotAssignReport(models.Model):
    _name = "kw_project_task_not_assign_report"
    _description = "Timesheet Project not Task Assign Summary"
    _auto = False
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    project_id = fields.Many2one('project.project',string="Project Name")
    code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(related='employee_id.name', string='Employee Name')
    designation =fields.Char(related='employee_id.job_id.name', string='Designation')
    date_of_joining = fields.Date(related='employee_id.date_of_joining',string='Date of Joining')
    emp_role = fields.Many2one('kwmaster_role_name', string='Employee Role')
    emp_category = fields.Char(related='employee_id.emp_category.name', string='Employee Category')
    employement_type = fields.Char(related='employee_id.employement_type.name', string='Employment Type')
    sbu_type = fields.Selection(
        string='SBU Type',
        selection=[('sbu', 'Vertical'), ('horizontal', 'Horizontal'), ('none', 'None')])
    # job_branch_id =fields.Char(related='employee_id.job_branch_id.name', string='Location')
    department_id=fields.Char(related='employee_id.department_id.name', string='Department Name')
    # practise_id = fields.Many2one('hr.department', string='Practice')
    # task_planning_start_date = fields.Date(string='Task Planning Date')
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # print("***** Called *****")
        to_date = 'to_date' in self._context and self._context['to_date'] or date.today()
        project_id = 'project_id' in self._context and self._context['project_id']
        sbu_type = 'sbu_type' in self._context and self._context['sbu_type']
        if to_date and project_id and sbu_type:
            self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select row_number() over(order by e.id desc) AS id,rt.emp_id as employee_id,e.emp_role AS emp_role,e.sbu_type,rt.project_id as project_id
            from kw_project_resource_tagging rt  join hr_employee e on e.id = rt.emp_id 
            where rt.project_id = {project_id.id} and rt.active=true and e.sbu_type = '{sbu_type}' and rt.emp_id not in
            (select a.assigned_employee_id from project_task a join hr_employee e on a.assigned_employee_id = e.id  where e.sbu_type = '{sbu_type}' 
            and planning_start_date <= '{to_date}' and planning_end_date >= '{to_date}')

                )""" % (self._table))

   