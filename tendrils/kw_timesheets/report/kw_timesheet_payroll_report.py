from odoo import tools
from odoo import models, fields, api


class TimesheetPayrollReport(models.Model):
    _name = "kw_timesheet_payroll_report"
    _description = "Timesheet Summary"
    _auto = False
    # _rec_name       = 'employee'

    emp_code = fields.Char(string="Employee Code")
    employee = fields.Char(string="Employee Name")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    designation = fields.Char(string="Designation")
    department_id = fields.Char(string="Department")
    division = fields.Char(string="Division")
    parent_id = fields.Char('Reporting Authority')
    doj=fields.Char('Date of Joining')
    
    working_days = fields.Integer('Working Days')
    absent_days = fields.Float('Absent Days')
    on_tour_days = fields.Float('On Tour Days')
    on_leave_days = fields.Float('On Leave Days')
    
    per_day_effort = fields.Float(string='Per Day Effort')
    required_effort_hour = fields.Float('Required Effort Hour')
    num_actual_effort = fields.Float('Actual Effort Hour')
    total_effort = fields.Float(string='Extra/Deficit Effort Hour')
    required_effort_day = fields.Float(string='Required Effort in Days')
    num_actual_effort_day = fields.Float(string='Actual Effort in Days')
    total_effort_day = fields.Float(string='Extra/Deficit Effort in Days')

    attendance_month = fields.Selection(string="Timesheet Month", selection=[
        ('01', "January"), ('02', "February"), ('03', "March"), ('04', "April"),
        ('05', "May"), ('06', "June"), ('07', "July"), ('08', "August"),
        ('09', "September"), ('10', "October"), ('11', "November"), ('12', "December")])
    attendance_year = fields.Integer("Timesheet Year")
    attendance_month_year = fields.Date(string="Timesheet Year/Month/Day")

    required_effort_char = fields.Char(string='Required Effort In HH:MM', compute="_compute_time_format")
    actual_effort_char = fields.Char(string="Actual Effort In HH:MM", compute="_compute_time_format")
    total_effort_char = fields.Char(string="Extra/Deficit Effort In HH:MM", compute="_compute_time_format")
    total_effort_percent = fields.Float(string="Extra/Deficit Effort In (%)", compute="_compute_time_format")

    @api.multi
    def _compute_time_format(self):
        for rec in self:
            time_required_effort_hour = rec.required_effort_hour
            time_actual_effort_hour = rec.num_actual_effort
            time_total_effort_hour = rec.total_effort

            if time_required_effort_hour > 0:
                rec.required_effort_char = "%d:%02d" % (int(time_required_effort_hour), ((time_required_effort_hour * 60) % 60))
            elif time_required_effort_hour == 0:
                rec.required_effort_char = "00:00"

            if time_actual_effort_hour > 0:
                rec.actual_effort_char = "%d:%02d" % (int(time_actual_effort_hour), ((time_actual_effort_hour * 60) % 60))
            elif time_actual_effort_hour == 0:
                rec.actual_effort_char = "00:00"

            if time_total_effort_hour < 0:
                abs_total_effort_hour = abs(time_total_effort_hour)
                rec.total_effort_char = '-' + "%d:%02d" % (int(abs_total_effort_hour), ((abs_total_effort_hour * 60) % 60))
            elif time_total_effort_hour > 0:
                abs_total_effort_hour = time_total_effort_hour
                rec.total_effort_char = "%d:%02d" % (int(abs_total_effort_hour), ((abs_total_effort_hour * 60) % 60))
            else:
                rec.total_effort_char = "00:00"

            if time_actual_effort_hour > 0 and time_required_effort_hour > 0:
                perc = ((time_actual_effort_hour - time_required_effort_hour) / time_required_effort_hour) * 100
                rec.total_effort_percent = "{:.2f}".format(perc)
            elif time_actual_effort_hour == 0 and time_required_effort_hour > 0:
                rec.total_effort_percent = "-100"
            elif time_actual_effort_hour == 0 and time_required_effort_hour == 0:
                rec.total_effort_percent = "0"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # print('self._context',self._context)
        if self._context.get('payroll_report'):
            if self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
                # print('manager found')
                dept_hod = self.env['hr.department'].sudo().search([('manager_id.user_id','=',self.env.uid)])
                if dept_hod:
                    args += ['|', ('employee_id', 'child_of', self.env.user.employee_ids.ids),
                             ('employee_id.department_id', 'child_of', dept_hod.ids)]
                else:
                    args += [('employee_id', 'child_of', self.env.user.employee_ids.ids)]
        return super(TimesheetPayrollReport, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)   

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW {self._table} AS (
         with timesheet AS
                (
                    SELECT employee_id, date, active,
                    sum(unit_amount) AS timesheet_effort
                    FROM account_analytic_line
                    where active = True and validated=True  
                    GROUP BY employee_id, date,active
                ), attendance AS
                (
                    SELECT 
                    a.employee_id,
                    date_trunc('month', attendance_recorded_date + INTERVAL '1 MONTH - 25 DAY') ::timestamp without time zone::date AS attendance_month_year, 
                    EXTRACT(year from attendance_recorded_date + INTERVAL '1 MONTH - 25 DAY') as attendance_year, 
                    sum(case when day_status in ('0','3') then 1 else 0 end) AS working_days,
                    sum(leave_day_value) AS on_leave_state,
                    sum(case when day_status in ('0','3') and is_on_tour = True then 1 else 0 end) AS on_tour_state,
                    sum(case
			when is_valid_working_day = True and is_on_tour = True then 0
                        when is_valid_working_day = True and payroll_day_value = 0 and day_status in ('0','3') then 1
                    else 0 
                    end) AS absent_state,
                    sum(case    
                        when day_status in ('0','3') and is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time  
                        when day_status in ('0','3') and is_cross_shift=True then resc.hours_per_day else 0 
                        end
                        *
                        case when leave_day_value=1 then 0 when leave_day_value=0.5 then 0.5 else 1 end
                        *
                        (case when is_valid_working_day = True and is_on_tour = True and day_status in ('0','3') then 1
                        when is_valid_working_day = True and payroll_day_value = 0 and day_status in ('0','3') then 0
			else 1 end)) AS num_required_effort,
                    sum(case when day_status in ('0','3') then timesheet_effort else 0 end) AS num_actual_effort
                    FROM kw_daily_employee_attendance a 
                    join resource_calendar resc on a.shift_id = resc.id
                    LEFT JOIN timesheet t ON t.employee_id=a.employee_id AND t.date=a.attendance_recorded_date AND t.active = True
                    WHERE a.attendance_recorded_date < CURRENT_DATE and a.attendance_recorded_date > date_trunc('month', CURRENT_DATE) - INTERVAL '2 year'
			group by  a.employee_id,date_trunc('month', a.attendance_recorded_date + INTERVAL '1 MONTH - 25 DAY'),EXTRACT(year from a.attendance_recorded_date + INTERVAL '1 MONTH - 25 DAY')
                  
                ), Day_Fraction as
                (
			select employee_id, attendance_month_year, case when (working_days-absent_state-on_leave_state) = 0 then 0 else num_required_effort/(working_days-absent_state-on_leave_state)  end as per_day_effort from attendance
                )
		    
                    SELECT row_number() over() AS id, to_char(date_trunc('month', a.attendance_month_year), 'MM') as attendance_month,
                    a.attendance_month_year,
                    a.attendance_year,
                    e.emp_code, e.name AS employee,
                    e.id AS employee_id,
                    j.name AS designation,
                    e.date_of_joining as doj,
                    (SELECT name FROM hr_department p WHERE e.department_id=p.id) AS department_id,
                    (SELECT name FROM hr_department p WHERE e.division=p.id) AS division,
		            (SELECT name FROM hr_employee o WHERE  o.id=e.parent_id) AS parent_id,
                    a.working_days AS working_days,
                    --(a.num_required_effort - a.absent_state)/(a.working_days)/(coalesce(a.num_actual_effort,0) - coalesce(a.num_required_effort,0)) as total_effort_in_days,
                    a.absent_state AS absent_days, a.on_tour_state AS on_tour_days, a.on_leave_state AS on_leave_days, df.per_day_effort,
                    a.num_required_effort AS required_effort_hour,
                    coalesce(a.num_actual_effort, 0) AS num_actual_effort,
                    (coalesce(a.num_actual_effort,0) - coalesce(a.num_required_effort,0)) AS total_effort,
                    case when df.per_day_effort=0 then 0 else (FLOOR(cast(a.num_required_effort/df.per_day_effort AS numeric)) + (case when round(cast(df.per_day_effort/2 AS numeric), 2) < CAST(cast(a.num_required_effort AS numeric) % cast(df.per_day_effort AS numeric) AS numeric) then 0.5 else 0 end)) end AS required_effort_day,
                    case when df.per_day_effort=0 OR a.num_actual_effort=0 then 0 else (FLOOR(cast(a.num_actual_effort/df.per_day_effort AS numeric)) + (case when round(cast(df.per_day_effort/2 AS numeric), 2) < CAST(cast(a.num_actual_effort AS numeric) % cast(df.per_day_effort AS numeric) AS numeric) then 0.5 else 0 end)) end AS num_actual_effort_day,
                    case when df.per_day_effort=0 then 0 else (FLOOR(cast((coalesce(a.num_actual_effort,0) - coalesce(a.num_required_effort,0))/df.per_day_effort AS numeric)) + (case when round(cast(df.per_day_effort/2 AS numeric), 2) < CAST(CAST(coalesce(a.num_actual_effort,0) - coalesce(a.num_required_effort,0) AS numeric) % cast(df.per_day_effort AS numeric) AS numeric) then 0.5 else 0 end)) end AS total_effort_day
                    FROM attendance a
                    join Day_Fraction DF ON DF.employee_id = a.employee_id and df.attendance_month_year=a.attendance_month_year
                    JOIN hr_employee e ON e.id = a.employee_id
                    JOIN hr_job j ON j.id=e.job_id
                    Join kwemp_employment_type k on k.id = e.employement_type
                    WHERE e.active = True AND e.enable_timesheet=True and k.name='FTE' 
            )""")

        # case when df.per_day_effort= 0 then 0 else round(cast(a.num_required_effort/df.per_day_effort as numeric)/5,1)*5 end AS required_effort_day,
        # case when df.per_day_effort= 0 then 0 else round(cast(a.num_actual_effort/df.per_day_effort as numeric)/5,1)*5 end AS num_actual_effort_day,
        # case when df.per_day_effort= 0 then 0 else round(cast(((coalesce(a.num_actual_effort,0) - coalesce(a.num_required_effort,0))/df.per_day_effort) as numeric)/5,1)*5 end AS total_effort_day
