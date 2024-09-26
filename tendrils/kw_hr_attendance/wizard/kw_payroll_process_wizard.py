# -*- coding: utf-8 -*-
#########################
#
# Created On : 21-Oct-2020 , By : T Ketaki Debadarshini
# Future day added to tour , leave , maternity and lwop 19 March 2021 (Gouranga)

#########################

from datetime import date, datetime, timezone, timedelta
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

from dateutil.relativedelta import relativedelta

from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_LE, IN_STATUS_EXTRA_LE, \
    IN_STATUS_LE_HALF_DAY, IN_STATUS_LE_FULL_DAY, DAY_STATUS_WORKING, DAY_STATUS_RWORKING, LATE_WPC, LATE_WOPC, \
    ATD_STATUS_PRESENT, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT, DAY_STATUS_WEEKOFF, DAY_STATUS_RHOLIDAY, \
    DAY_STATUS_HOLIDAY, EMP_STS_NORMAL, EMP_STS_NEW_JOINEE, EMP_STS_EXEMP, LATE_PC_PER_DAY_VALUE, LATE_PC_FIXED_DAY, \
    LATE_PC_FIXED_DAY_VALUE, LEAVE_TYPE_MATERNITY


class HrAttendancePayrollProcess(models.TransientModel):
    _name = "kw_payroll_process_wizard"
    _description = "Attendance Monthly Payroll Process"

    @api.model
    def default_get(self, fields):
        res = super(HrAttendancePayrollProcess, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        # print(self.env.context)

        res.update({
            'monthly_payroll_ids': active_ids,
        })

        return res

    attendance_year = fields.Selection(selection='_get_year_list', string='Year', default=str(datetime.today().year))
    attendance_month = fields.Selection(selection='_get_month_name_list', string='Month', default=str(datetime.today().month))
    company_id = fields.Many2one('res.company')
    department_id = fields.Many2one('hr.department')
    monthly_payroll_ids = fields.Many2many(
        string='Payroll Info',
        comodel_name='kw_employee_monthly_payroll_info',
        relation='payroll_process_monthly_payroll_rel',
        column1='process_id',
        column2='payroll_id',
    )
    
    @api.model
    def _get_month_name_list(self):
        cur_date = datetime.today().date()
        months_choices = [(str(cur_date.month), cur_date.strftime('%B'))]

        first = cur_date.replace(day=1)
        last_month_date = first - timedelta(days=1)
        months_choices.append((str(last_month_date.month), last_month_date.strftime('%B')))

        previous_last_month = last_month_date.replace(day=1) - timedelta(days=1)
        previous_last_month1 = previous_last_month.replace(day=1) - timedelta(days=1)
        previous_last_month2 = previous_last_month1.replace(day=1) - timedelta(days=1)
        previous_last_month3 = previous_last_month2.replace(day=1) - timedelta(days=1)
        previous_last_month4 = previous_last_month3.replace(day=1) - timedelta(days=1)
        previous_last_month5 = previous_last_month4.replace(day=1) - timedelta(days=1)
        previous_last_month6 = previous_last_month5.replace(day=1) - timedelta(days=1)
        previous_last_month7 = previous_last_month6.replace(day=1) - timedelta(days=1)
        previous_last_month8 = previous_last_month7.replace(day=1) - timedelta(days=1)
        previous_last_month9 = previous_last_month8.replace(day=1) - timedelta(days=1)


        months_choices.append((str(previous_last_month.month), previous_last_month.strftime('%B')))
        months_choices.append((str(previous_last_month1.month), previous_last_month1.strftime('%B')))
        months_choices.append((str(previous_last_month2.month), previous_last_month2.strftime('%B')))
        months_choices.append((str(previous_last_month3.month), previous_last_month3.strftime('%B')))
        months_choices.append((str(previous_last_month4.month), previous_last_month4.strftime('%B')))
        months_choices.append((str(previous_last_month5.month), previous_last_month5.strftime('%B')))
        months_choices.append((str(previous_last_month6.month), previous_last_month6.strftime('%B')))
        months_choices.append((str(previous_last_month7.month), previous_last_month7.strftime('%B')))
        months_choices.append((str(previous_last_month8.month), previous_last_month8.strftime('%B')))
        months_choices.append((str(previous_last_month9.month), previous_last_month9.strftime('%B')))


        return months_choices

    @api.model
    def _get_year_list(self):
        cur_date = datetime.today().date()
        first = cur_date.replace(day=1)
        last_month_date = first - timedelta(days=1)

        years = [(str(cur_date.year), cur_date.year)]

        # Check if the last month's year is not the same as the current year
        if last_month_date.year != cur_date.year:
            years.append((str(last_month_date.year), last_month_date.year))

        # Find the second latest year
        second_latest_year = cur_date.year - 1
        if second_latest_year != last_month_date.year:
            years.append((str(second_latest_year), second_latest_year))

        return years
            

    
    @api.multi
    def process_payroll_info(self):
        """
            absent days count   : from last month 26th to this month 25th
            leave,tour          : from last month 26th to this month 25th
            present days count  : from this month start days to this month end date
            actual working days : from this month start days to this month end date

            leave,tour          : future days upto this month end date
            maternity           : future days upto this month end date
            
        """
        atd_year, atd_month, company_id, department_id  = int(self.attendance_year), int(self.attendance_month), self.company_id.id, self.department_id.id

        daily_attendance = self.env['kw_daily_employee_attendance']
        start_date, _, payroll_end_date = daily_attendance._get_recompute_date_range_configs(
            end_date=datetime.today().date().replace(day=1, month=atd_month, year=atd_year))
        # print("start_date and payroll_end_date",start_date,payroll_end_date)
        department_filter = f" AND hr.department_id = {department_id}" if department_id else ""
        employee_monthly_payroll = self.env['kw_employee_monthly_payroll_info']
        payroll_end_date = payroll_end_date.replace(day=payroll_end_date.day - 1)
        # print(start_date,payroll_end_date)
        # start_date                      = start_date.replace(month=atd_month,year=atd_year)
        if payroll_end_date > start_date:

            month_start_date, month_end_date = self.env['kw_late_attendance_summary_report']._get_month_range(atd_year, atd_month)
            monthly_payroll_recs = employee_monthly_payroll.search([('attendance_year', '=', atd_year), ('attendance_month', '=', atd_month)])
            # attendance_recorded_date >= '{month_start_date}' and attendance_recorded_date <= '{payroll_end_date}' and
            query = f""" SELECT 
                employee_id,  
                sum(leave_day_value) as num_leave_days,
                sum(case when is_on_tour = True then 1 else 0 end) as num_tour_days,

                sum(case when payroll_day_value = 0 and is_valid_working_day = True and (is_on_tour = False or is_on_tour is null) and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1  when  payroll_day_value = 0.5  and is_valid_working_day = True and (is_on_tour = False or is_on_tour is null ) and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 0.5 else 0 end) as num_absent_days,

                sum(case when attendance_recorded_date >= '{month_start_date}' and attendance_recorded_date <= '{payroll_end_date}' and is_on_tour = True and is_valid_working_day = True and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1  when attendance_recorded_date >= '{month_start_date}' and attendance_recorded_date <= '{payroll_end_date}'  and is_valid_working_day = True and (is_on_tour = False or is_on_tour is null ) and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then payroll_day_value when attendance_recorded_date > '{payroll_end_date}' and attendance_recorded_date <= '{month_end_date}' and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as num_present_days,
                
                sum(case when  attendance_recorded_date >= '{month_start_date}' and attendance_recorded_date <= '{payroll_end_date}' and state = '{ATD_STATUS_PRESENT}'  and is_valid_working_day = True and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1  when  attendance_recorded_date >= '{month_start_date}' and attendance_recorded_date <= '{payroll_end_date}'  and is_valid_working_day = True and state in ('{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 0.5 when attendance_recorded_date > '{payroll_end_date}' and attendance_recorded_date <= '{month_end_date}' and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as num_present_days_count_log,

                sum(case when attendance_recorded_date >= '{month_start_date}' and attendance_recorded_date <= '{month_end_date}' and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as num_shift_working_days,

                sum(case when  leave_day_value >0 and day_status in ('{DAY_STATUS_WEEKOFF}','{DAY_STATUS_RHOLIDAY}') then leave_day_value else 0 end) as num_wh_leave_days,
                sum(case when  leave_day_value >0 and day_status in ('{DAY_STATUS_HOLIDAY}') then leave_day_value else 0 end) as num_fh_leave_days,
                sum(case when  is_on_tour = True and day_status in ('{DAY_STATUS_WEEKOFF}','{DAY_STATUS_RHOLIDAY}') then 1 else 0 end) as num_wh_tour_days,
                sum(case when  is_on_tour = True and day_status in ('{DAY_STATUS_HOLIDAY}') then 1 else 0 end) as num_fh_tour_days,
            
                sum(case when employee_status = {EMP_STS_NEW_JOINEE} then 1 else 0 end) as new_joinee_status,
                sum(case when employee_status = {EMP_STS_EXEMP} then 1 else 0 end) as ex_employee_status,
                sum(case when  leave_day_value >0 and is_lwop_leave=True and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then leave_day_value else 0 end) as num_leave_lwop, 
                sum(case when  leave_day_value >0 and leave_code ='{LEAVE_TYPE_MATERNITY}' and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then leave_day_value else 0 end) as num_mt_leave_days,    
                    
                sum(case when  le_action_status ='{LATE_WOPC}' and check_in_status in ('{IN_STATUS_LE}','{IN_STATUS_EXTRA_LE}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as num_late_wopc,
                sum(case when  le_action_status ='{LATE_WPC}' and check_in_status in ('{IN_STATUS_LE}','{IN_STATUS_EXTRA_LE}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as num_late_wpc,
                
                0 as num_ex_late_wopc,
                0 as num_ex_late_wpc,
                {company_id} as company_id,
                {department_id} as department_id 
                
                from kw_daily_employee_attendance as att 
                join hr_employee as hr
                on att.employee_id = hr.id
                where attendance_recorded_date >= '{start_date}' and attendance_recorded_date <= '{payroll_end_date}' and hr.company_id = {company_id} 
                {department_filter}
                group by employee_id
             """
            # print("fetch query is--->",query)
            self.env.cr.execute(query)
            # % (EMP_STS_NEW_JOINEE,EMP_STS_EXEMP) 

            res = self.env.cr.dictfetchall()
            hr_employee = self.env['hr.employee']

            # #process the records within payroll date
            for data in res:
                employee_rec = hr_employee.browse(data['employee_id'])
                self._create_payroll_record(monthly_payroll_recs, atd_year, atd_month, employee_rec, data,
                                            month_start_date, month_end_date,start_date, payroll_end_date)

            # #process new joinee records after payroll end date
            new_joinee_rec_after_payroll_day = daily_attendance.search(
                [('attendance_recorded_date', '>', payroll_end_date),
                 ('employee_id.date_of_joining', '>', payroll_end_date), ('is_valid_working_day', '=', True)])
            
            emp_rec_after_payroll_day = new_joinee_rec_after_payroll_day.mapped('employee_id') # if new_joinee_rec_after_payroll_day else hr_employee

            for employee_rec in emp_rec_after_payroll_day:
                payroll_data = {'employee_id': employee_rec.id, 'num_leave_days': 0.0, 'num_tour_days': 0,
                                'num_absent_days': 0.0, 'num_present_days': 0.0, 'num_present_days_count_log': 0.0,
                                'num_shift_working_days': 0, 'num_wh_leave_days': 0.0, 'num_fh_leave_days': 0.0,
                                'num_wh_tour_days': 0, 'num_fh_tour_days': 0, 'new_joinee_status': 1,
                                'ex_employee_status': 0, 'num_leave_lwop': 0.0, 'num_late_wopc': 0, 'num_late_wpc': 0,
                                'num_ex_late_wopc': 0, 'num_ex_late_wpc': 0, 'num_mt_leave_days': 0.0,'company_id':employee_rec.company_id.id,'department_id':employee_rec.department_id.id}

                self._create_payroll_record(monthly_payroll_recs, atd_year, atd_month, employee_rec, payroll_data,
                                            month_start_date, month_end_date,start_date, payroll_end_date)
        
        self.env.user.notify_success(message='Payroll Processed Successfully.')
        return {"type": "set_scrollTop", }

    def count_shift_working_days(self, employee_rec, month_start_date, month_end_date, payroll_end_date):
        """count the shift working days for payroll processing, future working days . By default for all the
        future shift working days the present status is considered as true.

            @input params:

            -- employee_record set
            -- month start date
            -- month end date
            -- payroll start date

            @returns :

            -- no of shift working days
            -- no of future payroll working days
            -- no of actual present days in the future payroll days (after the payroll cal day)

        """
        daily_attendance      = self.env['kw_daily_employee_attendance']

        emp_attendance_record = daily_attendance.search(
            [('employee_id', '=', employee_rec.id), ('attendance_recorded_date', '>=', month_start_date),
             ('attendance_recorded_date', '<=', month_end_date)])
        emp_new_joinee = emp_attendance_record.filtered(lambda r:r.employee_status == EMP_STS_NEW_JOINEE)
        emp_ex_employee = emp_attendance_record.filtered(lambda r:r.employee_status == EMP_STS_EXEMP)
        # print(employee_rec,emp_new_joinee,emp_ex_employee)

        num_shift_working_days,actual_working_days, future_payroll_days, fut_actual_present_days = 0, 0, 0, 0
        # Additional variables for leave , tour ,maternity, lwop future dates 19 March 2021 (Gouranga)
        future_tour_days, future_leave_days, future_mt_leave_days = 0, 0, 0
        future_wh_leave_days, future_fh_leave_days, future_wh_tour_days, future_fh_tour_days, future_leave_lwop = 0, 0, 0, 0, 0
        # additional variable for future ex employee and future new joinee count added on 7 April 2021 (Gouranga)
        future_ex_emp_count, future_new_joinee_count = 0, 0
        range_start_date = month_start_date
        range_end_date = month_end_date

        if emp_new_joinee:
            range_start_date = emp_new_joinee.attendance_recorded_date

        if emp_ex_employee:
            range_end_date = emp_ex_employee.attendance_recorded_date
        # print(range_start_date,range_end_date)
        for day in range(int((month_end_date - month_start_date).days) + 1):

            attendance_date = month_start_date + timedelta(day)
            day_all_employee_rec = emp_attendance_record.filtered(lambda rec: rec.attendance_recorded_date == attendance_date)

            if day_all_employee_rec:
                if day_all_employee_rec.day_status in [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]:
                    num_shift_working_days += 1
                    if range_start_date <= attendance_date <= range_end_date and day_all_employee_rec.is_valid_working_day:
                        # print("inside attendance data if-->")
                        actual_working_days += 1

                    if attendance_date > payroll_end_date:
                        if day_all_employee_rec.is_valid_working_day:
                            future_payroll_days += 1
                            fut_actual_present_days += day_all_employee_rec.payroll_day_value
                            
                        # Start : Future dates for lwop, maternity 19 March 2021 (Gouranga)

                        if day_all_employee_rec.leave_day_value > 0 and day_all_employee_rec.is_lwop_leave:
                            future_leave_lwop += day_all_employee_rec.leave_day_value

                        if day_all_employee_rec.leave_day_value >0 and day_all_employee_rec.leave_code == LEAVE_TYPE_MATERNITY:
                            future_mt_leave_days += day_all_employee_rec.leave_day_value
                            
                        # End : Future dates for for lwop, maternity 19 March 2021 (Gouranga)
                        
                # Start : Future dates for tour, leave, wh_leave, wh_tour, fh_leave,fh_tour  19 March 2021 (Gouranga)
                if attendance_date > payroll_end_date:
                    if day_all_employee_rec.employee_status == EMP_STS_NEW_JOINEE:
                        future_new_joinee_count += 1

                    if day_all_employee_rec.employee_status == EMP_STS_EXEMP:
                        future_ex_emp_count += 1

                    if day_all_employee_rec.is_on_tour:
                        future_tour_days += 1

                    if day_all_employee_rec.leave_day_value > 0:
                        future_leave_days += day_all_employee_rec.leave_day_value

                    if day_all_employee_rec.day_status in [DAY_STATUS_WEEKOFF,DAY_STATUS_RHOLIDAY]:

                        if day_all_employee_rec.leave_day_value > 0:
                            future_wh_leave_days += day_all_employee_rec.leave_day_value

                        if day_all_employee_rec.is_on_tour:
                            future_wh_tour_days += 1

                    if day_all_employee_rec.day_status in [DAY_STATUS_HOLIDAY]:

                        if day_all_employee_rec.leave_day_value > 0:
                            future_fh_leave_days += day_all_employee_rec.leave_day_value

                        if day_all_employee_rec.is_on_tour:
                            future_fh_tour_days += 1
                # End : Future dates for tour, leave, wh_leave, wh_tour, fh_leave,fh_tour  19 March 2021 (Gouranga)
            else:
                shift_info = daily_attendance._compute_day_status(employee_rec, attendance_date)
                if shift_info and shift_info[0] and shift_info[0] in [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]:
                    num_shift_working_days += 1

                    valid_day = True
                    if employee_rec.date_of_joining and attendance_date < employee_rec.date_of_joining:
                        valid_day = False
                    if not employee_rec.active and employee_rec.last_working_day and attendance_date > employee_rec.last_working_day:
                        valid_day = False
                    if range_start_date <= attendance_date <= range_end_date and valid_day:
                        actual_working_days += 1
                        # print("inside without data if-->")

                    if valid_day and attendance_date > payroll_end_date:
                        future_payroll_days += 1
        # returned additional parameters for leave , tour ,maternity and lwop 19 March 2021 (Gouranga)
        return num_shift_working_days,actual_working_days,future_payroll_days,fut_actual_present_days,future_tour_days,future_leave_days,future_mt_leave_days,future_wh_leave_days,future_fh_leave_days,future_wh_tour_days,future_fh_tour_days,future_leave_lwop,future_ex_emp_count,future_new_joinee_count

    def _create_payroll_record(self,monthly_payroll_recs,atd_year,atd_month,employee_rec,data,month_start_date,month_end_date,start_date,payroll_end_date):
        """create a payroll data in monthly payroll table """

        if data:
            payroll_data = data
            emp_status = EMP_STS_NORMAL
            # condition taken down to get additional merged sttaus 7 Apr 2021 (Gouranga)
            # if payroll_data['new_joinee_status'] >0 :
            #     emp_status  = EMP_STS_NEW_JOINEE
            # if payroll_data['ex_employee_status'] >0 :
            #     emp_status  = EMP_STS_EXEMP
            # additional parameters for leave , tour , maternity and lwop cached 19 March 2021 (Gouranga)
            # additional parameters for ex employee and new joinee cached 07 Apr 2021 (Gouranga)
            num_shift_working_days,actual_working_days, future_payroll_days, fut_actual_present_days, future_tour_days, future_leave_days, future_mt_leave_days, future_wh_leave_days, future_fh_leave_days, future_wh_tour_days, future_fh_tour_days, future_leave_lwop, future_ex_emp_count, future_new_joinee_count = self.count_shift_working_days(employee_rec, month_start_date, month_end_date, payroll_end_date)

            # start : future date for new joinee and ex employee added : 7 April 2021 (Gouranga)
            # commented out this portion to resolve the issue of wrong count of exemployee and new joinee status
            # ''' if (payroll_data['new_joinee_status'] + future_new_joinee_count) > 0:
            #     emp_status = EMP_STS_NEW_JOINEE

            # if (payroll_data['ex_employee_status'] + future_ex_emp_count) > 0:
            #     emp_status = EMP_STS_EXEMP

            # if not employee_rec.active and employee_rec.last_working_day and (employee_rec.last_working_day <= month_start_date  or employee_rec.last_working_day <= month_end_date):
            #     emp_status = EMP_STS_EXEMP '''

            # End : future date for new joinee and ex employee added : 7 April 2021 (Gouranga)
            if employee_rec.date_of_joining and start_date <= employee_rec.date_of_joining <= payroll_end_date:
                emp_status = EMP_STS_NEW_JOINEE

            if not employee_rec.active and employee_rec.last_working_day and \
                    (start_date <= employee_rec.last_working_day <= payroll_end_date  or employee_rec.last_working_day < start_date):
                emp_status = EMP_STS_EXEMP

            num_present_days = data['num_present_days'] + future_payroll_days
            num_absent_days = data['num_absent_days']
            num_present_days_count_log = data['num_present_days_count_log'] + fut_actual_present_days
            num_late_wpc = data['num_late_wpc']

            # Start : future dates added On 19 March 2021 (Gouranga)
            num_leave_days = data['num_leave_days'] + future_leave_days
            num_tour_days = data['num_tour_days'] + future_tour_days
            num_mt_leave_days = data['num_mt_leave_days'] + future_mt_leave_days

            num_wh_leave_days = data['num_wh_leave_days'] + future_wh_leave_days
            num_wh_tour_days = data['num_wh_tour_days'] + future_wh_tour_days

            num_leave_lwop = data['num_leave_lwop'] + future_leave_lwop
            num_fh_leave_days = data['num_fh_leave_days'] + future_fh_leave_days
            num_fh_tour_days = data['num_fh_tour_days'] + future_fh_tour_days
            emp_company_id = data['company_id']
            emp_department_id = data['department_id']
            # End : future dates added On 19 March 2021 (Gouranga)

            fixed_pc_late_days_count, num_late_days_pc_after_fixed = 0, 0
            if num_late_wpc >= LATE_PC_FIXED_DAY:
                remaining_days_after_fixed = num_late_wpc - LATE_PC_FIXED_DAY
                fixed_pc_late_days_count = LATE_PC_FIXED_DAY * LATE_PC_FIXED_DAY_VALUE

                num_late_days_pc_after_fixed = remaining_days_after_fixed * LATE_PC_PER_DAY_VALUE
                # LATE_PC_PER_DAY_VALUE,LATE_PC_FIXED_DAY

            if employee_rec.no_attendance:
                num_present_days = num_shift_working_days
                num_absent_days = 0
                fixed_pc_late_days_count, num_late_days_pc_after_fixed = 0, 0
            # future dates for leave , tour ,maternity, lwop added on 19 March 2021 (Gouranga) 
            # future dates for ex employee and new joinee added on 7 April 2021 (Gouranga) 

            payroll_data.update({'emp_status': emp_status,
                                 'attendance_year': atd_year,
                                 'attendance_month': atd_month,
                                 'department_id':emp_department_id,
                                 'num_shift_working_days': num_shift_working_days,
                                 'actual_working_days': actual_working_days,
                                 'num_present_days_count_log': num_present_days_count_log,
                                 'num_absent_days': num_absent_days,
                                 'num_actual_working_days': num_present_days,
                                 'num_present_days': num_present_days,
                                 'num_fixed_late_days_pc': fixed_pc_late_days_count,
                                 'num_late_days_pc_after_fixed': num_late_days_pc_after_fixed,
                                 'num_total_late_days_pc': fixed_pc_late_days_count + num_late_days_pc_after_fixed,
                                 'num_leave_days': num_leave_days,
                                 'num_tour_days': num_tour_days,
                                 'num_mt_leave_days': num_mt_leave_days,
                                 'num_wh_leave_days': num_wh_leave_days,
                                 'num_wh_tour_days': num_wh_tour_days,
                                 'num_leave_lwop': num_leave_lwop,
                                 'num_fh_leave_days': num_fh_leave_days,
                                 'num_fh_tour_days': num_fh_tour_days,
                                 'company_id':emp_company_id})

            del payroll_data['new_joinee_status']
            del payroll_data['ex_employee_status']

            # print(payroll_data)

            emp_payroll_rec = monthly_payroll_recs.filtered(lambda rec: rec.employee_id.id == data['employee_id'])
            if emp_payroll_rec:
                emp_payroll_rec.write(payroll_data)
            else:
                emp_payroll_rec.create(payroll_data)

        return True

    def share_latest_payroll_info_with_kwantify(self):
        """Share the payroll info with the kwantify         
        """
        atd_year, atd_month = int(self.attendance_year), int(self.attendance_month)

        daily_attendance = self.env['kw_daily_employee_attendance']
        start_date, _, payroll_end_date = daily_attendance._get_recompute_date_range_configs(end_date=datetime.today().date().replace(day=1,month=atd_month,year=atd_year))

        employee_monthly_payroll = self.env['kw_employee_monthly_payroll_info']

        payroll_end_date = payroll_end_date.replace(day=payroll_end_date.day - 1)
        # print(start_date,payroll_end_date)
       
        if payroll_end_date > start_date:           

            latest_payroll_info = employee_monthly_payroll.search([('attendance_year','=',atd_year),('attendance_month','=',atd_month)])            

            for payroll_info in latest_payroll_info:
                # #call the sharing method of payroll
                payroll_info.share_payroll_info_with_kwantify(atd_year,atd_month)

        self.env.user.notify_success(message='Payroll details shared with Tendrils successfully.')
        return {"type": "set_scrollTop", }

    # share selected records with kwantify, Created On : 30-Nov-2020, By : T Ketaki Debadarshini
    def share_selected_payroll_info_with_kwantify(self):
        if self.monthly_payroll_ids:
            for monthly_payroll_id in self.monthly_payroll_ids:
                monthly_payroll_id.share_payroll_info_with_kwantify()
        else:
            raise ValidationError("Please select at least one payroll info to share")
