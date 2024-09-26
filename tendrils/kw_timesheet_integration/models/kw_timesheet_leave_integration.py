import math
from odoo import models, fields, api
from datetime import date, datetime, timedelta


class kw_timesheet_payroll_report(models.Model):
    _inherit = "kw_timesheet_payroll_report"

    status = fields.Boolean(string='Shared', compute='_compute_report_status')
    timesheet_el_days = fields.Float(string='Timesheet EL Deduction in Days', compute='_compute_timesheet_el_days', search="search_el_deduct")
    timesheet_paycut_days = fields.Float(string='Timesheet Paycut in Days', compute='_compute_timesheet_el_days', search="search_paycut_days")

    @api.model
    def search_el_deduct(self,operator,value):
        recs = self.search([]).filtered(lambda x: x.timesheet_el_days > 0)
        return [('id', 'in', recs.ids)]

    @api.model
    def search_paycut_days(self,operator,value):
        recs = self.search([]).filtered(lambda x: x.timesheet_paycut_days > 0)
        return [('id', 'in', recs.ids)]

    @api.multi
    def _compute_report_status(self):
        for record in self:
            compare_payroll_record = self.env['kw_payroll_monthly_attendance_report'].sudo().search([('timesheet_payroll_report_id', '=', record.id),
                                                                                                     ('attendance_month', '=', record.attendance_month),
                                                                                                     ('attendance_year', '=', record.attendance_year)])
            if compare_payroll_record:
                record.status = True

    # """ If timesheet_el_days>0, record will create in kw_timesheet_leave_deduct model """

    # @api.model
    # def action_timesheet_el_deduct_update_scheduler(self):
    #     year = datetime.today().year
    #     month = datetime.today().month
    #     next_month = month + 1 if month < 12 else 1
    #     dt_25th_next_month = datetime.strptime(
    #                 '{}-{}-{:2} {}:{}:{}'.format(year, next_month, 25, 5, 0, 0), '%Y-%m-%d %H:%M:%S')
    #     dt_25th_current_month = datetime.strptime('{}-{}-{:2}'.format(year, month, 25), '%Y-%m-%d')

    #     timesheet_leave_deduct_record = self.env['kw_timesheet_leave_deduct']
    #     # if datetime.today().day <= 25:
    #     el_deduct_records = self.env['kw_timesheet_payroll_report'].sudo().search([('attendance_year','=',str(datetime.today().year))])
    #     for el_deduct_record in el_deduct_records:
    #         if el_deduct_record.timesheet_el_days > 0:
    #             get_timesheet_leave_deduct_records = timesheet_leave_deduct_record.sudo().search([('timesheet_payroll_report_id', '=', el_deduct_record.id)])
               
    #             current_timehseet_leave_deduct_record=get_timesheet_leave_deduct_records.filtered(lambda x:x.timesheet_month==datetime.today().strftime("%m") and x.timesheet_year==year)
              
    #             if get_timesheet_leave_deduct_records:
                    
    #                 if datetime.today().day <= 25 and current_timehseet_leave_deduct_record:
    #                     current_timehseet_leave_deduct_record.write(
    #                         {'emp_code': el_deduct_record.emp_code,
    #                          'employee_id': el_deduct_record.employee_id.id,
    #                          'designation': el_deduct_record.designation,
    #                          'department_id': el_deduct_record.department_id,
    #                          'division': el_deduct_record.division,
    #                          'parent_id': el_deduct_record.parent_id,
    #                          'timesheet_month': el_deduct_record.attendance_month,
    #                          'timesheet_year': el_deduct_record.attendance_year,
    #                          'timesheet_el_deduct_in_days': el_deduct_record.timesheet_el_days,
    #                          'attendance_month_year': el_deduct_record.attendance_month_year})
    #             else:
                    
    #                 timesheet_leave_deduct_record.sudo().create(
    #                     {'timesheet_payroll_report_id': el_deduct_record.id,
    #                      'emp_code': el_deduct_record.emp_code,
    #                      'employee_id': el_deduct_record.employee_id.id,
    #                      'designation': el_deduct_record.designation,
    #                      'department_id': el_deduct_record.department_id,
    #                      'division': el_deduct_record.division,
    #                      'parent_id': el_deduct_record.parent_id,
    #                      'timesheet_month': el_deduct_record.attendance_month,
    #                      'timesheet_year': el_deduct_record.attendance_year,
    #                      'timesheet_el_deduct_in_days': el_deduct_record.timesheet_el_days,
    #                      'attendance_month_year': el_deduct_record.attendance_month_year})
        # """update cron next execution time"""
        # validate_scheduler = self.env.ref('kw_timesheet_integration.el_deduct_update_scheduler_for_timesheet')
        # validate_scheduler.sudo().write({'nextcall': dt_25th_next_month})

    @api.multi
    def _compute_timesheet_el_days(self):
        leave_type = self.env['hr.leave.type'].sudo()
        leave_deduct = self.env['kw_timesheet_leave_deduct'].sudo()
        employee_leave_balances = {}
        # print(">>>>>>>>>>>>>>>>>>>>employee_leave_balances>>>>>>>>>>>>>>>>>>>>>>>>>>",employee_leave_balances)
        for record in self:
            deficit_hour = (record.required_effort_hour - record.num_actual_effort)
            if record.per_day_effort > 0:
                ttl_effort_day = math.floor(deficit_hour/record.per_day_effort) + (0.5 if (record.per_day_effort / 2) < (deficit_hour % record.per_day_effort) else 0) if deficit_hour > 0 else 0
            else:
                ttl_effort_day = 0
            """fetch EL balance of employee"""
            employee_id = record.employee_id.id
            if employee_id not in employee_leave_balances:
                employee_leave_balances[employee_id] = leave_type.with_context(employee_id=employee_id).search_read(
                    [('leave_code', '=', 'EL')], ['max_leaves', 'remaining_leaves'], limit=1)
            el_balance = employee_leave_balances[employee_id]
            """if deficit effort hour is more than 10% of required effort hour in a month """
            deducted_leaves = leave_deduct.search([('timesheet_month','=',record.attendance_month),('timesheet_year','=',record.attendance_year),('employee_id','=',employee_id)])
            # print(">>>>>>>>>>>>>>>>>>>>employee_leave_balances>>>>>>>>>>>>>>>>>>>>>>>>>>",employee_leave_balances)
            
            record.total_effort_day = ttl_effort_day
            if (record.required_effort_hour * 0.1) < (record.required_effort_hour - record.num_actual_effort):
                # check if el is already deducted
                if deducted_leaves:
                    record.timesheet_el_days = deducted_leaves.timesheet_el_deduct_in_days
                    record.timesheet_paycut_days = ttl_effort_day - deducted_leaves.timesheet_el_deduct_in_days
                # check if el balance 
                elif el_balance and el_balance[0]['remaining_leaves'] > 0:
                    # if EL balance is more than or equals to deficit days
                    if el_balance[0]['remaining_leaves'] >= ttl_effort_day:
                        record.timesheet_el_days = ttl_effort_day
                    else:
                        record.timesheet_el_days = el_balance[0]['remaining_leaves']
                        record.timesheet_paycut_days = ttl_effort_day - el_balance[0]['remaining_leaves']
                # no el balance
                else:
                    record.timesheet_paycut_days = ttl_effort_day
            else:
                record.timesheet_el_days = 0.0
            
    # @api.multi
    # def _search_avinash(self, operator, value):
    #     # field_id = self.search([]).filtered(lambda x : x.timesheet_el_days > 0 )
    #     return [('timesheet_el_days', '>',0)]