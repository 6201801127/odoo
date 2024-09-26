# -*- coding: utf-8 -*-
# ########################
# Update History
# change attendance sync status to False, Updated On : 21-Oct-2020 , By : T Ketaki Debadarshini
# permission to Attendance manager to apply request for any employee, employee and attendance request date duplication validation removed, Updated On : 30-Nov-2020 , By : T Ketaki Debadarshini

# ########################
import pytz
from datetime import date, datetime, timedelta
import re
from lxml import etree
import uuid

from odoo import tools
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.addons.resource.models import resource

MAX_DAYS_FOR_APPLY = 35


class EmployeeApplyAttendance(models.Model):
    _name = 'kw_employee_apply_attendance'
    _description = 'Attendance Correction Request'
    _rec_name = 'employee_id'

    # _inherit        = ["mail.thread"]

    def _default_access_token(self):
        return uuid.uuid4().hex

    access_token = fields.Char('Access Token', default=_default_access_token)

    applied_for = fields.Selection(string="Applied By", selection=[('self', 'Self'), ('others', 'Others')],
                                   required=True, default='self')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU", related="employee_id.user_id.branch_id",
                                store=True)

    department_id = fields.Many2one(string='Department', comodel_name='hr.department',
                                    related="employee_id.department_id")
    designation_id = fields.Many2one(string='Designation', comodel_name='hr.job', related="employee_id.job_id")
    # branch_location      = fields.Many2one('kw_location_master', string="Location",related="branch_id.location",store=True)

    attendance_date = fields.Date(string='Attendance Date', required=True, index=True)
    check_in_datetime = fields.Datetime(string='Office-in Date & Time', required=True)
    check_out_datetime = fields.Datetime(string='Office-out Date & Time', required=True)
    reason = fields.Text(string="Reason", required=True)

    action_taken_by = fields.Many2one('hr.employee', string="Action Taken By", ondelete='cascade')
    authority_remark = fields.Text(string='Remark')
    action_taken_on = fields.Datetime(string='Action Taken On')

    state = fields.Selection(string="Status",
                             selection=[('1', 'Draft'), ('2', 'Applied'), ('3', 'Approved'), ('5', 'Rejected'),
                                        ('6', 'Cancelled')], required=True, default='1')  # ,('4','Approved by HR')

    btn_visibility_status = fields.Boolean(string="Button Visibility", compute="_compute_button_visibility_status")
    cancel_btn_visibility = fields.Boolean(string="Cancel button visibility",
                                           compute="_compute_button_visibility_status")

    attendance_history_id = fields.Many2one(
        string='Daily Attendance History Id',
        comodel_name='kw_daily_employee_attendance', compute="_compute_attendance_entries"
    )

    shift_id = fields.Many2one('resource.calendar', string="Assigned Shift ", related="attendance_history_id.shift_id")
    shift_name = fields.Char("Shift Name", related="shift_id.name", store=False)
    shift_in = fields.Char("Shift In Time Display", related="attendance_history_id.shift_in", store=False)
    shift_out = fields.Char("Shift Out Time Display", related="attendance_history_id.shift_out", store=False)
    shift_in_time = fields.Float(string="Shift In Time", related="attendance_history_id.shift_in_time")
    shift_out_time = fields.Float(string="Shift Out Time", related="attendance_history_id.shift_out_time")
    is_cross_shift = fields.Boolean(string="Is Cross Shift", related="attendance_history_id.is_cross_shift")

    attendance_log_ids = fields.Many2many(
        string='Daily Attendance Log',
        comodel_name='hr.attendance', compute="_compute_attendance_entries",
    )
    portal_login_ids = fields.Many2many(string='Portal Log-in Log', comodel_name='user_login_detail',
                                        compute="_compute_attendance_entries", )
    request_for = fields.Char("Request For", compute="_compute_attendance_entries", store=False)

    def _compute_button_visibility_status(self):
        for rec in self:
            emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).ids
            # print(self.env.uid,rec.employee_id.parent_id.id,emp_ids,rec.employee_id.parent_id.id in emp_ids)
            eos_con = self._context.get('hr_eos_att_request')
            if eos_con:
                rec.btn_visibility_status = True
                rec.cancel_btn_visibility = True
            else:
                rec.btn_visibility_status = True if rec.employee_id.parent_id.id in emp_ids and rec.state == '2' else False  # self.env.user.has_group('hr_attendance.group_hr_attendance_manager') and rec.state== '3' or

                rec.cancel_btn_visibility = True if rec.create_uid.id == self.env.uid else False

    @api.depends('attendance_date', 'employee_id', 'check_in_datetime', 'check_out_datetime')
    def _compute_attendance_entries(self):
        for rec in self:
            if rec.attendance_date and rec.employee_id:
                rec.attendance_history_id = self.env['kw_daily_employee_attendance'].search(
                    [('employee_id', '=', rec.employee_id.id), ('attendance_recorded_date', '=', rec.attendance_date)],
                    limit=1).id

                rec.attendance_log_ids = self.env['hr.attendance'].search(
                    [('employee_id', '=', rec.employee_id.id), ('check_in', '>=', rec.attendance_date),
                     ('check_in', '<=', rec.attendance_date)]).ids

                rec.portal_login_ids = self.env['user_login_detail'].search(
                    [('user_id', '=', rec.employee_id.user_id.id), ('date_time', '>=', rec.attendance_date),
                     ('date_time', '<=', rec.attendance_date)]).ids
                request_for = 'All Day'
                if rec.attendance_history_id and rec.check_in_datetime and rec.check_out_datetime:
                    if not rec.attendance_history_id.check_in or (
                            rec.attendance_history_id.check_in and rec.attendance_history_id.check_in.strftime(
                        '%Y-%m-%d %H:%M') != rec.check_in_datetime.strftime('%Y-%m-%d %H:%M')):
                        request_for = 'Office-in'
                    if not rec.attendance_history_id.check_out or (
                            rec.attendance_history_id.check_out and rec.attendance_history_id.check_out.strftime(
                        '%Y-%m-%d %H:%M') != rec.check_out_datetime.strftime('%Y-%m-%d %H:%M')):
                        request_for = 'Office-out' if request_for != 'Office-in' else 'All Day'
                rec.request_for = request_for

    @api.constrains('attendance_date', 'employee_id')
    def date_validation(self):
        for record in self:
            if record.attendance_date and (datetime.now().date() - record.attendance_date).days > MAX_DAYS_FOR_APPLY:
                raise ValidationError(f"Attendance date should not be older than {MAX_DAYS_FOR_APPLY} days.")

            # if record.attendance_date and record.employee_id:

            #     attendance_record_exist = self.env['kw_employee_apply_attendance'].search([('employee_id','=',record.employee_id.id),('attendance_date','=',record.attendance_date),('state','not in',['5','6'])]) - self

            #     if attendance_record_exist:
            #         raise ValidationError(f'Attendance record already exists on the requested date for "{record.employee_id.name}".')           

            if record.attendance_date and record.attendance_date > datetime.now().date():
                raise ValidationError("Attendance date should not be earlier than today's date")

    """method to check validation for attendance datetime of employee"""

    def check_date_validation(self, employee_id, attendance_date=False, check_in_datetime=False,
                              check_out_datetime=False):
        if employee_id and attendance_date:
            daily_attendance = self.env['kw_daily_employee_attendance']
            emp_tz = employee_id.tz or employee_id.shift_id.tz or 'UTC'

            attendance_history_id = daily_attendance.search(
                [('employee_id', '=', employee_id.id), ('attendance_recorded_date', '=', attendance_date)], limit=1)

            shift_in_time = attendance_history_id.shift_in_time if attendance_history_id else False
            shift_out_time = attendance_history_id.shift_out_time if attendance_history_id else False
            is_cross_shift = attendance_history_id.is_cross_shift if attendance_history_id else False

            if not attendance_history_id:
                shift_info = daily_attendance._get_employee_shift(employee_id, attendance_date)
                shift_in_time = shift_info[4] if shift_info else False
                shift_out_time = shift_info[5] if shift_info else False
                is_cross_shift = shift_info[3].cross_shift if shift_info else False

            if check_in_datetime:
                # # check-in datetime in employee timezone
                in_datetime_emp_tz = check_in_datetime.astimezone(pytz.timezone(emp_tz))

                # print(in_datetime_emp_tz.replace(tzinfo=None))

                if check_in_datetime > datetime.now():
                    raise ValidationError('"Office in date-time" should be less than current date-time.')

                elif attendance_date != in_datetime_emp_tz.replace(tzinfo=None).date() and not is_cross_shift:
                    raise ValidationError('"Office in date" must be same as "Attendance Requested Date".')

                elif shift_out_time:
                    office_out_datetime = datetime.combine(
                        attendance_date if not is_cross_shift else attendance_date + timedelta(1),
                        resource.float_to_time(shift_out_time))
                    out_datetime_emp_tz = pytz.timezone(emp_tz).localize(office_out_datetime)
                    utc_out_datetime = out_datetime_emp_tz.astimezone(pytz.timezone('UTC'))

                    if check_in_datetime > utc_out_datetime.replace(tzinfo=None):
                        raise ValidationError('"Office-in time" should be less than shift out time.')

                if is_cross_shift and (in_datetime_emp_tz.replace(tzinfo=None).date() - attendance_date).days > 1:
                    raise ValidationError('Invalid "Office In" Date.')

            if check_out_datetime:
                if check_in_datetime and check_out_datetime < check_in_datetime:
                    raise ValidationError('"Office-out" time cannot be earlier than "Office In" time.')

                if not (self.applied_for == 'others' and self.env.user.has_group(
                        'hr_attendance.group_hr_attendance_manager')):
                    if check_out_datetime > datetime.now():
                        raise ValidationError('"Office-out time" should be less than current date-time.')

                out_datetime_emp_tz = check_out_datetime.astimezone(pytz.timezone(emp_tz))

                if attendance_date != out_datetime_emp_tz.replace(tzinfo=None).date() and not is_cross_shift:
                    raise ValidationError('"Office out date" should be same as "Attendance Requested Date".')

                if is_cross_shift and (out_datetime_emp_tz.replace(tzinfo=None).date() - attendance_date).days > 1:
                    raise ValidationError('Invalid "Office Out" Date.')

    @api.constrains('check_in_datetime', 'check_out_datetime', 'attendance_date', 'employee_id')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            attendance.check_date_validation(attendance.employee_id, attendance.attendance_date,
                                             attendance.check_in_datetime, attendance.check_out_datetime)

            # if attendance.check_in_datetime and attendance.check_out_datetime:

            #     if attendance.attendance_date and not attendance.is_cross_shift:
            #         if attendance.check_in_datetime.date() != attendance.attendance_date or attendance.check_out_datetime.date() != attendance.attendance_date:
            #             raise ValidationError('"Office In/ Out" time must be same as the "attendance requested date".')

            #     elif attendance.attendance_date and attendance.is_cross_shift:
            #         if (attendance.check_in_datetime.date() - attendance.attendance_date).days >1 or (attendance.check_out_datetime.date() - attendance.attendance_date).days >1:
            #             raise ValidationError('Invalid "Office In/ Out" time .')

    @api.onchange('applied_for')
    def _get_employee(self):
        emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.applied_for == "others":
            self.employee_id = False

            # print(self.env.user.has_group('hr_attendance.group_hr_attendance_manager'))
            if not self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
                return {'domain': {'employee_id': ([('parent_id', 'in', emp_ids.ids)])}}
            else:
                return {'domain': {'employee_id': ([])}}
        else:

            self.employee_id = emp_ids.id
            return {'domain': {'employee_id': ([('id', 'in', emp_ids.ids)])}}

    @api.onchange('attendance_date', 'employee_id')
    def _get_check_inout_time(self):
        if self.attendance_date and self.employee_id and self.attendance_history_id:
            self.check_in_datetime, self.check_out_datetime = False, False
            self.check_in_datetime = self.attendance_history_id.check_in
            self.check_out_datetime = self.attendance_history_id.check_out

    @api.constrains('reason')
    def validate_reason(self):
        for record in self:
            if re.match("^[a-zA-Z0-9/\s\+-.()]+$", record.reason) == None:
                raise ValidationError("Please remove special characters from reason")

    @api.constrains('authority_remark')
    def validate_authority_remark(self):
        for record in self:
            if record.authority_remark and re.match("^[a-zA-Z0-9/\s\+-.,_()]+$", record.authority_remark) == None:
                raise ValidationError("Please remove special characters from remark")

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        result = super(EmployeeApplyAttendance, self).create(values)

        # for attendance_request in result:
        # if self.env.user.has_group('hr_attendance.group_hr_attendance_manager') :
        #     result.write({'state':'4','action_taken_by':self.env.user.employee_ids.id,'authority_remark':'Application auto-approved by Attendance Manager','action_taken_on':datetime.now()})

        #     ##create daily attendance for those info
        #     result.create_daily_attendance()
        # else:
        for attendance_request in result:
            if attendance_request.applied_for == 'others' and (
                    attendance_request.employee_id.parent_id.user_id == self.env.user or self.env.user.has_group(
                    'hr_attendance.group_hr_attendance_manager')):
                attendance_request.write({'state': '3', 'action_taken_by': self.env.user.employee_ids.id,
                                          'authority_remark': 'Application auto-approved.',
                                          'action_taken_on': datetime.now()})

                # #create daily attendance for those info
                attendance_request.create_daily_attendance()
                if attendance_request.state == '3':
                    # mail template for auto approved by RA
                    template = self.env.ref('kw_hr_attendance.kw_attendance_request_approved_email_template')
                    self.env['mail.template'].browse(template.id).send_mail(attendance_request.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                attendance_request.write({'state': '2', 'action_taken_by': attendance_request.employee_id.parent_id.id})
                if attendance_request.state == '2':
                    # mail template for apply the attendance request
                    template = self.env.ref('kw_hr_attendance.kw_apply_attendance_request_email_template')
                    self.env['mail.template'].browse(template.id).with_context(
                        token=attendance_request.access_token).send_mail(attendance_request.id,
                                                                         notif_layout="kwantify_theme.csm_mail_notification_light")

        return result

    @api.multi
    def create_daily_attendance(self):
        """
        Added on : 11 March 2021 (Gouranga) create in hr.attendance while manual attendance approved.
        """
        # daily_attendance                = self.env['kw_daily_employee_attendance']

        for rec in self:
            # attendance_date                 = rec.attendance_date
            employee = rec.employee_id
            hr_attendance = self.env['hr.attendance']

            if employee.resource_calendar_id:
                # emp_day_rec             = daily_attendance.search([('attendance_recorded_date','=',attendance_date),('employee_id','=',employee.id)])    

                # #daily_emp_attendance    = self.env['kw_daily_employee_attendance']
                # shift_info              = daily_attendance._get_employee_shift(employee,attendance_date)
                # emp_tz                  = employee.tz or employee.resource_calendar_id.tz or 'UTC' 

                # # day_shift               = ofc_hours.mapped('calendar_id')[0]
                # day_shift               = shift_info[3]
                # shift_second_half_time  = shift_info[6] if shift_info[6] else 0
                # shift_name              = shift_info[7] if shift_info[7] else day_shift.name

                # attendance_data         = {'employee_id':employee.id,'shift_id':day_shift.id,'shift_name':shift_name ,'is_cross_shift':day_shift.cross_shift,'shift_in_time':shift_info[4],'shift_out_time':shift_info[5],'attendance_recorded_date':attendance_date,'check_in':rec.check_in_datetime,'check_in_mode':3,'check_out':rec.check_out_datetime,'check_out_mode':3,'tz':emp_tz,'shift_second_half_time':shift_second_half_time,'kw_sync_status':False}

                # if not emp_day_rec:      
                #     daily_attendance.create(attendance_data)   
                # else:
                #     emp_day_rec.write(attendance_data)
                hr_attendance.create({'employee_id': employee.id,
                                      'branch_id': employee.user_id and employee.user_id.branch_id and employee.user_id.branch_id.id or False,
                                      'check_in': rec.check_in_datetime,
                                      'check_out': rec.check_out_datetime,
                                      'check_in_mode': 3,
                                      })

            else:
                raise ValidationError(
                    f'There is no shift assigned for "{employee.name}". \n Please assign shift to the employee(s) before proceeding for manual attendance request')

    # #approve the request
    @api.multi
    def approve_attendance_request(self):
        return self.call_approval_wizard('approve')

    # #reject the request
    @api.multi
    def reject_attendance_request(self):
        if not self.authority_remark:
            raise UserError("Please enter remark.")

        return self.call_approval_wizard('reject')

    @api.multi
    def cancel_attendance_request(self):
        return self.call_approval_wizard('cancel')

    @api.multi
    def call_approval_wizard(self, action_type):
        for attendance_request_rec in self:
            approval_wiz = self.env['kw_employee_attendance_approval_wizard'].create(
                {'action_type': action_type, 'attendance_request_ids': [[6, 'false', [attendance_request_rec.id]]],
                 'remark': attendance_request_rec.authority_remark})

            if approval_wiz:
                approval_wiz.save_action_details(action_type)

                # print(action_type)
        if action_type == 'cancel' or self._context.get('hr_eos_att_request'):
            model = 'kw_employee_apply_attendance'
            view_id = self.env.ref('kw_hr_attendance.view_kw_employee_apply_attendance_tree').id
            fview_id = self.env.ref('kw_hr_attendance.kw_employee_apply_attendance_view_form').id
            domain = ['|', ('employee_id.user_id.id', '=', self.env.user.id),
                      ('employee_id.parent_id.user_id.id', '=', self.env.user.id)]
            context = {"search_default_filter_current_month": 1, "search_default_filter_my_requests": 1, "edit": False,
                       "import": False}
            views = [(view_id, 'tree'), (fview_id, 'form')]
        else:
            model = 'kw_attendance_request_take_action'
            view_id = self.env.ref('kw_hr_attendance.view_kw_employee_take_action_attendance_tree').id
            domain = [('state', 'in', ['2']), ('employee_id.parent_id.user_id.id', '=', self.env.user.id)]
            context = {'create': False, 'import': False}
            views = [(view_id, 'tree')]

        return {
            'name': 'Attendance Request' if action_type == 'cancel' else 'Attendance Request Approval',
            'type': 'ir.actions.act_window',
            'res_model': model,
            'target': 'main',
            # 'view_type' : view_type,          
            'views': views,
            'context': context,  # ,'no_breadcrumbs': True
            'domain': domain
        }

    @api.multi
    def request_take_action(self):
        self.ensure_one()
        view_id = self.env.ref('kw_hr_attendance.kw_employee_apply_attendance_view_form').id
        return {
            'name': 'Employee Attendance Approval Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_employee_apply_attendance',
            'target': 'same',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': self.id,
            'flags': {'mode': 'edit', },
            'context': {'create': False}
        }

    @api.constrains('employee_id')                                                
    def attendance_mode_validation(self):
        emp_atten = self.env['kw_attendance_request_take_action']
        for rec in self:
            attendance_record = emp_atten.sudo().search([('employee_id','=',rec.employee_id.id),('attendance_date','=',rec.attendance_date),('state','in',['2'])])
            if attendance_record:
                raise ValidationError("You cannot Apply Attendance Twice for the same Date.")

# #class to take action for the attendance request, Created By : T Ketaki Debadarshini, On : 12-Nov-2020
class AttendanceRequestAction(models.Model):
    _name = "kw_attendance_request_take_action"
    _description = "Attendance Request Take Action"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'id desc'

    app_request_id = fields.Many2one('kw_employee_apply_attendance', string="Attendance Request Id")
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', )
    branch_id = fields.Many2one(string='Branch', comodel_name='kw_res_branch', )
    attendance_date = fields.Date(string='Attendance Date', )

    department_id = fields.Many2one(string='Department', comodel_name='hr.department',
                                    related="employee_id.department_id")
    designation_id = fields.Many2one(string='Designation', comodel_name='hr.job', related="employee_id.job_id")

    check_in_datetime = fields.Datetime(string='Office-in Date & Time', related="app_request_id.check_in_datetime")
    check_out_datetime = fields.Datetime(string='Office-out Date & Time', related="app_request_id.check_out_datetime")
    create_date = fields.Datetime(string='Applied On')
    reason = fields.Text(string="Reason", related="app_request_id.reason")
    btn_visibility_status = fields.Boolean(string="Button Visibility", compute="_compute_button_visibility_status")
    request_for = fields.Char("Request For", related="app_request_id.request_for")
    state = fields.Selection(string="Status",
                             selection=[('1', 'Draft'), ('2', 'Applied'), ('3', 'Approved'), ('5', 'Rejected'),
                                        ('6', 'Cancelled')])

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            
            SELECT id,id as app_request_id,employee_id,branch_id,attendance_date,state,create_date         
            FROM kw_employee_apply_attendance WHERE state in ('2')       

        )""" % (self._table))  # ,'3'

    def _compute_button_visibility_status(self):
        for rec in self:
            emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).ids
            eos_con = self._context.get('hr_eos_att_request')
            if eos_con:
                rec.btn_visibility_status = True
            else:
                rec.btn_visibility_status = True if rec.employee_id.parent_id.id in emp_ids and rec.state == '2' else False

    @api.multi
    def request_take_action(self):
        self.ensure_one()
        view_id = self.env.ref('kw_hr_attendance.kw_employee_apply_attendance_view_form').id
        return {
            'name': 'Employee Attendance Approval Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_employee_apply_attendance',
            'target': 'same',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': self.id,
            'flags': {'mode': 'edit', },
            'context': {'create': False}

        }

