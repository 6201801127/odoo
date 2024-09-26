from odoo import tools
from odoo import models, fields, api


class TimesheetReport(models.Model):
    _name = "kw_timesheet_report"
    _description = "Timesheet report Summary"
    _auto = False
    _rec_name = 'employee_name'

    # @api.depends('employee_id','project')
    # def check_project_tagged(self):
    #     for record in self:
    #         project_rec= self.env['project.project'].sudo().search([('name','=',record.project)])
    #         if project_rec:
    #             resouce_check=project_rec.resource_id.filtered(lambda x:x.emp_id.id == record.employee_id.id)
    #             if resouce_check:
    #                 record.project_tagged = True


    employee_id = fields.Many2one('hr.employee', 'Employee')
    project_id = fields.Many2one('project.project', 'Project')
    parent_id = fields.Many2one('hr.employee', 'Reporting Authority')
    employee_name = fields.Char(string='Employee Name', )
    dept_name = fields.Char(string='Department', )
    desg_name = fields.Char("Designation")
    division = fields.Char("Division")
    project = fields.Char("Project Name")
    category_name = fields.Char("Category Name")
    project_task = fields.Char("Activity")
    opportunity = fields.Char("Opportunity/Work Order")
    date = fields.Date("Date")
    desc = fields.Char("Description")
    effort_hour = fields.Float('Effort Hour')
    timesheet_effort = fields.Char("Timesheet Effort")
    location = fields.Char("Location")

    # active    = fields.Boolean('Active')
    # project_tagged = fields.Boolean(string='Tagged Employee',compute='check_project_tagged',search ='_search_employee_tagged_project')
    # tagging_employee = fields.Boolean(string='Tagged Project Start Employee',search ='_search_timesheet_tagged_project')

    # @api.multi
    # def _search_employee_tagged_project(self,operator,value):
    #     # print("method call")
    #     domain = []
    #     if 'active_model' in self._context and 'active_id' in self._context and self._context['active_model'] == 'kw_timesheet_project_tag_report': 
    #         project = self.env['project.project'].browse(self._context['active_id'])
    #         project_employees = project.mapped('resource_id.emp_id')
    #         if value == 'taggged':
    #             domain = [('employee_id','in',project_employees.ids)]
    #         elif value == 'non-tagged':
    #             domain = [('employee_id','not in',project_employees.ids)]
    #     else:
    #         query = 'select distinct emp_id from kw_project_resource_tagging where emp_id is not null'
    #         self._cr.execute(query)
    #         query_data = self._cr.fetchall()
    #         # print("QUERY DATA",query_data)
    #         employee_ids = [emp_tuple[0] for emp_tuple in query_data]
    #         if value == 'taggged':
    #             domain = [('employee_id','in',employee_ids)]
    #         elif value == 'non-tagged':
    #             domain = [('employee_id','not in',employee_ids)]
    #     # print("FINAL DOMAIN-->",domain)
    #     return domain

    # @api.multi
    # def _search_timesheet_tagged_project(self,operator,value):
    #     print("_search_timesheet_tagged_project method called")
    #     domain = []
    #     query = 'select project_id,emp_id,start_date from kw_project_resource_tagging where start_date is not null'
    #     self._cr.execute(query)
    #     employee_wise_project_data = self._cr.fetchall()
    #     print(employee_wise_project_data)
    #     return domain

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # print('self._context',self._context)
        if self._context.get('timesheet_report'):
            if self.env.user.has_group('kw_timesheets.group_kw_timesheets_report_manager'):
                args +=[]
            elif self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
                dept_hod= self.env['hr.department'].sudo().search([('manager_id.user_id','=',self.env.uid)])
                if dept_hod:
                    args += ['|',('employee_id','child_of',self.env.user.employee_ids.ids),('employee_id.department_id','child_of',dept_hod.ids)]
                else:
                    args += [('employee_id','child_of',self.env.user.employee_ids.ids)]
        return super(TimesheetReport, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)   

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
          SELECT row_number() over(order by t.id) as id,e.id AS employee_id,e.parent_id,
            concat(e.name,' (',e.emp_code,')') AS employee_name, 
            d.name AS dept_name,
            j.name AS desg_name,
            (SELECT name FROM hr_department WHERE id = e.division) AS division,
            (SELECT alias FROM kw_res_branch WHERE id = e.job_branch_id) AS location,
            (SELECT name FROM project_project WHERE id = t.project_id) AS project,
            (SELECT id FROM project_project WHERE id = t.project_id) AS project_id,
            coalesce(cl.name,'') AS opportunity,
            c.name AS category_name,
            pt.name AS project_task,
            t.date AS date, t.name AS desc,
            t.unit_amount AS effort_hour, 
            coalesce(Cast(TO_CHAR((t.unit_amount || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins')as timesheet_effort
            FROM account_analytic_line t
            JOIN hr_employee e ON e.id = t.employee_id and t.active = True
            LEFT JOIN hr_department d ON e.department_id = d.id
            JOIN kw_project_category_master c ON c.id = t.prject_category_id
            JOIN project_task pt ON pt.id = t.task_id
            LEFT JOIN hr_job j ON j.id =e.job_id
            LEFT JOIN crm_lead cl ON cl.id = t.crm_lead_id

            )""" % (self._table))
