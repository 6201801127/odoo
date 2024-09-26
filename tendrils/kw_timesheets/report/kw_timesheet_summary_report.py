from odoo import tools
from odoo import models, fields, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class TimesheetSummaryReport(models.Model):
    _name           = "kw_timesheet_summary_report"
    _description    = "Timesheet report Summary"
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
    total_effort        = fields.Float('Extra/Deficit Effort')
    total_effortper     = fields.Float('Total Effort in %')
    is_validate         = fields.Char(string='Is Validate')
    remark              = fields.Char('Remark',compute='get_remark')
    # active              = fields.Boolean('Active')

    @api.multi
    def get_remark(self):
        timesheet_validation_recs = self.env['timesheet.validation'].sudo().search([])
        for rec in self:
            validation_recs = timesheet_validation_recs.filtered(lambda x: (rec.week_start_date <= x.validation_date or rec.week_end_date >= x.validation_date))
            validation_line_recs = validation_recs.mapped('validation_line_ids')
            for validation_line_rec in validation_line_recs:
                if validation_line_rec.employee_id.id == rec.employee_id.id and rec.week_start_date <=validation_line_rec.validation_id.validation_date and rec.week_end_date==validation_line_rec.validation_id.validation_date:
                    rec.remark = validation_line_rec.validation_id.remark
    
    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     print('self._context',self._context)
    #     if self._context.get('timesheet_summary_report'):
    #         if self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
    #             dept_hod = self.env['hr.department'].sudo().search([('manager_id.user_id','=',self.env.uid)])
    #             if dept_hod:
    #                 args += ['|',('employee_id','child_of',self.env.user.employee_ids.ids),('employee_id.department_id','child_of',dept_hod.ids)]
    #             else:
    #                 args += [('employee_id','child_of',self.env.user.employee_ids.ids)]
    #     print("Final args    --->",args)
    #     return super(TimesheetSummaryReport, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)   

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            with attendance as
                (select
                a.employee_id,
                date_trunc('week', attendance_recorded_date)::date AS WeekStartDate,
                (date_trunc('week', attendance_recorded_date)+ '6 days'::interval)::date as WeekEndDate,
                sum(case    
                when day_status in ('0','3') and is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time  
                when day_status in ('0','3') and is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 
                end
                *
                case when leave_day_value=1 then 0 when leave_day_value=0.5 then 0.5 else 1 end
                *
                (case when is_valid_working_day = True and is_on_tour = True and day_status in ('0','3') then 1
                when is_valid_working_day = True and payroll_day_value = 0 and day_status in ('0','3') then 0
                else 1 end)) AS num_required_effort,
                        
                sum(case when day_status in ('0','3') then 1 else 0 end) as working_days,
                sum(leave_day_value) as on_leave_state,
                sum(case when is_on_tour = True then 1 else 0 end) as on_tour_state,
                    sum(case
                    when is_valid_working_day = True and is_on_tour = True then 0
                    when is_valid_working_day = True and payroll_day_value = 0 and day_status in ('0','3') then 1
                    else 0 
                    end) AS absent_state
                from kw_daily_employee_attendance a 
                group by employee_id, date_trunc('week', attendance_recorded_date)::date,
                (date_trunc('week', attendance_recorded_date)+ '6 days'::interval)::date
                ),
                timesheet as(
                select employee_id, date_trunc('week', date)::date AS WeekStartDate,
                (date_trunc('week', date)+ '6 days'::interval)::date as WeekEndDate, 
                sum(unit_amount) as timesheet_effort
                , min(case when validated = 't' then 1 else 0 end) as validated,
                active 
                from account_analytic_line  
                group by employee_id,active,
                date_trunc('week', date)::date,
                (date_trunc('week', date)+ '6 days'::interval)::date
                )

                select row_number() over(order by a.weekstartdate, e.id) as id, a.weekstartdate as week_start_date, a.weekenddate as week_end_date, 
                a.employee_id as employee_id,e.department_id as department_id, e.division as division_id, e.job_id as designation_id, 
                a.working_days as working_days, 
                a.absent_state as absent_days, a.on_tour_state as on_tour_days, a.on_leave_state as on_leave_days,
                a.num_required_effort as required_effort,
                coalesce(t.timesheet_effort, 0) as timesheet_effort,
                (coalesce(t.timesheet_effort,0) - coalesce(a.num_required_effort,0)) as total_effort,
                case when coalesce(a.num_required_effort,0)= 0 then 0 else  (coalesce(t.timesheet_effort,0) / coalesce(a.num_required_effort,0))*100 end as total_effortper,
                t.validated as is_validate
                from attendance a
                join hr_employee e on e.id = a.employee_id
                left join timesheet t on t.employee_id = a.employee_id and t.weekstartdate = a.weekstartdate and t.WeekEndDate = a.WeekEndDate and t.active = True
                where e.enable_timesheet = True and a.WeekStartDate >= '2021-05-03' 
            )""" % (self._table))
    
    


    @api.multi
    def timesheet_summary_report_view_details_grid(self):
        
        view_id = self.env.ref('timesheet_grid.timesheet_view_grid_by_task_readonly').id
        return{
            'model': 'ir.actions.act_window',
            'name': self.employee_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'view_mode': 'grid',
            'views': [(view_id, 'grid')],
            'target': 'self',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'grid_anchor': (self.week_start_date - relativedelta(weeks=0)).strftime('%Y-%m-%d'),
                        'grid_range': 'week',
                        'search_default_groupby_project': 1,
                        'search_default_groupby_task': 1}
        }
