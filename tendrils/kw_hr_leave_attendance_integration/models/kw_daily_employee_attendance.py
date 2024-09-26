# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
# Description   : Creates ralation between leave allocation request and attendance records. Apply for comp off in case of off day entries
# Create By     : T Ketaki Debadrashini, On -11th Sep 2020                          #
###############################################################################
import logging
from datetime import date, datetime, timedelta, time

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import LEAVE_STS_ALL_DAY, LEAVE_STS_FHALF, LEAVE_STS_SHALF


class KwDailyEmpAttendance(models.Model):
    _inherit = 'kw_daily_employee_attendance'

    comp_off_ids = fields.One2many(
        string='Comp Off Leave Allocation Requests',
        comodel_name='hr.leave.allocation',
        inverse_name='attendance_id',
    )

    past_off_days_entries = fields.Boolean(compute="compute_past_off_days_entries")
    off_day_entries = fields.Boolean(string="OFF DAYS ENTRIES", oldname="Off_Day_Entries")

    @api.multi
    def compute_past_off_days_entries(self):
        past_date = date.today() - timedelta(days=180)
        for record in self:
            if record.attendance_recorded_date >= past_date:
                record.write({'off_day_entries': True})
                # record.past_off_days_entries = True
                # print(record.past_off_days_entries)
            else:
                record.write({'off_day_entries': False})
                # record.past_off_days_entries = False
                # print(record.past_off_days_entries)    

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('filter_before_6_month_date'):
            before_6_month_date = date.today() - timedelta(days=180)
            args += [('attendance_recorded_date', '>=', before_6_month_date)]
        return super(KwDailyEmpAttendance, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                         access_rights_uid=access_rights_uid)

    @api.multi
    def action_off_day_entry_apply_window(self):
        """action to open the comp off apply pop up with the default values from attendance record
            - raises error is comp off leave type is not defined
        """
        self.ensure_one()
        holiday_status_id = self.env['hr.leave.type'].search([('is_comp_off', '=', True)])

        if holiday_status_id:
            view_id = self.env.ref('kw_hr_leave_attendance_integration.view_off_day_entries_apply_form').id

            return {
                'name': 'Apply Comp Off',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.leave.allocation',
                'target': 'new',
                'view_type': 'form',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'flags': {'action_buttons': False, 'mode': 'edit', 'toolbar': False, },
                'context': {'create': False,
                            'default_name': f'Allocation request for date {self.attendance_recorded_date}',
                            'default_holiday_status_id': holiday_status_id.id,
                            'default_attendance_id': self.id,
                            'default_holiday_type': 'employee',
                            'default_employee_id': self.employee_id.id}
            }
        else:
            raise ValidationError(
                "Comp Off leave type does not exist in the system.\n Please create a comp off leave type and try again.")

    # #method to update leave status after leave cancellation

    def attendance_leave_cancellation_update(self, approved_leave_id):
        """
            update leave status the daily attendance data of each employee
            -   checks if leave status is there 
                   
        """
        if approved_leave_id:
            leave_from_date = approved_leave_id.request_date_from
            leave_to_date = approved_leave_id.request_date_to

            attendance_dates = []

            attendance_dates = [leave_from_date + timedelta(days=day) for day in range((leave_to_date - leave_from_date).days + 1)]
            # print(attendance_dates)

            attendance_records = self.env['kw_daily_employee_attendance'].sudo().search(
                [('attendance_recorded_date', 'in', attendance_dates),
                 ('employee_id', '=', approved_leave_id.employee_id.id), ('leave_day_value', '>', 0)])
            # leave_status  is_lwop_leave LEAVE_STS_SHALF LEAVE_STS_FHALF LEAVE_STS_ALL_DAY

            for attendance_record in attendance_records:
                leave_day_value = 1
                cancel_leave_status = LEAVE_STS_ALL_DAY

                if attendance_record.attendance_recorded_date == leave_from_date or attendance_record.attendance_recorded_date == leave_to_date:
                    if approved_leave_id.request_date_from_period == 'pm':
                            if leave_from_date == leave_to_date:
                                if approved_leave_id.request_unit_half == True and approved_leave_id.request_unit_half_to_period == True: 
                                    leave_day_value -= .5
                                    cancel_leave_status = LEAVE_STS_SHALF
                            elif attendance_record.attendance_recorded_date == leave_from_date:
                                if approved_leave_id.request_unit_half == True: 
                                    leave_day_value -= .5
                                    cancel_leave_status = LEAVE_STS_SHALF
                        # if approved_leave_id.request_unit_half_to_period and approved_leave_id.request_date_to_period:

                    if approved_leave_id.request_date_to_period == 'am':
                        if leave_from_date == leave_to_date:
                            if approved_leave_id.request_unit_half == True and approved_leave_id.request_unit_half_to_period == True: 
                                leave_day_value -= .5
                                cancel_leave_status = LEAVE_STS_FHALF
                        elif attendance_record.attendance_recorded_date == leave_to_date:
                            if approved_leave_id.request_unit_half_to_period == True: 
                                leave_day_value -= .5
                                cancel_leave_status = LEAVE_STS_FHALF

                    # if approved_leave_id.request_unit_half and approved_leave_id.request_date_from_period:
                    #     if approved_leave_id.request_date_from_period == 'pm':
                    #         leave_day_value -= .5
                    #         cancel_leave_status = LEAVE_STS_SHALF
                    # if approved_leave_id.request_unit_half_to_period and approved_leave_id.request_date_to_period:
                    #     if approved_leave_id.request_date_to_period == 'am':
                    #         leave_day_value -= .5
                    #         cancel_leave_status = LEAVE_STS_FHALF

                final_leave_status = attendance_record.leave_day_value - leave_day_value
                modified_leave_day_status = False

                if final_leave_status <= 0:
                    modified_leave_day_status = False
                elif final_leave_status == .5:
                    modified_leave_day_status = LEAVE_STS_SHALF if cancel_leave_status == LEAVE_STS_FHALF else LEAVE_STS_FHALF
                else:
                    continue
                # print(attendance_record,modified_leave_day_status)
                if attendance_record.leave_status != modified_leave_day_status \
                        or attendance_record.is_lwop_leave != approved_leave_id.holiday_status_id.unpaid \
                        or attendance_record.leave_code != approved_leave_id.holiday_status_id.leave_code:
                    attendance_record.sudo().write({'leave_status': modified_leave_day_status,
                                                    'is_lwop_leave': approved_leave_id.holiday_status_id.unpaid if modified_leave_day_status else False,
                                                    'leave_code': approved_leave_id.holiday_status_id.leave_code if modified_leave_day_status else False})
                    # print(asas)
        return True

    # #method to update leave status after leave approval
    def attendance_leave_approval_update(self, approved_leave_id, leave_data):
        """
            update leave status & LWOP the daily attendance data of each employee
            -   checks if leave status is there 
                   
        """
        if approved_leave_id:
            leave_from_date = approved_leave_id.request_date_from
            leave_to_date = approved_leave_id.request_date_to
            attendance_dates = []

            attendance_dates = [leave_from_date + timedelta(days=day) for day in range((leave_to_date - leave_from_date).days + 1)]
            # print(attendance_dates)

            attendance_records = self.env['kw_daily_employee_attendance'].sudo().search(
                [('attendance_recorded_date', 'in', attendance_dates),
                 ('employee_id', '=', approved_leave_id.employee_id.id)])
            # print(attendance_records)
            for attendance_record in attendance_records:
                leave_day_value = 1
                approve_leave_status = LEAVE_STS_ALL_DAY

                if attendance_record.attendance_recorded_date == leave_from_date or attendance_record.attendance_recorded_date == leave_to_date:
                    if leave_data:
                        leave_data = leave_data.filtered(lambda x: \
                                ((x.request_date_to == attendance_record.attendance_recorded_date) \
                            and ((x.request_date_from == attendance_record.attendance_recorded_date or x.request_date_to == attendance_record.attendance_recorded_date))) or \
                                ((x.request_date_from == attendance_record.attendance_recorded_date) \
                            and ((x.request_date_from == attendance_record.attendance_recorded_date or x.request_date_to == attendance_record.attendance_recorded_date))))
                        if len(leave_data) == 2:
                            leave_day_value = 1
                        else:
                            if approved_leave_id.request_date_from_period == 'pm':
                                if leave_from_date == leave_to_date:
                                    if approved_leave_id.request_unit_half == True and approved_leave_id.request_unit_half_to_period == True: 
                                        leave_day_value -= .5
                                        approve_leave_status = LEAVE_STS_SHALF
                                elif attendance_record.attendance_recorded_date == leave_from_date:
                                    if approved_leave_id.request_unit_half == True: 
                                        leave_day_value -= .5
                                        approve_leave_status = LEAVE_STS_SHALF
                            # if approved_leave_id.request_unit_half_to_period and approved_leave_id.request_date_to_period:
                            if approved_leave_id.request_date_to_period == 'am':
                                if leave_from_date == leave_to_date:
                                    if approved_leave_id.request_unit_half == True and approved_leave_id.request_unit_half_to_period == True: 
                                        leave_day_value -= .5
                                        approve_leave_status = LEAVE_STS_FHALF
                                elif attendance_record.attendance_recorded_date == leave_to_date:
                                    if approved_leave_id.request_unit_half_to_period == True: 
                                        leave_day_value -= .5
                                        approve_leave_status = LEAVE_STS_FHALF
                    else:
                        if approved_leave_id.request_date_from_period == 'pm':
                            if leave_from_date == leave_to_date:
                                if approved_leave_id.request_unit_half == True and approved_leave_id.request_unit_half_to_period == True: 
                                    leave_day_value -= .5
                                    approve_leave_status = LEAVE_STS_SHALF
                            elif attendance_record.attendance_recorded_date == leave_from_date:
                                if approved_leave_id.request_unit_half == True: 
                                    leave_day_value -= .5
                                    approve_leave_status = LEAVE_STS_SHALF
                        # if approved_leave_id.request_unit_half_to_period and approved_leave_id.request_date_to_period:
                        if approved_leave_id.request_date_to_period == 'am':
                            if leave_from_date == leave_to_date:
                                if approved_leave_id.request_unit_half == True and approved_leave_id.request_unit_half_to_period == True: 
                                    leave_day_value -= .5
                                    approve_leave_status = LEAVE_STS_FHALF
                            elif attendance_record.attendance_recorded_date == leave_to_date:
                                if approved_leave_id.request_unit_half_to_period == True: 
                                    leave_day_value -= .5
                                    approve_leave_status = LEAVE_STS_FHALF

                final_leave_status = leave_day_value
                modified_leave_day_status = False
                # print(attendance_record,final_leave_status)
                if final_leave_status == 1:
                    modified_leave_day_status = LEAVE_STS_ALL_DAY
                elif final_leave_status == .5:
                    modified_leave_day_status = approve_leave_status
                else:
                    continue

                # print(modified_leave_day_status)
                if attendance_record.leave_status != modified_leave_day_status \
                        or attendance_record.is_lwop_leave != approved_leave_id.holiday_status_id.unpaid \
                        or attendance_record.leave_code != approved_leave_id.holiday_status_id.leave_code:
                    attendance_record.sudo().write({'leave_status': modified_leave_day_status,
                                                    'is_lwop_leave': approved_leave_id.holiday_status_id.unpaid if modified_leave_day_status else False,
                                                    'leave_code': approved_leave_id.holiday_status_id.leave_code if modified_leave_day_status else False})

        return True

    def update_daily_attendance_leave_tour_status2(self):
        """
            update leave /tour status the daily attendance data of each employee
            -   checks if on tour
            -   checks if on leave
            -   checks if LWOP                       
        """
        daily_attendance = self.env['kw_daily_employee_attendance']
        start_date, end_date, _ = self._get_recompute_date_range_configs(end_date=datetime.today().date())
        error_log, update_record_log = '', ''
        # print(start_date,end_date)
        if end_date > start_date:

            # #""" call the .net web service for leave /tour status update with a date range"""

            try:
                leave_data = self.env['hr.leave'].generate_days_with_from_and_to_date(start_date, end_date)
                # tour_data = self.env['kw_tour'].get_tour_data(start_date,end_date)

                for data in leave_data:
                    try:
                        self.attendance_leave_approval_update(data,False)
                    except Exception as e:
                        # print(str(e))
                        error_log += "\n %s, %s:\t%s" % (data.employee_id.name, data.id, str(e))
                        continue

                # for emp_id,details in tour_data.items():
                #     emp_records = daily_attendance.search([('employee_id', '=', emp_id), ('attendance_recorded_date', 'in', list(details.keys()))])
                #     for emp_record in emp_records:
                #         is_on_tour = details[emp_record.attendance_recorded_date]
                #         ##"""update the attendance record tour and leave status if not updated """
                #         if emp_record.is_on_tour != is_on_tour:
                #             try:
                #                 # print(emp_record.employee_id.name,emp_record.attendance_recorded_date)
                #                 emp_record.write({'is_on_tour': is_on_tour})
                #                 update_record_log += "## start_rec## tour status  update of date :\t%s\t Employee:\t%s ## end_rec##" % (
                #                     emp_record.attendance_recorded_date, emp_record.employee_id.name)
                #             except Exception as e:
                #                 print(str(e))
                #                 error_log += "\n %s, %s:\t%s" % (emp_record.employee_id.name, emp_record.attendance_recorded_date, str(e))
                #                 continue

            except Exception as e:
                # print(str(e))
                error_log += "\nError while updating leave/tour status \nError Msg:\t%s" % (str(e))
                pass

            # #insert into log table -- and if error log exists send mail to configured email-id
            if error_log:
                try:
                    self.env['kw_kwantify_integration_log'].sudo().create(
                        {'name': 'Attendance Employee update leave / tour status',
                         'error_log': error_log,
                         'update_record_log': update_record_log,
                         'request_params': f"Leave: generate_days_with_from_and_to_date({start_date},{end_date}), Tour: get_tour_data({start_date},{end_date})",
                         'response_result': f"Leave: {leave_data} "
                         })  # , Tour : {tour_data}
                except Exception as e:
                    logging.exception(f"message, {e}")
                    pass
