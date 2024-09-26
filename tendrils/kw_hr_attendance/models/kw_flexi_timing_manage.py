# -*- coding: utf-8 -*-
# ########################
# Modification History :

# 03-Jul-2020 : End Date removed from global leaves, By : T Ketaki Debadarshini

# ########################
from datetime import datetime
from ast import literal_eval
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'


    def _get_default_employee(self):
        if self._context.get('hide_emp'):
            return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
        else:
            return False
    
    # branch_id               = fields.Many2one(string ='Branch ', comodel_name='kw_res_branch', ondelete='restrict')
    employee_id = fields.Many2one('hr.employee', string="Employee",default=_get_default_employee )

    first_half_hour_from = fields.Float(string='First Half Start Time')
    first_half_hour_to = fields.Float(string='First Half End Time')
    rest_hour = fields.Float(string='Rest Time')
    second_half_hour_from = fields.Float(string='Second Half Start Time')
    second_half_hour_to = fields.Float(string='Second Half End Time')

    attendance_ids = fields.One2many('resource.calendar.attendance', 'calendar_id', 'Working Time',
                                     copy=True, default=False)
    select_flexi_hrs = fields.Selection([('30min','+30.min'),('45min','+45.min'),('60min','+60.min'),('90min','+90.min')])
    btn_visibility_status = fields.Boolean(string="Button Visibility", compute="_compute_button_visibility_status")
    state =  fields.Selection([('draft', 'Draft'),('apply', 'Apply'), ('approved', 'Approved'),('reject','Rejected')],default='draft')
    approved_by = fields.Many2one('hr.employee', string="Approved By")
    flexi_reason = fields.Text("Reason")
    ra_remark = fields.Text("Remark")

    @api.constrains('select_flexi_hrs')
    def check_flexi_add_on(self):
        if self.select_flexi_hrs == False:
            raise ValidationError('Please choose Flexi hours.')


    def _compute_button_visibility_status(self):
        for rec in self:
            emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).ids
            user_chck = self._context.get('hr_eos_att_request')
            if user_chck:
                rec.btn_visibility_status = True
            else:
                rec.btn_visibility_status = True if rec.employee_id.parent_id.id in emp_ids  else False  # self.env.user.has_group('hr_attendance.group_hr_attendance_manager') and rec.state== '3' or


    @api.multi
    def request_take_action(self):
        self.ensure_one()
        view_id = self.env.ref('kw_hr_attendance.view_resource_user_calendar_form').id
        return {
            'name': 'Employee Flexi Shift Approval Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'resource.calendar',
            'target': 'same',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': self.id,
            'flags': {'mode': 'edit', },
            'context': {'create':0,'edit':1}
        }
    


    def apply_flexi_time(self):
        param = self.env['ir.config_parameter'].sudo()
        # record = super(ResourceCalendar, self).create(vals)
        for record in self:
            record.state='apply'
            mail_cc=[]
            core_teams = literal_eval(param.get_param('kw_hr_attendance.hr_core_team_ids') or '[]')
            if core_teams:
                employees = self.env['hr.employee'].search([('id', 'in', core_teams), ('active', '=', True)])
                for employee in employees:
                    mail_cc.append(employee.work_email)
            email_from=record.employee_id.work_email
            email_to = record.employee_id.parent_id.work_email
            emp_name=record.employee_id.name
            emp_code=record.employee_id.emp_code
            emp_parent=record.employee_id.parent_id.name
            dept_head = record.employee_id.department_id.manager_id.work_email if record.employee_id.department_id.manager_id else False
            functional_authority = record.employee_id.coach_id.work_email if record.employee_id.coach_id else False

            # div_head = record.employee_id.division.manager_id.work_email if record.employee_id.division.manager_id else False
            sbu_representative = record.employee_id.sbu_master_id.representative_id.work_email if record.employee_id.sbu_master_id else False
            if dept_head:
                mail_cc.append(dept_head)
            # if div_head:
            #     mail_cc.append(div_head)
            if functional_authority:
                mail_cc.append(functional_authority)
            if sbu_representative:
                mail_cc.append(sbu_representative)
            cc_emails = ",".join(set(mail_cc))
            extra_params= {'email_to':email_to,'emp_name':emp_name,'emp_code':emp_code,'emp_parent':emp_parent,
            'email_from':email_from,'mail_cc': cc_emails,'record': record,
            }
            self.env['hr.contract'].contact_send_custom_mail(res_id=record.id,
                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                            template_layout='kw_hr_attendance.kw_flexi_shift_apply_email_template',
                                            ctx_params=extra_params,
                                            description="Flexi Time Request")
            self.env.user.notify_success("Flexi Time Request Sent Successfully.")
            return record

    def approve_resource_flexi_shift(self):
        param = self.env['ir.config_parameter'].sudo()
        for rec in self:
            if rec:
                self.action_assign_flexi()
                rec.write({
                    'state' : 'approved',
                    'approved_by':self.employee_id.parent_id.id,
                })
            mail_cc=[]
            mail_cc += rec.employee_id.coach_id.mapped('work_email')

            core_teams = literal_eval(param.get_param('kw_hr_attendance.hr_core_team_ids') or '[]')
            if core_teams:
                employees = self.env['hr.employee'].search([('id', 'in', core_teams), ('active', '=', True)])
                for employee in employees:
                    mail_cc.append(employee.work_email)
            email_from=rec.employee_id.parent_id.work_email
            email_to = rec.employee_id.work_email
            dept_head = rec.employee_id.department_id.manager_id.work_email if rec.employee_id.department_id.manager_id else False
            # div_head = rec.employee_id.division.manager_id.work_email if rec.employee_id.division.manager_id else False
            sbu_representative = rec.employee_id.sbu_master_id.representative_id.work_email if rec.employee_id.sbu_master_id else False
            if dept_head:
                mail_cc.append(dept_head)
            # if div_head:
            #     mail_cc.append(div_head)
            if sbu_representative:
                mail_cc.append(sbu_representative)
            cc_emails = ",".join(set(mail_cc))
            extra_params= {'email_to':email_to,
            'email_from':email_from,'mail_cc': cc_emails,'record_id': rec.id,
            }
            self.env['hr.contract'].contact_send_custom_mail(res_id=self.id,
                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                            template_layout='kw_hr_attendance.kw_flexi_shift_approve_email_template',
                                            ctx_params=extra_params,
                                            description="Flexi Time Approved")
            self.env.user.notify_success("Flexi Time Request Approved Successfully.")
            return True
        
    def reject_resource_flexi_shift(self):
        param = self.env['ir.config_parameter'].sudo()
        for rec in self:
            if rec:
                rec.write({
                    'state' : 'reject',
                    'approved_by':self.employee_id.parent_id.id,
                })
            mail_cc=[]
            mail_cc += rec.employee_id.coach_id.mapped('work_email')
            core_teams = literal_eval(param.get_param('kw_hr_attendance.hr_core_team_ids') or '[]')
            if core_teams:
                employees = self.env['hr.employee'].search([('id', 'in', core_teams), ('active', '=', True)])
                for employee in employees:
                    mail_cc.append(employee.work_email)
            email_from=rec.employee_id.parent_id.work_email
            email_to = rec.employee_id.work_email
            dept_head = rec.employee_id.department_id.manager_id.work_email if rec.employee_id.department_id.manager_id else False
            # div_head = rec.employee_id.division.manager_id.work_email if rec.employee_id.division.manager_id else False
            sbu_representative = rec.employee_id.sbu_master_id.representative_id.work_email if rec.employee_id.sbu_master_id else False
            if dept_head:
                mail_cc.append(dept_head)
            # if div_head:
            #     mail_cc.append(div_head)
            if sbu_representative:
                mail_cc.append(sbu_representative)
            cc_emails = ",".join(set(mail_cc))
            extra_params= {'email_to':email_to,
            'email_from':email_from,'mail_cc': cc_emails,'record_id': rec.id,
            }
            self.env['hr.contract'].contact_send_custom_mail(res_id=self.id,
                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                            template_layout='kw_hr_attendance.kw_flexi_shift_reject_email_template',
                                            ctx_params=extra_params,
                                            description="Flexi Time Rejected")
            self.env.user.notify_danger("Flexi Time Rejected.")
            return True

    @api.onchange('employee_id','select_flexi_hrs')
    def get_resource_calendar_details(self):
        thirty,fourty5,sixty,ninty=00.50,00.75,01.00,01.50
        if self.employee_id:
            # print(f"Flexi Timing for {self.employee_id.name} assigned on {datetime.now().date()}")
            self.name = f"Flexi Timing for {self.employee_id.name} assigned on {datetime.now().date()}"
            if self.employee_id.resource_calendar_id:
                employeee_shift = self.employee_id.resource_calendar_id
                self.hours_per_day = employeee_shift.hours_per_day
                self.branch_id = employeee_shift.branch_id
                self.tz = employeee_shift.tz
                self.late_exit_time = employeee_shift.late_exit_time
                self.late_entry_time = employeee_shift.late_entry_time
                self.early_entry_time = employeee_shift.early_entry_time
                self.extra_early_entry_time = employeee_shift.extra_early_entry_time
                self.extra_late_exit_time = employeee_shift.extra_late_exit_time

                self.grace_time = employeee_shift.grace_time
                self.rest_hour = employeee_shift.rest_hour
                self.cross_shift = employeee_shift.cross_shift

                self.late_entry_half_leave_time = employeee_shift.late_entry_half_leave_time
                self.late_entry_full_leave_time = employeee_shift.late_entry_full_leave_time
                self.early_exit_half_leave_time = employeee_shift.early_exit_half_leave_time
                if self.select_flexi_hrs and self.select_flexi_hrs=='30min':
                    self.first_half_hour_from = employeee_shift.first_half_hour_from + thirty
                    self.first_half_hour_to = employeee_shift.first_half_hour_to + thirty
                    self.second_half_hour_from = employeee_shift.second_half_hour_from + thirty
                    self.second_half_hour_to = employeee_shift.second_half_hour_to + thirty
                elif self.select_flexi_hrs and self.select_flexi_hrs=='45min':
                    self.first_half_hour_from = employeee_shift.first_half_hour_from + fourty5
                    self.first_half_hour_to = employeee_shift.first_half_hour_to + fourty5
                    self.second_half_hour_from = employeee_shift.second_half_hour_from + fourty5
                    self.second_half_hour_to = employeee_shift.second_half_hour_to + fourty5
                elif self.select_flexi_hrs and self.select_flexi_hrs=='60min':
                    self.first_half_hour_from = employeee_shift.first_half_hour_from + sixty
                    self.first_half_hour_to = employeee_shift.first_half_hour_to + sixty
                    self.second_half_hour_from = employeee_shift.second_half_hour_from + sixty
                    self.second_half_hour_to = employeee_shift.second_half_hour_to + sixty
                elif self.select_flexi_hrs and self.select_flexi_hrs=='90min':
                    self.first_half_hour_from = employeee_shift.first_half_hour_from + ninty
                    self.first_half_hour_to = employeee_shift.first_half_hour_to + ninty
                    self.second_half_hour_from = employeee_shift.second_half_hour_from + ninty
                    self.second_half_hour_to = employeee_shift.second_half_hour_to + ninty
                self.attendance_ids = False
                # print("Check--",self.hours_per_day,employeee_shift.hours_per_day)

    @api.constrains('employee_id', 'start_date', 'end_date')
    def check_duplicate(self):
        for record in self:
            # record.check_duplicate_employee()
            record.check_duplicate_date_range()
            if record.employee_id and record.attendance_ids:
                for attendance in record.attendance_ids:
                    if not (attendance.date_from or attendance.date_to):
                        raise ValidationError(f"Please specify both starting date and end date for {attendance.name}. Duration is mandatory for Flexi Time Management")

    @api.multi
    def check_duplicate_employee(self):
        duplicate_rec = self.env['resource.calendar'].search_count(
            [('employee_id', '!=', False), ('employee_id', '=', self.employee_id.id), ('id', '!=', self.id)])

        if duplicate_rec:
            raise ValidationError(f"Flexi Timing has already been assigned for {self.employee_id.name}")

    @api.multi
    def check_duplicate_date_range(self):
        if self.employee_id:
            emp_record = self.env['resource.calendar'].search([('employee_id', '=', self.employee_id.id),('state','!=','reject')]) - self
            duplicate_date_range = emp_record.filtered(lambda r: self.start_date and self.end_date and r.start_date and r.end_date and (r.start_date <= self.start_date <= r.end_date or r.start_date <= self.end_date <= r.end_date))

            if duplicate_date_range:
                raise ValidationError(
                    f'''There is already a Flexi Timing found for {self.employee_id.name} having \n 
                    Start Date : {duplicate_date_range[0].start_date} and  End Date : {duplicate_date_range[0].end_date}''')

    # #action to assign flexi time
    def action_assign_flexi(self):
        if not self.employee_id:
            raise ValidationError("Please select employee.")
        else:
            # self.check_duplicate_employee()
            self.check_duplicate_date_range()

        if not any([self.start_date, self.end_date, self.first_half_hour_from, self.first_half_hour_to,
                    self.second_half_hour_from, self.second_half_hour_to]):
            raise ValidationError("Please enter all the fields required to assign flexi hours (Start Date, End Date, Working Hour Details).")
        elif self.end_date < self.start_date:
            raise ValidationError("End date should not be less than start date.")

        elif self.first_half_hour_from >= self.first_half_hour_to:
            raise ValidationError("First half start time should not be greater than end time.")

        elif self.second_half_hour_from >= self.second_half_hour_to:
            raise ValidationError("Second half start time should not be greater than end time.")

        elif not self.cross_shift and (self.second_half_hour_from < self.first_half_hour_to or self.second_half_hour_from <= self.first_half_hour_from):
            raise ValidationError("Second half should start after first half time.")

            # existing_working_hours = self.attendance_ids.filtered(lambda rec: rec.date_from == self.start_date and rec.date_to == self.end_date) if self.attendance_ids else []

        flexi_working_hours = []
        invalid_data = self.env['resource.calendar.attendance']
        # print(resource_rec)
        # print(self.id)
        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for week_day in range(7):

            first_half_rec = self.attendance_ids.filtered(lambda rec: rec.dayofweek == str(week_day) and rec.day_period == 'morning')
            second_half_rec = self.attendance_ids.filtered(lambda rec: rec.dayofweek == str(week_day) and rec.day_period == 'afternoon')

            first_half_data = {'name': week_days[week_day] + ' First Half',
                               'dayofweek': str(week_day),
                               'hour_from': self.first_half_hour_from,
                               'hour_to': self.first_half_hour_to,
                               'day_period': 'morning',
                               'date_from': self.start_date,
                               'date_to': self.end_date,
                               'rest_time': self.rest_hour}

            second_half_data = {'name': week_days[week_day] + ' Second Half',
                                'dayofweek': str(week_day),
                                'hour_from': self.second_half_hour_from,
                                'hour_to': self.second_half_hour_to,
                                'day_period': 'afternoon',
                                'date_from': self.start_date,
                                'date_to': self.end_date}

            if first_half_rec:
                single_rec = first_half_rec[0]
                invalid_data |= first_half_rec - single_rec
                single_rec.write(first_half_data)
            else:
                flexi_working_hours.append((0, 0, first_half_data))

            if second_half_rec:
                one_record = second_half_rec[0]
                invalid_data |= second_half_rec - one_record
                one_record.write(second_half_data)
            else:
                flexi_working_hours.append((0, 0, second_half_data))

        # print(flexi_working_hours)

        if flexi_working_hours:
            self.attendance_ids = flexi_working_hours

        if invalid_data:
            invalid_data.unlink()

        return
