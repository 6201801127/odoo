# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api


class DailyMatchingReport(models.Model):
    _name = "kw_daily_matching_report"
    _description = "Employee Attendance Summary Report"
    _auto = False

    item = fields.Char('Item')
    count = fields.Integer('Count')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
           -- Master Start --
                select 1 as id, 'Total Employee' as Item,
                coalesce(count(id),0) as count
                from hr_employee
                where active = True
                UNION all

                select 2 as id, 'Total Employee Configured for attendance', count(id)
                from hr_employee
                where (id in (select hr_employee_id from hr_employee_kw_attendance_mode_master_rel)) and active = True
                UNION all

                select 3 as id, 'Total Shift' as Item,
                coalesce(count(id),0)
                from resource_calendar
                where employee_id is Null
                UNION all

                select 4 as id,'Total Roster Group' as Item,
                coalesce(count(id),0)
                from kw_roaster_group_config
                UNION all
            
                select 5 as id,'Total Roster Employee' as Item, 
                coalesce(count(emp.id),0) 
                from hr_employee emp
                where emp.active = True and emp.id in (select group_id from hr_employee_roaster_group_config_rel)
                UNION all

                select 6 as id, 'Total Roster Employee Configured' as Item,
                coalesce(count(emp.id),0) 
                from hr_employee emp
                where emp.active = True and emp.id in 
                (select employee_id from kw_employee_roaster_shift where date = current_date)
                UNION all
                
                select 7 as id,'Total Flexi Employee' as Item, 
                coalesce(count(emp.id),0) 
                from hr_employee emp
                where emp.active = True and emp.id in (select employee_id from resource_calendar where employee_id is not null)
                UNION all
                
                select 8 as id,'Only Portal Mode Attendance' as Item, 
                coalesce(count(e.hr_employee_id),0) as count
                from hr_employee_kw_attendance_mode_master_rel e
                join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                inner join hr_employee emp on emp.id = e.hr_employee_id 
                where am.alias = 'portal'
                AND e.hr_employee_id not in (select hr_employee_id from hr_employee_kw_attendance_mode_master_rel e
                    join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                    where am.alias not in ('portal'))
                And emp.active = True
                UNION all

                select 9 as id,'Only Bio-Metric Mode Attendance' as Item, 
                coalesce(count(e.hr_employee_id),0) as count
                from hr_employee_kw_attendance_mode_master_rel e
                join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                inner join hr_employee emp on emp.id = e.hr_employee_id 
                where am.alias = 'bio_metric'
                AND e.hr_employee_id not in (select hr_employee_id from hr_employee_kw_attendance_mode_master_rel e
                    join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                    where am.alias not in ('bio_metric'))
                And emp.active = True
                    UNION all

                select 10 as id,'Total Portal + Bio Mode attendance' as Item, 
                coalesce(count(id),0) as count
                from hr_employee emp 
                where id in (select hr_employee_id from hr_employee_kw_attendance_mode_master_rel e
                    join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                    where am.alias = 'portal') 
                and id in (select hr_employee_id from hr_employee_kw_attendance_mode_master_rel e
                    join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                    where am.alias = 'bio_metric') 
                and id not in (select hr_employee_id from hr_employee_kw_attendance_mode_master_rel e
                    join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                    where am.alias not in ('bio_metric','portal')) 
                And emp.active = True
                    UNION all

                select 11 as id,'Total Manual Mode Attendance' as Item, 
                coalesce(count(e.hr_employee_id),0) as count
                from hr_employee_kw_attendance_mode_master_rel e
                join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                inner join hr_employee emp on emp.id = e.hr_employee_id 
                where am.alias = 'manual'
                AND e.hr_employee_id not in (select hr_employee_id from hr_employee_kw_attendance_mode_master_rel e
                    join kw_attendance_mode_master am on am.id = e.kw_attendance_mode_master_id
                    where am.alias not in ('manual'))
                And emp.active = True
                UNION all

                select 12 as id, 'Total No Attendance' as Item,
                coalesce(count(id),0) as count
                from hr_employee where no_attendance = True and active = True
                UNION all
            /*******Master End

            Attendance Start  ***/
                    
                select 13 as id,'Total Present' as Item,
                coalesce(sum(case when check_in is not null then 1 else 0 end),0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION All

                select 29 as id,'Total Week Off/Holiday+Present' as Item,
                coalesce(sum(case when check_in is not null and day_status in ('2','4','5') then 1 else 0 end),0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION All

                select 30 as id,'Total Employee on Week Off/Holiday' as Item,
                coalesce(sum(case when day_status in ('2','4','5') then 1 else 0 end),0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION All

                select CAST(concat(rb.id,12) AS INT) AS id,concat('Total Present in ',rb.name,', ',rb.city) as Item,
                coalesce(sum(case when check_in is not null then 1 else 0 end),0)
                from kw_daily_employee_attendance da
                join hr_employee he on he.id = da.employee_id
                join resource_calendar rc on rc.id = he.resource_calendar_id
                join kw_res_branch rb on rb.id = rc.branch_id
                where attendance_recorded_date = current_date group by rb.id
                UNION all

                select 15 as id,'Total Leave' as Item,
                coalesce(sum(case when state = '4' and day_status in ('0','3') then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION all

                select 16 as id,'Total Tour' as Item,
                coalesce(sum(case when state = '3' and day_status in ('0','3') then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION all

                select 17 as id,'Total Absent' as Item,
                coalesce(sum(case when check_in is null and day_status in ('0','3') then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION all

                select 18 as id,'Total Half Day Absent' as Item,
                coalesce(sum(case when state in ('7','8') and day_status in ('0','3') then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION all

                select 19 as id,'Total Portal Attendance' as Item, 
                coalesce(count(emp.id),0) 
                from hr_employee emp
                where emp.active = True and emp.id in (select employee_id from hr_attendance where check_in_mode = 0 and mode_enabled =True and (Date(check_in) = current_date or Date(check_out) = current_date)) and emp.id not in (select employee_id from hr_attendance where check_in_mode = 1 and mode_enabled =True and (Date(check_in) = current_date or Date(check_out) = current_date)) 
                UNION all
                
                select 20 as id,'Total Bio-Metric Attendance' as Item, 
                coalesce(count(emp.id),0) 
                from hr_employee emp
                where emp.active = True and emp.id in (select employee_id from hr_attendance where check_in_mode = 1 and mode_enabled =True and (Date(check_in) = current_date or Date(check_out) = current_date))
                UNION all
            /*******Attendance End

            Late Entry Start  ***/

                select 21 as id,'Total Late Entry' as Item,
                coalesce(sum(case when check_in_status = '2' and day_status in ('0','3') then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION all

                select 22 as id,'Total Extra Late Entry' as Item,
                coalesce(sum(case when check_in_status = '3' and day_status in ('0','3') then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION all

                select 23 as id,'Total Early Entry' as Item,
                coalesce(sum(case when check_in_status in ('-1','0') and day_status in ('0','3') then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION all

            /*** Late Entries End 

            Roster Start ***/
                
                select 24 as id,'Total Roster Present' as Item,
                coalesce(sum(case when check_in is not null and day_status = '3' then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date
                UNION All
                
                select 25 as id, 'Roster Off' as Item,
                coalesce(count(id),0)
                from hr_employee 
                where active = True and 
                id in (select employee_id from kw_employee_roaster_shift where week_off_status = True and date = current_date)
                UNION all
                
                select 26 as id,'Total Roster Absent' as Item,
                coalesce(sum(case when check_in is null and day_status = '3' then 1 else 0 end) ,0)
                from kw_daily_employee_attendance where attendance_recorded_date = current_date

                
            -- Roster End --
        )""" % (self._table))
