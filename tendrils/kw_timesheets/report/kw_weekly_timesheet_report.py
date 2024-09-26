from odoo import tools
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class WeeklyTimesheetReport(models.Model):
    _name           = "kw_weekly_timesheet_report"
    _description    = "Weekly Timesheet report Summary"
    _auto           = False
    _rec_name       = 'employee_id'
    _order          = "id asc"

    week_start_date     = fields.Date(string="Week Start Date")
    week_end_date       = fields.Date(string="Week End Date")
    employee_id         = fields.Many2one('hr.employee', string="Employee")
    department_id       = fields.Many2one('hr.department', string="Department")
    division_id         = fields.Many2one('hr.department', string="Division")
    designation_id      = fields.Many2one('hr.job', string="Designation")
    working_days        = fields.Integer('Working Days')
    absent_days         = fields.Integer('Absent')
    on_tour_days        = fields.Float('On Tour')
    on_leave_days       = fields.Float('On Leave')
    required_effort     = fields.Float('Required Effort')
    timesheet_effort    = fields.Float('Actual Effort')
    actual_effort       = fields.Float('Actual Timesheet Effort',compute="compute_actual_timesheet_effort")
    total_effort        = fields.Float('Extra/Deficit Effort')
    is_validate         = fields.Char(string='Is Validate')

    @api.multi
    def compute_actual_timesheet_effort(self):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)

        for weekly_timesheet in self:
            domain = ['&','&','&',('date','>=',weekly_timesheet.week_start_date),('date','<=',weekly_timesheet.week_end_date),('employee_id', '=', weekly_timesheet.employee_id.id),
                        '|','|',('project_id.emp_id','=',current_employee.id),
                                '&',('employee_id.parent_id','=',current_employee.id),('prject_category_id','!=',project_work.id),
                                '&',('project_id.reviewer_id','=',current_employee.id),('project_id.emp_id','=',weekly_timesheet.employee_id.id)]
            timesheets = self.env['account.analytic.line'].search(domain)
            weekly_timesheet.actual_effort = timesheets and sum(timesheets.mapped(lambda r:r.unit_amount)) or 0

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # print("received domain in _search",args)
        if self._context.get('weekly_timesheet'):
            if not self.env.user.has_group('hr_timesheet.group_timesheet_manager'):
                current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
                
                all_employees = current_employee.child_ids

                employee_projects = self.env['project.project'].sudo().search([('emp_id','=',current_employee.id)])
                all_employees |= employee_projects.mapped('resource_id.emp_id')
                
                reviewer_group_users = self.env.ref('kw_resource_management.group_sbu_reviewer').users
                if self.env.user in reviewer_group_users:
                    employee_reviewer_projects = self.env['project.project'].sudo().search([('reviewer_id','=',current_employee.id)])
                    all_employees |= employee_reviewer_projects.mapped('emp_id')

                all_employees -= current_employee
                args += [('employee_id','in',all_employees.ids),('is_validate','=','0')]
        # print("final domain in _search is -->",args)
        return super(WeeklyTimesheetReport, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # print("received domain in read_group",domain)
        if self._context.get('weekly_timesheet'):
            if not self.env.user.has_group('hr_timesheet.group_timesheet_manager'):
                current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
                
                all_employees = current_employee.child_ids
                
                employee_projects = self.env['project.project'].sudo().search([('emp_id','=',current_employee.id)])
                all_employees |= employee_projects.mapped('resource_id.emp_id')
                
                reviewer_group_users = self.env.ref('kw_resource_management.group_sbu_reviewer').users
                if self.env.user in reviewer_group_users:
                    employee_reviewer_projects = self.env['project.project'].sudo().search([('reviewer_id','=',current_employee.id)])
                    all_employees |= employee_reviewer_projects.mapped('emp_id')

                all_employees -= current_employee
                domain += [('employee_id','in',all_employees.ids),('is_validate','=','0')]
        # print("final domain in read_group is -->",domain)
        return super(WeeklyTimesheetReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)
        
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        # print("received domain in _search",domain)
        if self._context.get('weekly_timesheet'):
            if not self.env.user.has_group('hr_timesheet.group_timesheet_manager'):
                current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
                
                all_employees = current_employee.child_ids

                employee_projects = self.env['project.project'].sudo().search([('emp_id','=',current_employee.id)])
                all_employees |= employee_projects.mapped('resource_id.emp_id')
                
                reviewer_group_users = self.env.ref('kw_resource_management.group_sbu_reviewer').users
                if self.env.user in reviewer_group_users:
                    employee_reviewer_projects = self.env['project.project'].sudo().search([('reviewer_id','=',current_employee.id)])
                    all_employees |= employee_reviewer_projects.mapped('emp_id')

                all_employees -= current_employee
                domain += [('employee_id','in',all_employees.ids),('is_validate','=','0')]
        # print("final domain in search_read is -->",domain)
        return super(WeeklyTimesheetReport,self).search_read(domain, fields, offset, limit, order)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            with attendance as
                (select
                a.employee_id,
                date_trunc('week', attendance_recorded_date)::date AS WeekStartDate,
                (date_trunc('week', attendance_recorded_date)+ '6 days'::interval)::date as WeekEndDate,
                sum(case    when day_status in ('0','3') and is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time  
                    when day_status in ('0','3') and is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 
                    end*case when leave_day_value=1 then 0 when leave_day_value=0.5 then 0.5 else 1 end) as num_required_effort,
                sum(case when day_status in ('0','3') then 1 else 0 end) as working_days,
                sum(leave_day_value) as on_leave_state,
                sum(case when is_on_tour = True then 1 else 0 end) as on_tour_state,
                sum(case 
                when is_valid_working_day = True and payroll_day_value = 0 and day_status in ('0','3') then 1
                when is_valid_working_day = True and payroll_day_value = 0.5 and day_status in ('0','3') then 0.5 
                else 0 
                end) as absent_state
                from kw_daily_employee_attendance a 
                group by employee_id, date_trunc('week', attendance_recorded_date)::date,
                (date_trunc('week', attendance_recorded_date)+ '6 days'::interval)::date
            ),
            timesheet as(
                select employee_id, date_trunc('week', date)::date AS WeekStartDate,
                (date_trunc('week', date)+ '6 days'::interval)::date as WeekEndDate, 
                sum(unit_amount) as timesheet_effort
                , min(case when validated = 't' then 1 else 0 end) as validated
                from account_analytic_line  
                group by employee_id,
                date_trunc('week', date)::date,
                (date_trunc('week', date)+ '6 days'::interval)::date
            )

            select row_number() over(order by a.weekstartdate, e.id) as id, a.weekstartdate as week_start_date, a.weekenddate as week_end_date, 
            a.employee_id as employee_id,e.department_id as department_id, e.division as division_id, e.job_id as designation_id, 
            a.working_days as working_days, 
            a.absent_state as absent_days, a.on_tour_state as on_tour_days, a.on_leave_state as on_leave_days,
            a.num_required_effort as required_effort,
            t.timesheet_effort as timesheet_effort,
            (coalesce(t.timesheet_effort,0) - coalesce(a.num_required_effort,0)) as total_effort,
            t.validated as is_validate
            from attendance a
            join hr_employee e on e.id = a.employee_id
            join timesheet t on t.employee_id = a.employee_id and t.weekstartdate = a.weekstartdate and t.WeekEndDate = a.WeekEndDate
            where e.active = True and a.WeekEndDate < CURRENT_DATE
            )""" % (self._table))

    @api.multi
    def weekly_timesheet_view_details(self):
        view_id = self.env.ref('hr_timesheet.timesheet_view_tree_user').id
        return{
            'model': 'ir.actions.act_window',
            'name': 'Validate Timesheet',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            # 'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'tree')],
            'target': 'self',
            # 'view_id': view_id,
            'domain': [('employee_id', '=', self.employee_id.id), ('date', '>=', self.week_start_date),
                       ('date', '<=', self.week_end_date)],
            'context': {'custom_timesheet_report': True}
        }

    @api.multi
    def weekly_timesheet_view_details_grid(self):
        # print("GRID METHOD--->")
        view_id = self.env.ref('timesheet_grid.timesheet_view_grid_by_employee_validation').id
        # tree_view_id = self.env.ref('hr_timesheet.timesheet_view_tree_user').id
        domain = []
        if not self.env.user.has_group('hr_timesheet.group_timesheet_manager'):
            # print("not in manager group")
            current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
            project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)
            
            # project_manager_projects = self.env['project.project'].sudo().search([('emp_id','=',current_employee.id)],limit=1)
            
            # reviewers = self.env.ref('kw_resource_management.group_sbu_reviewer').users
            # reviewer_projects = self.env['project.project'].sudo().search([('reviewer_id','=',current_employee.id)])
                    

            # if project_manager_projects and self.employee_id.parent_id == current_employee and self.env.user in reviewers: #PM,RA and Reviewer
            #     print("All 3")
            domain = ['&',('employee_id', '=', self.employee_id.id),
                        '|','|',('project_id.emp_id','=',current_employee.id),
                                '&',('employee_id.parent_id','=',current_employee.id),('prject_category_id','!=',project_work.id),
                                '&',('project_id.reviewer_id','=',current_employee.id),('project_id.emp_id','=',self.employee_id.id)]

            # elif project_manager_projects and self.env.user in reviewers: #PM and Reviewer
            #     print("project manager and reviewer")
            #     domain = ['&',('employee_id', '=', self.employee_id.id),
            #               '|',('project_id.emp_id','=',current_employee.id),
            #                 '&',('project_id.reviewer_id','=',current_employee.id),('project_id.emp_id','=',self.employee_id.id)]
                
            # elif self.employee_id.parent_id == current_employee and self.env.user in reviewers: #RA and Reviewer
            #     print("RA and Reviewer")
            #     domain = ['&',('employee_id', '=', self.employee_id.id),
            #               '|',('prject_category_id','!=',project_work.id),
            #               '&',('project_id.reviewer_id','=',current_employee.id),('project_id.emp_id','=',self.employee_id.id)]
            # elif project_manager_projects and self.employee_id.parent_id == current_employee:
            #     print("PM and RA")
            #     domain = ['&',('employee_id', '=', self.employee_id.id),
            #               '|',
            #               ('project_id.emp_id','=',current_employee.id),('prject_category_id','!=',project_work.id)]
            # elif self.env.user in reviewers:
            #     print("only reviewer")
            #     domain = [('employee_id', '=', self.employee_id.id),
            #               ('project_id.reviewer_id','=',current_employee.id),
            #               ('project_id.emp_id','=',self.employee_id.id)]
            # elif project_manager_projects:
            #     print("only project manager")
            #     domain = [('employee_id', '=', self.employee_id.id),('project_id.emp_id','=',current_employee.id)]
            # else:
            #     print("only RA")
            #     domain = [('employee_id', '=', self.employee_id.id),('prject_category_id','!=',project_work.id)]
                
        # print("final domain inside grid",domain)
        
        return {
            'model': 'ir.actions.act_window',
            'name': self.employee_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'view_mode': 'grid',
            'views': [(view_id, 'grid')],
            'target': 'self',
            'domain': domain,
            'context': {'grid_anchor': (self.week_start_date - relativedelta(weeks=0)).strftime('%Y-%m-%d'),
                        'week_end_date':str(self.week_end_date),
                        'grid_range': 'week',
                        'edit':True,
                       }
                    }
