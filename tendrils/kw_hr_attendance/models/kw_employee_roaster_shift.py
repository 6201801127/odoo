# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import pytz
from odoo.addons.resource.models import resource
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_RWORKING, DAY_STATUS_RHOLIDAY


class EmployeeRoasterShift(models.Model):
    _name = 'kw_employee_roaster_shift'
    _description = 'Employee Roster Shift'
    _rec_name = "employee_id"
    _order = 'date asc'

    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True)
    date = fields.Date(string="Date", required=True, autocomplete="off", index=True)
    shift_id = fields.Many2one('resource.calendar', string="Shift", required=True)
    week_off_status = fields.Boolean(string="Week off")
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU", related="employee_id.user_id.branch_id",
                                store=True)
    # branch_location = fields.Many2one('kw_location_master', string="Location",related="branch_id.location",store=True)

    enable_edit = fields.Boolean(string="Is Current Month Record", compute="_compute_enable_edit", store=False)

    @api.multi
    def _compute_enable_edit(self):
        for roster in self:
            roster.enable_edit = True if (datetime.now().date() - roster.date).days <= 30 else False

    @api.constrains('employee_id', 'date', 'shift_id', 'week_off_status')
    def check_redundancy(self):
        for roaster in self:
            if roaster.employee_id and roaster.date:
                # print(self.env['kw_daily_employee_attendance']._get_employee_shift(roaster.employee_id,roaster.date))

                if (datetime.now().date() - roaster.date).days > 30:
                    raise ValidationError("You can not assign/modify roster shift to more than 30 days older record(s).")

                ers_record = self.env['kw_employee_roaster_shift'].search(
                    [('employee_id', '=', roaster.employee_id.id), ('date', '=', roaster.date)]) - roaster
                if ers_record:
                    raise ValidationError("Shift has been already assigned on selected dates.\n Please change the date duration.")

    # #update the daily attendance table status as per the week off state , in case of backward update/create
    @api.multi
    def change_attendance_status(self):
        """
            update the daily attendance table status as per the week off state , in case of backward update/create  
        """
        for roaster_shift in self:
            if roaster_shift.date <= datetime.now().date():

                attendance_rec = self.env['kw_daily_employee_attendance'].search(
                    [('employee_id', '=', roaster_shift.employee_id.id),
                     ('attendance_recorded_date', '=', roaster_shift.date)])

                roaster_day_status = DAY_STATUS_RHOLIDAY if roaster_shift.week_off_status else DAY_STATUS_RWORKING

                # #if attendnace record is there and shift differs or day status differs then
                if attendance_rec and (roaster_shift.shift_id != attendance_rec.shift_id or attendance_rec.day_status != roaster_day_status):

                    daily_attendance = self.env['kw_daily_employee_attendance']

                    shift_info = daily_attendance._get_employee_shift(roaster_shift.employee_id, roaster_shift.date)

                    shift_id, shift_name, is_cross_shift = shift_info[3].id, shift_info[7], shift_info[3].cross_shift
                    shift_in_time, shift_out_time, shift_second_half_time = shift_info[4], shift_info[5], shift_info[
                        6] if shift_info[6] else 0
                    if shift_info and shift_info[0] == 'roster' and shift_info[3] != roaster_shift.shift_id:

                        timezone = pytz.timezone(attendance_rec.tz or 'UTC')
                        start_dt = datetime.combine(attendance_rec.attendance_recorded_date, resource.float_to_time(0.0))
                        end_dt = datetime.combine(attendance_rec.attendance_recorded_date, resource.float_to_time(23.98))
                        attendance_intervals = False

                        employee_shift = roaster_shift.shift_id
                        attendance_intervals = employee_shift.with_context(
                            employee_id=roaster_shift.employee_id.id)._attendance_intervals(
                            start_dt.replace(tzinfo=timezone), end_dt.replace(tzinfo=timezone), resource=None)
                        all_ofc_hours = self.env['resource.calendar.attendance']
                        exceptional_ofc_hours = self.env['resource.calendar.attendance']
                        regular_ofc_hours = self.env['resource.calendar.attendance']
                        for _, _, rec in attendance_intervals:
                            all_ofc_hours |= rec

                        exceptional_ofc_hours = all_ofc_hours.filtered(lambda rec: rec.date_from and rec.date_to)
                        regular_ofc_hours = all_ofc_hours.filtered(lambda rec: not rec.date_from)

                        ofc_hours = exceptional_ofc_hours if exceptional_ofc_hours else regular_ofc_hours
                        shift_inout_info = daily_attendance._get_shift_in_out_time(ofc_hours)

                        if shift_inout_info:
                            shift_id, shift_name, is_cross_shift = shift_inout_info[0].id, shift_inout_info[0].name, \
                                                                   shift_inout_info[0].cross_shift

                            shift_in_time, shift_out_time, shift_second_half_time = shift_inout_info[1], \
                                                                                    shift_inout_info[2], \
                                                                                    shift_inout_info[3] if \
                                                                                    shift_inout_info[3] else 0

                    # print({'shift_id':shift_id,'shift_name':shift_name,'is_cross_shift':is_cross_shift,'shift_in_time':shift_in_time,'shift_out_time':shift_out_time,'day_status':roaster_day_status,'shift_second_half_time':shift_second_half_time})
                    attendance_rec.write({'shift_id': shift_id,
                                          'shift_name': shift_name,
                                          'is_cross_shift': is_cross_shift,
                                          'shift_in_time': shift_in_time,
                                          'shift_out_time': shift_out_time,
                                          'day_status': roaster_day_status,
                                          'shift_second_half_time': shift_second_half_time})

                    # print(sss)

                    # #update the log
                    # body        = ("The attendance record of <b>%s</b> for <b>%s</b> has been updated as per the roaster  shift assignment. <b>Action Taken By :</b> %s")%(roaster_shift.employee_id.name,roaster_shift.date,self.env.user.employee_ids.name)        
                    # attendance_rec.message_post(body=body)      

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        result = super(EmployeeRoasterShift, self).create(values)

        # #update the attendance status
        result.change_attendance_status()
        return result

    @api.multi
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """
        result = super(EmployeeRoasterShift, self).write(values)

        # #update the attendance status
        self.change_attendance_status()

        template = self.env.ref('kw_hr_attendance.kw_roster_update_email_template')
        if template:
            for record in self:
                template.send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        return result
