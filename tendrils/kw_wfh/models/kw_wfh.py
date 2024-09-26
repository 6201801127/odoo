# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import pytz
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
import calendar
from time import gmtime, strftime
from ast import literal_eval
import uuid


class kw_employee_status(models.Model):
    _name = 'kw_wfh_employee_status'
    _description = 'WFH Employee status'

    wfh_id = fields.Many2one('kw_wfh', string="Ref", required=True, ondelete='cascade')
    empl_id = fields.Many2one('hr.employee', string="Employee")
    status = fields.Boolean('WFH', default=False)
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')


class WfhAction(models.Model):
    _name = 'kw_wfh_action'
    _description = 'WFH Action status'

    access_token = fields.Char('Invitation Token')
    wfh_id = fields.Many2one('kw_wfh', 'WFH linked', ondelete='cascade')
    ra_id = fields.Many2one('hr.employee', 'Employee', domain=[('user_id', '!=', False)])
    status = fields.Boolean(default=True)


class kw_wfh_mail_data(models.Model):
    _name = 'kw_wfh_mail'
    _description = 'Work From Home'

    record_id = fields.Integer(string='Id')
    name = fields.Char(string='Name')


class kw_wfh(models.Model):
    _name = 'kw_wfh'
    _description = "Work From Home"
    _rec_name = 'ref_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    """ Hide/Show buttons (Grant,Hold,Reject,Cancel) to RA and Finance having group 'group_kw_wfh_user'
            :Applied state: show's approve , Hold , Reject buttons to RA 
            :Grant state: show's Grant , Hold , Reject buttons to Finance 
            :Hide cancel button in applied state in user login view 
            """
    @api.depends('ref_no')
    @api.multi
    def _compute_btn_access(self):
        for record in self:
            if self.env.user.has_group('kw_wfh.group_kw_wfh_user'):
                if record.state == 'applied' and record.env.uid == record.action_to_be_taken_by.user_id.id:
                    record.show_grant_button = True
                if (record.state == 'applied' and record.env.uid != record.employee_id.user_id.id
                        and self.env.context.get('ra_view_loaded')) :
                    record.show_btn_cancel = False
                if record.state == 'applied' and record.env.uid == record.employee_id.user_id.id:
                    record.show_btn_cancel = True
                # if record.state == 'hold' and record.env.uid == record.action_to_be_taken_by.user_id.id:
                #     record.show_grant_button = True
                if (record.state == 'grant' and record.env.uid == record.employee_id.user_id.id
                        and not self.env.context.get('manager_view_loaded')):
                    record.hide_btn_cancel = True
            if self.env.user.has_group('kw_employee.group_hr_ra'):
                if record.state == 'applied' and self.env.user.employee_ids == self.employee_id.parent_id:
                    record.hide_btn_cancel = True
                if record.state == 'grant' and self.env.user.employee_ids == self.employee_id.parent_id:
                    record.show_grant_button = True
            if self.env.user.has_group('kw_wfh.group_kw_wfh_manager'):
                if record.state == 'applied':
                    record.hide_btn_cancel = True
                    record.show_grant_button = True
            manager_context = self.env.context.get('report_view_loaded')
            if manager_context != True:
                record.emp_record_report = True
            if manager_context == True:
                record.hide_btn_cancel = True

    """ hide employee extension record """
    @api.multi
    def _hide_extension_button(self):
        for record in self:
            if (record.request_to_date and date.today() > record.request_to_date) \
                    or record.is_extended \
                    or record.wfh_type == 'others' \
                    or record.state in ['draft', 'cancel', 'reject', 'applied', 'expired']:
                record.hide_extension_record = True

    """ Assign Employee's Department to 'emp_dept_id' field """
    @api.depends('employee_id')
    def get_emp_department_id(self):
        for rec in self:
            rec.emp_dept_id = rec.employee_id.department_id

    """ Assign Employee's Work location to 'emp_job_location_id' field """
    @api.depends('employee_id')
    def get_emp_job_location(self):
        for rec in self:
            rec.emp_job_location_id = rec.employee_id.job_branch_id

    """ Assign 'Total Allowed days' after calculating. 
        :If total leave days = 0 --> 'Total Allowed days' = 'No Limit'
        :If total leave days = 'value' --> 'Total Allowed days' = 'value' 
        """
    @api.depends('no_of_leave_days')
    def _compute_allowed_days(self):
        for rec in self:
            if rec.no_of_leave_days == '0':
                rec.allowed_days = 'No limit'
            if rec.no_of_leave_days != '0':
                rec.allowed_days = rec.no_of_leave_days

    """ Calculate total no of day's in selected date range excluding Saturday and Sunday 
    (Total Day's between From date - To date) for both 'WFH By User' and 'WFH By HR' 
        """
    @api.depends('request_from_date', 'request_to_date',)
    def _compute_days_count(self):
        dt_from = dt_to = act_from_date = act_to_date = False
        for record in self:
            if (self.env.context.get('self_view_loaded') == True or self.env.context.get('ra_view_loaded') == True
                    or self.env.context.get('manager_view_loaded') == True):
                if record.request_from_date and record.request_to_date:
                    act_from_date = record.request_from_date
                    act_to_date = record.request_to_date
                    dt_from = datetime.strptime(str(act_from_date), DEFAULT_SERVER_DATE_FORMAT).date()
                    dt_to = datetime.strptime(str(act_to_date), DEFAULT_SERVER_DATE_FORMAT).date()
            # if self.env.context.get('manager_view_loaded') == True:
            #    if record.from_date and record.to_date:
            #        act_from_date = record.from_date
            #        act_to_date = record.to_date
            #        dt_from = datetime.strptime(str(act_from_date), DEFAULT_SERVER_DATE_FORMAT).date()
            #        dt_to = datetime.strptime(str(act_to_date), DEFAULT_SERVER_DATE_FORMAT).date()
            if dt_from and dt_to and act_from_date and act_to_date:
                daysDiff = str((dt_to - dt_from).days)
                SatAndSun = 0
                dates_btwn = dt_from
                while dates_btwn <= dt_to:
                    if dates_btwn.strftime("%A") == "Saturday":
                        SatAndSun += 1
                    if dates_btwn.strftime("%A") == "Sunday":
                        SatAndSun += 1
                    else:
                        SatAndSun += 0
                    dates_btwn = dates_btwn + timedelta(days=1)
                if act_from_date <= act_to_date:
                    self.days_count = int(daysDiff) - int(SatAndSun) + 1

    # def _compute_action_to_be_taken_by(self):
    #     for record in self:
    #         record.action_to_be_taken_by = record.employee_id.parent_id.id

    # @api.depends()
    def _compute_system_info(self):
        for record in self:
            record.issued_system = record.employee_id.issued_system

    @api.depends('state')
    def _get_state_value(self):
        for record in self:
            if record.state == 'applied':
                record.form_status = 'Pending at RA'
            else:
                record.form_status = dict(record.fields_get(["state"],['selection'])['state']["selection"]).get(record.state)



    """ Initiative by CSM / HR """
    emp_status_ids = fields.One2many('kw_wfh_employee_status', 'wfh_id', string="WFH availed by Employee's")

    search_by = fields.Selection(string="Search Option", selection=[('user', 'By User'), ('hierarchy', 'By Hierarchy')], required=True, default='user')
    searched_user = fields.Many2many('hr.employee', string="Employee")
    department_id = fields.Many2many('hr.department', 'department_kw_wfh_rel', 'dept_id', 'rel_dept_id', string="Department", default=False)
    division = fields.Many2many('hr.department', 'division_kw_wfh_rel', 'div_id', 'rel_div_id', string="Division", default=False)
    section = fields.Many2many('hr.department', 'section_kw_wfh_rel', 'section_id', 'rel_section_id', string="Practice", default=False)
    practise = fields.Many2many('hr.department', 'practise_kw_wfh_rel', 'practise_id', 'rel_practise_id', string="Section", default=False)
    location_type = fields.Selection(string="Location Type", selection=[('all', 'All'), ('location', 'Location Specific')], default='location')
    location_id = fields.Many2many('kw_res_branch', string="Location", track_visibility='onchange')
    loaction_name = fields.Char('Location Name', related='location_id.location.name', store=True)
    # from_date = fields.Date(string='From Date', track_visibility='onchange', index=True)
    # to_date = fields.Date(string='To Date', track_visibility='onchange', index=True)
    """Employee Request """
    reason_id = fields.Many2one('kw_wfh_reason_master', string="Reason", required=True)
    no_of_leave_days = fields.Char(related='reason_id.no_of_days', string="No of allowed WFH days")
    remark = fields.Text(string="Reason Description", track_visibility='onchange')
    ra_remark = fields.Text(string="RA Remark", track_visibility='onchange')
    request_from_date = fields.Date(string='From Date', track_visibility='onchange', index=True)
    request_to_date = fields.Date(string='To Date', track_visibility='onchange', index=True)
    ref_no = fields.Char(string="Ref No", required=True, default="New", readonly="1", track_visibility='onchange')
    old_reff_no = fields.Char(string="Old Ref No", readonly="1")
    # parent_id = fields.Many2one('kw_wfh',string="Parent Id")
    parent_ref_id = fields.Many2one('kw_wfh', string="Parent Ref Id", help="For Extended WFH parent reference id")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    req_department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id')
    req_division_id = fields.Many2one('hr.department', string="Division", related='employee_id.division')
    req_section_id = fields.Many2one('hr.department', string="Practice", related='employee_id.section')
    req_practise_id = fields.Many2one('hr.department', string="Section", related='employee_id.practise')
    employee_code = fields.Char(related='employee_id.emp_code', string="Employee code")
    job_id = fields.Many2one('hr.job', string="Designation", related='employee_id.job_id')
    action_to_be_taken_by = fields.Many2one('hr.employee', string="Action to be taken by")
    # action_to_be_taken_by = fields.Many2one('hr.employee', string="Action to be taken by", compute='_compute_action_to_be_taken_by', store=True)
    action_taken_by = fields.Many2one('hr.employee', string="Action taken by")
    state = fields.Selection([('draft', 'Draft'), ('applied', 'Applied'),
                              ('grant', 'Granted'), ('reject', 'Rejected'),
                              ('cancel', 'Cancelled'), ('expired', 'Expired')], string='Status', default='draft',
                             track_visibility='onchange')
    form_status = fields.Char(string='Status', compute="_get_state_value")
    extension_remark = fields.Text(string="Extension Remark", track_visibility='onchange')
    revised_to_date = fields.Date(string='Revised upto', index=True)
    emp_dept_id = fields.Many2one('hr.department', string="Employee Department", compute="get_emp_department_id", store=True)
    emp_job_location_id = fields.Many2one('kw_res_branch', compute="get_emp_job_location", string="Location", store=True)
    wfh_type = fields.Selection(string="Type", selection=[('self', 'Self'), ('others', 'CSM')], default='self')
    emp_id = fields.Many2one('hr.employee', string="Employee")
    allowed_days = fields.Char(string="Maximum Day's Allowed", compute='_compute_allowed_days')
    computer_info = fields.Many2one('kw_system_info', string="Computer Information")
    inter_connectivity = fields.Selection(string="Internet Connection",
                                          selection=[('yes', 'Mobile Data'), ('no', 'Hotspot'),
                                                     ('broadband', 'Broadband')], default='yes')
    vpn_access = fields.Selection(string="VPN Accessibility", selection=[('yes', 'Yes'), ('no', 'No')], default='yes')
    citrix_access = fields.Selection(string="Citrix Accessibility Required?", selection=[('yes', 'Yes'), ('no', 'No')], default='no')
    days_count = fields.Char(string="Total days", compute='_compute_days_count', store=True, track_visibility='onchange')
    current_task_emp_id = fields.Many2one('kw_wfh', string="Current Task Employee Id", default=lambda self: self.env.context.get('current_record_id'))
    """ remark action on button """
    action_remark = fields.Text(string="Remarks", track_visibility='onchange')
    approved_on = fields.Date(string="Approved On", track_visibility='onchange')
    approved_by = fields.Char(string="Approved By", track_visibility='onchange')

    """ hide/show button """
    show_btn_cancel = fields.Boolean(compute='_compute_btn_access', string="Show Cancel Button", default=False)
    hide_btn_cancel = fields.Boolean(compute='_compute_btn_access', string="hide Cancel Button", default=False)
    show_apply_btn = fields.Boolean(string="Show Apply Button")
    show_apply_extension_btn = fields.Boolean(string="Show Apply Extension Button", default=False)
    show_hr_grant_button = fields.Boolean(string="Show Grant Button")
    show_hr_extension_button = fields.Boolean(string="Show Extension Button")
    show_grant_button = fields.Boolean(compute='_compute_btn_access')
    hide_extension_grant_btn = fields.Boolean(string="Hide Employee grant button", default=False)
    hide_hr_request_record = fields.Boolean(string="Hide Hr request Record", default=False)
    hide_emp_request_record = fields.Boolean(string="Hide Employee request Record", default=False)
    hide_extension_record = fields.Boolean(string="Hide Employee request Record(Apply Extension Button)", compute='_hide_extension_button')
    hide_csm_wfh_extended_record = fields.Boolean(string="Hide CSM WFH Extended Record", default=False)
    hide_csm_initiated_record = fields.Boolean(string="Hide CSM Initiated Record", default=False)
    wfh_active_link = fields.Boolean(string="WFH active link", default=False)
    hr_wfh_active_link = fields.Boolean(string="HR WFH active link", default=False)
    wfh_end_process = fields.Boolean(string="WFH End Process", default=False)
    hide_expired_record = fields.Boolean(string="Hide Expired Record", default=False)
    is_extended = fields.Boolean(string="Is Extended", default=False)
    show_wfh_record = fields.Boolean(string="Show Wfh Record", default=False)
    is_record_created = fields.Boolean(string="Is Record Created", store=True, readonly=True)
    hr_created_wfh_active_link = fields.Boolean(string="HR created WFH active record", default=False)
    """HR initiate record parent id"""
    manager_created_record_id = fields.Many2one('kw_wfh', string="Manager Created Record Id")
    emp_record_report = fields.Boolean(compute='_compute_btn_access', string="Employee Task", default=False)
    filter_hr_record = fields.Boolean(string="Filter HR Record", default=False)
    previous_attendance_mode_ids = fields.Many2many('kw_attendance_mode_master', 'previous_attendance_mode_ids_wfh_rel',
                                                    'mode_ids', 'current_mode_ids',
                                                    string="Previous Attendance Mode Ids")
    """ Actual From date and To date of the WFH record
    :Actual From Date - updated on applying WFH request
    :Actual To Date - updated on expiring of WFH request (Expires manually by RA/HR or by Scheduler)
    """
    act_from_date = fields.Date(string='Actual From Date', track_visibility='onchange', index=True)
    act_to_date = fields.Date(string='Actual To Date', track_visibility='onchange', index=True)
    employee_wfh_details = fields.Text('Employee WFH details', store=True)

    """Employee Related Attendance Mode"""
    attendance_mode_ids = fields.Many2many('kw_attendance_mode_master', related='employee_id.attendance_mode_ids',
                                           string="Attendance mode")
    process_id = fields.Many2one('kw_wfh_hr_process')
    issued_system = fields.Selection(string='Computer Allocated',
                                     selection=[('aio', 'AIO'), ('pc', 'Desktop'), ('laptop', 'Laptop')],
                                     compute='_compute_system_info')

    def generate_days_with_from_and_to_date(self, from_date, to_date):
        date_list = []
        delta = to_date - from_date
        for i in range(delta.days + 1):
            day = from_date + timedelta(days=i)
            date_list.append(day)
        return date_list

    def get_work_from_home_data(self, start_date, end_date):
        data_dict = {}
        granted_wfhs = self.search(['&', '&', ('state', 'in', ['grant', 'expired']), ('employee_id', '!=', False),
                                    '|',
                                    '&', ('request_from_date', '>=', start_date), ('request_from_date', '<=', end_date),
                                    '&', ('request_to_date', '>=', start_date), ('request_to_date', '<=', end_date)])
        employees = granted_wfhs.mapped('employee_id')
        for emp in employees:
            data_dict[emp.id] = {work_date: False for work_date in self.generate_days_with_from_and_to_date(start_date, end_date)}
            corresponding_records = granted_wfhs.filtered(lambda r: r.employee_id == emp).sorted(key=lambda r: r.request_from_date)

            for wfh_record in corresponding_records:
                for emp_date in self.generate_days_with_from_and_to_date(wfh_record.request_from_date, wfh_record.request_to_date):
                    if emp_date in data_dict[emp.id]:
                        data_dict[emp.id][emp_date] = True
        return data_dict

    """ 
        :Store's Actual From date from Selected From date in WFH By HR / WFH By User
        :Create a Refference No of record
        :Fire's a Validation if there is WFH record in the selected Date Range in both WFH By HR / WFH By User
        """
    @api.model
    def create(self, vals):
        if vals.get('request_from_date'):
            vals['act_from_date'] = vals.get('request_from_date')
        # if vals.get('from_date'):
            # vals['act_from_date'] = vals.get('from_date')
        if self.env.context.get('manager_view_loaded'):
            vals['wfh_type'] = 'others'
        if vals.get('manager_created_record_id'):
            vals['ref_no'] = self.browse(vals.get('manager_created_record_id')).ref_no
        if vals.get('ref_no', 'New') == 'New':
            vals['ref_no'] = self.env['ir.sequence'].next_by_code('kw_wfh_sequence') or '/'
        active_emp_record = self.sudo().search([('employee_id', '=', self.env.user.employee_ids.id),
                                                ('state', 'not in', ['expired', 'cancel', 'reject']),
                                                ('request_to_date', '!=', False),
                                                ('request_from_date', '!=', False)])
        """Initiate by HR """
        manager_context = self.env.context.get('manager_view_loaded')
        """Extend of WFH"""
        extended_view = self.env.context.get('extended_record')

        """WFH extend by user"""
        if active_emp_record and not manager_context and not extended_view \
                and vals.get('request_to_date') and vals.get('request_from_date'):
            applied_from_date = datetime.strptime(vals.get('request_from_date'), '%Y-%m-%d').date()
            applied_to_date = datetime.strptime(vals.get('request_to_date'), '%Y-%m-%d').date()
            for record in active_emp_record:
                if (applied_from_date <= record.request_from_date and applied_to_date >= record.request_to_date) \
                        or (applied_from_date >= record.request_from_date and applied_to_date <= record.request_to_date) \
                        or (record.request_from_date <= applied_from_date <= record.request_to_date <= applied_to_date) \
                        or (applied_from_date <= record.request_from_date <= applied_to_date <= record.request_to_date):
                    raise ValidationError(f"You cannot apply WFH From {applied_from_date.strftime('%d-%b-%Y')} to {applied_to_date.strftime('%d-%b-%Y')}.\n You already have a WFH application from {record.request_from_date.strftime('%d-%b-%Y')} to {record.request_to_date.strftime('%d-%b-%Y')}.")
        """WFH extend by User"""
        if vals.get('revised_to_date') and extended_view:
            active_emp_record = self.env['kw_wfh'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id),
                                                                  ('state', 'not in', ['expired', 'cancel', 'reject']),
                                                                  ('id', '!=', vals.get('parent_ref_id'))])
            revise_to_date = datetime.strptime(vals.get('revised_to_date'), '%Y-%m-%d').date()
            searched_record = self.browse(vals.get('parent_ref_id'))
            if active_emp_record:
                for record in active_emp_record:
                    if record.request_from_date <= revise_to_date <= record.request_to_date \
                            or searched_record.request_to_date <= record.request_from_date <= revise_to_date >= record.request_to_date:
                        raise ValidationError(f"You cannot apply WFH Extension till {revise_to_date.strftime('%d-%b-%Y')} as your WFH application is from {record.request_from_date.strftime('%d-%b-%Y')} to {record.request_to_date.strftime('%d-%b-%Y')}")
        """ update from date and to date on extension """
        if self.env.context.get('extended_record'):
            request_to_date = self.browse(vals.get('parent_ref_id')).request_to_date
            extend_from_date = datetime.strptime(str(request_to_date), '%Y-%m-%d').strftime('%Y-%m-%d')
            date_time_obj = datetime.strptime(extend_from_date, '%Y-%m-%d').date() + timedelta(days=1)
            if date_time_obj.strftime("%A") == "Saturday":
                date_time_obj = date_time_obj + timedelta(days=1)
            if date_time_obj.strftime("%A") == "Sunday":
                date_time_obj = date_time_obj + timedelta(days=1)
            vals['request_to_date'] = vals.get('revised_to_date')
            vals['request_from_date'] = date_time_obj
        return super(kw_wfh, self).create(vals)

    @api.onchange('request_from_date', 'request_to_date')
    def onchange_days(self):
        """ Fire a validation if To date is less than From date """
        for record in self:
            if (self.env.context.get('self_view_loaded') == True or self.env.context.get('ra_view_loaded') == True
                    or self.env.context.get('manager_view_loaded') == True):
                if record.request_from_date and record.request_to_date and record.request_from_date > record.request_to_date:
                    return {'warning': {
                        'title': _('Validation Error'),
                        'message': _('To Date cannot be less than From Date')
                    }}
            # if self.env.context.get('manager_view_loaded') == True:
            #    if record.from_date and record.to_date and record.from_date > record.to_date:
            #        return {'warning': {
            #            'title': _('Validation Error'),
            #            'message': _('To Date cannot be less than From Date')
            #        }}

    """ On calling the method
        :WFH record send to RA (RA id stored in 'action_to_be_taken_by' field)
        :Employee's Department,Division,Section,Practise,location gets populated
        :'to_date','from_date' fields is populated to filter record based on from date and to date
        :'filter_hr_record' is set TRUE to hide record in WFH by HR menu
        :WFH request mail send to RA
        """
    @api.model
    def apply_wfh_request(self):
        db_name = self._cr.dbname
        rec = self.employee_id
        rec_id = self.id
        act_id = self.env.ref('kw_wfh.kw_wfh_requset_takeaction_window').id
        # hod_email = self.employee_id.department_id.manager_id.work_email
        attendance = self.env['kw_daily_employee_attendance'].search(
            [('employee_id', '=', self.employee_id.parent_id.id), ('attendance_recorded_date', '=', datetime.today().date())])
        if attendance and attendance.status == 'On Leave':
            ra_id = self.employee_id.parent_id.parent_id
        else:
            ra_id = self.employee_id.parent_id
        self.sudo().write({'state': 'applied',
                           'department_id': [(6, 0, [rec.department_id.id])] if rec.department_id.id else '',
                           'division': [(6, 0, [rec.division.id])] if rec.division.id else '',
                           'section': [(6, 0, [rec.section.id])] if rec.section.id else '',
                           'practise': [(6, 0, [rec.practise.id])] if rec.practise.id else '',
                           'searched_user': [(6, 0, [rec.id])] if rec.id else '',
                           'location_id': [(6, 0, [rec.job_branch_id.id])] if rec.job_branch_id.id else '',
                           'filter_hr_record': True,
                           'action_to_be_taken_by': ra_id.id,
                           })
        # 'form_status': 'applied',

        token = uuid.uuid4().hex
        rec = self.env['kw_wfh_action'].sudo().create({
            'access_token': token,
            'wfh_id': self.id,
            'ra_id': ra_id.id,
            'status': True,
        })
        template_id = self.env.ref('kw_wfh.kw_wfh_emp_request_mail_template')
        template_id.with_context(rec_id=rec_id, 
            act_id=act_id, 
            db_name=db_name,
            token=token,
            mailto=ra_id.work_email,
            rsvp=ra_id.name).send_mail(rec_id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Work from home request applied successfully.")

    """ on calling this method
        :WFH record send to RA (RA id stored in 'action_to_be_taken_by' field)
        :Employee's Department,Division,Section,Practise,location gets populated
        :'to_date','from_date' fields is populated to filter record based on from date and to date
        :'request_from_date' updated to next working day.
        :'request_to_date' updated to Revised to date
        :'filter_hr_record' is set TRUE to hide record in WFH by HR menu
        :WFH request mail send to RA 
        """
    def apply_wfh_extension(self):
        # db_name = self._cr.dbname
        act_id = self.env.ref('kw_wfh.kw_wfh_requset_takeaction_window').id
        rec = self.employee_id
        # self.parent_ref_id.hide_extension_record = True
        hod_email = self.employee_id.department_id.manager_id.work_email
        # extend_from_date = self.request_to_date + timedelta(days=1)
        # if extend_from_date.strftime("%A") == "Saturday":
        #     extend_from_date = extend_from_date + timedelta(days=1)
        # if extend_from_date.strftime("%A") == "Sunday":
        #     extend_from_date = extend_from_date + timedelta(days=1)
        self.sudo().write({
            'state': 'applied',
            'action_to_be_taken_by': self.env.user.employee_ids.parent_id.id,
            # 'form_status': 'applied',
            # 'request_from_date': extend_from_date,
            # 'request_to_date': self.revised_to_date,
            # 'department_id': [(6, 0, [rec.department_id.id])] if rec.department_id.id else '',
            # 'division': [(6, 0, [rec.division.id])] if rec.division.id else '',
            # 'section': [(6, 0, [rec.section.id])] if rec.section.id else '',
            # 'practise': [(6, 0, [rec.practise.id])] if rec.practise.id else '',
            # 'searched_user': [(6, 0, [rec.id])] if rec.id else '',
            # 'location_id': [(6, 0, [rec.job_branch_id.id])] if rec.job_branch_id.id else '',
            'filter_hr_record': True,
            'hide_emp_request_record': True,
        })
        token = uuid.uuid4().hex
        rec = self.env['kw_wfh_action'].sudo().create({
            'access_token': token,
            'wfh_id': self.id,
            'ra_id': self.employee_id.parent_id.id,
            'status': True,
        })
        template_id = self.env.ref('kw_wfh.kw_wfh_emp_extension_request_mail_template')
        template_id.with_context(rec_id=self.id, act_id=act_id, db_name=self._cr.dbname,
                                 token=token).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Extension for work from home applied successfully.")

    """ Redirect RA Take action form view (show's WFH request Details )"""
    @api.multi
    def request_take_action(self):
        view_id = self.env.ref('kw_wfh.kw_wfh_requset_takeaction_form').id
        target_id = self.id
        action = {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_wfh',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
            'context': {'default_show_btn_cancel': False,
                        'default_hide_extension_grant_btn': False,
                        'default_hide_btn_cancel': True},
        }
        return action

    """ Redirect to Employee report tree view (shows list of employee's)"""
    @api.multi
    def view_employee_list(self):
        view_id = self.env.ref('kw_wfh.kw_wfh_employee_report_tree').id
        target_id = self.id
        action = {
            'name': 'WFH: Employee List',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_wfh',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'tree')],
            'target': 'self',
            'view_id': view_id,
            'context': {},
            'domain': [('manager_created_record_id', '=', self.id)]
        }
        return action

    """ Restrict user on applying WFH when
        :To date < From date
        :From date is past date when back date is not enabled
        :Back date selected is not in the current month range 
        :Days between selected date range is > Total allowed days 
        """
    @api.constrains('request_from_date', 'request_to_date')
    def validate_request_date(self):
        for record in self:
            fmt = '%Y-%m-%d'
            today_date = date.today()
            from_date = record.request_from_date
            to_date = record.request_to_date
            dt_from = datetime.strptime(str(from_date), fmt)
            dt_to = datetime.strptime(str(to_date), fmt)
            daysDiff = str((dt_to - dt_from).days)
            SatAndSun = 0
            if from_date > to_date:
                raise ValidationError("From date should be less than To date.")
            if self.env.context.get('self_view_loaded') == True or self.env.context.get('ra_view_loaded') == True:
                if record.request_from_date and record.request_to_date and record.request_from_date > record.request_to_date:
                    raise ValidationError("From date should be less than To date")
            if self.env.context.get('is_validated') and not self.env.context.get('extended_record'):
                if record.reason_id.reason and not record.reason_id.back_date:
                    if from_date < today_date:
                        raise ValidationError("Starting date cannot be a past date.")
                if record.reason_id.reason and record.reason_id.back_date:
                    """First day of month"""
                    # dt_month_first_date = date.today() - timedelta(days=date.today().day - 1)
                    dt_month_first_date = today_date.replace(day=1)
                    if from_date < dt_month_first_date or to_date < dt_month_first_date:
                        raise ValidationError("Back date can only be select within current month range")
                if record.allowed_days != 'No limit':
                    dates_btwn = dt_from
                    while dates_btwn <= dt_to:
                        dates_btwn = dates_btwn + timedelta(days=1)
                        if (dates_btwn.strftime("%A") == "Saturday"):
                            SatAndSun += 1
                        elif (dates_btwn.strftime("%A") == "Sunday"):
                            SatAndSun += 1
                        else:
                            SatAndSun += 0
                    if int(daysDiff) - int(SatAndSun) > int(record.allowed_days) - 2:
                        raise ValidationError(f"You cannot apply for more than {record.allowed_days} days")

    """ Restrict manager on initiating WFH when 
        :To date < From date
        :From date is past date when back date is not enabled
        :Back date selected is not in the current month range 
        """
    # @api.constrains('from_date', 'to_date')
    # def from_date_validation(self):
    #     for record in self:
    #         if self.env.context.get('manager_view_loaded') == True:
    #             if record.from_date and record.to_date and record.from_date > record.to_date:
    #                 raise ValidationError("From date should be less than To date")
    #         if record.from_date and not record.request_to_date:
    #             today_date = date.today()
    #             from_date = record.from_date
    #             to_date = record.to_date

    #             if record.reason_id.reason and not record.reason_id.back_date and from_date < today_date:
    #                 raise ValidationError("Starting date cannot be a past date or current date")
    #             if record.reason_id.reason and record.reason_id.back_date:
    #                 """First day of month"""
    #                 # dt_month_first_date = date.today() - timedelta(days=date.today().day - 1)
    #                 dt_month_first_date = today_date.replace(day=1)
    #                 if from_date < dt_month_first_date or to_date < dt_month_first_date:
    #                     raise ValidationError("Back date can only be select within current month range")

    """ Restrict User/Manager on extension of WFH when Revised date < To date """
    @api.onchange('request_to_date', 'revised_to_date')
    def date_validation(self):
        for record in self:
            if record.revised_to_date:
                # if record.to_date and not record.request_to_date:
                if record.request_to_date >= record.revised_to_date:
                    raise ValidationError("Revised date cannot be less or equal To date")
                # if record.request_to_date and not record.to_date:
                #     if record.request_to_date >= record.revised_to_date:
                #         raise ValidationError("Revised date cannot be less or equal to requested To date")

    """ On calling the Method
        :Hierarchy wise selection: show's list of employee with thier wfh status and date
        """
    @api.onchange('request_from_date', 'request_to_date', 'department_id', 'division', 'section', 'practise',
                  'location_id', 'revised_to_date')
    def _populate_employees(self):
        if self.request_from_date and self.request_to_date and not self.searched_user:
            # self.searched_user = False
            domain = []
            if self.search_by == 'hierarchy':
                if self.department_id:
                    domain.append(('department_id', 'in', self.department_id.ids))
                if self.division:
                    domain.append(('division', 'in', self.division.ids))
                if self.section:
                    domain.append(('section', 'in', self.section.ids))
                if self.practise:
                    domain.append(('practise', 'in', self.practise.ids))
            if self.location_id:
                domain.append(('job_branch_id', 'in', self.location_id.ids))
            emp_ids = self.env['hr.employee'].sudo().search(domain)
            wfh_domain = [('state', '=', 'grant'), ('filter_hr_record', '=', True), ('employee_id', 'in', emp_ids.ids)]
            if not self.revised_to_date:
                wfh_domain += ['|', '|',
                               '&', ('request_from_date', '<=', self.request_from_date), ('request_to_date', '>=', self.request_from_date),
                               '&', ('request_from_date', '<=', self.request_to_date), ('request_to_date', '>=', self.request_to_date),
                               '&', ('request_from_date', '>=', self.request_from_date), ('request_to_date', '<=', self.request_to_date), ]
            if self.revised_to_date:
                from_date = self.request_to_date + timedelta(days=1)
                wfh_domain += ['|', '|',
                               '&', ('request_from_date', '<=', from_date), ('request_to_date', '>=', from_date),
                               '&', ('request_from_date', '<=', self.revised_to_date), ('request_to_date', '>=', self.revised_to_date),
                               '&', ('request_from_date', '>=', from_date), ('request_to_date', '<=', self.revised_to_date), ]
            wfh_records = self.env['kw_wfh'].sudo().search(wfh_domain)
            if wfh_records and emp_ids:
                # self.searched_user = False
                if self.search_by == 'hierarchy':
                    self.emp_status_ids = [(5, 0, 0)]
                for emp_rec in emp_ids:
                    wfh_rec = wfh_records.filtered(lambda r: r.employee_id == emp_rec)
                    if wfh_rec:
                        if self.search_by == 'hierarchy' and self.location_type == 'location' \
                                or self.search_by == 'hierarchy' and self.location_type == 'all':
                            for record in wfh_rec:
                                self.emp_status_ids = [(0, 0, {'empl_id': record.employee_id, 'status': True,
                                                               'from_date': record.request_from_date,
                                                               'to_date': record.request_to_date})]
            return {'domain': {'searched_user': [('id', 'in', emp_ids.ids)]}}

    """ On calling the Method
        :Employee wise selection: show's list of selected employee with their wfh status and date
        """
    @api.onchange('searched_user', 'revised_to_date')
    def _fetch_active_wfh(self):
        if self.request_from_date and self.request_to_date and self.searched_user:
            self.emp_status_ids = [(5, 0, 0)]
            wfh_domain = [('state', '=', 'grant'), ('filter_hr_record', '=', True), ('employee_id', 'in', self.searched_user.ids)]
            if not self.revised_to_date:
                wfh_domain += ['|', '|',
                               '&', ('request_from_date', '<=', self.request_from_date), ('request_to_date', '>=', self.request_from_date),
                               '&', ('request_from_date', '<=', self.request_to_date), ('request_to_date', '>=', self.request_to_date),
                               '&', ('request_from_date', '>=', self.request_from_date), ('request_to_date', '<=', self.request_to_date), ]
            if self.revised_to_date:
                from_date = self.request_to_date + timedelta(days=1)
                wfh_domain += ['|', '|',
                               '&', ('request_from_date', '<=', from_date), ('request_to_date', '>=', from_date),
                               '&', ('request_from_date', '<=', self.revised_to_date), ('request_to_date', '>=', self.revised_to_date),
                               '&', ('request_from_date', '>=', from_date), ('request_to_date', '<=', self.revised_to_date), ]
            wfh_records = self.env['kw_wfh'].sudo().search(wfh_domain)
            for emp_rec in wfh_records:
                self.emp_status_ids = [(0, 0, {'empl_id': emp_rec.employee_id, 'status': True,
                                               'from_date': emp_rec.request_from_date,
                                               'to_date': emp_rec.request_to_date})]

    @api.onchange('department_id')
    def onchange_department(self):
        dept_child = self.mapped("department_id.child_ids")
        self.division &= dept_child
        return {'domain': {'division': [('id', 'in', dept_child.ids)]}}

    @api.onchange('division')
    def onchange_division(self):
        division_child = self.mapped("division.child_ids")
        self.section &= division_child
        return {'domain': {'section': [('id', 'in', division_child.ids)]}}

    @api.onchange('section')
    def onchange_section(self):
        section_child = self.mapped("section.child_ids")
        self.practise &= section_child
        return {'domain': {'practise': [('id', 'in', section_child.ids)]}}

    """ On onchange of 'search_by','location_type','location_id'
        :Hierarchy wise: populate list of employee's present in the selected Hierarchy (irrespective of location)
        :User wise: populate all employee's (irrespective of location) 
        """
    @api.onchange('search_by', 'location_type', 'location_id')
    def onchange_search_by(self):
        if self.search_by == 'user':
            self.department_id = False
            self.division = False
            self.section = False
            self.practise = False
        if self.location_type == 'all':
            self.location_id = False
        if self.search_by == 'user' and self.location_type == 'location':
            self.emp_status_ids = False

    """ Returns list of emails of all employee's present in IT and admin group ('group_kw_onboarding_nsa','group_kw_onboarding_admin') 
    with comma separated format
        """
    @api.multi
    def get_IT_Admin_users_mail(self):
        # hr_user_group = self.env.ref('kw_employee.group_hr')
        nsa_user_group = self.env.ref('kw_onboarding.group_kw_onboarding_nsa')
        admin_user_group = self.env.ref('kw_onboarding.group_kw_onboarding_admin')
        all_mails = False
        if nsa_user_group.users or admin_user_group.users:
            # or hr_user_group.users
            authority_nsa_emps = self.env['hr.employee'].sudo().search([('user_id', 'in', nsa_user_group.users.ids)])
            authority_admin_emps = self.env['hr.employee'].sudo().search([('user_id', 'in', admin_user_group.users.ids)])
            if authority_nsa_emps or authority_admin_emps:
                nsa_emails = authority_nsa_emps.mapped('work_email')
                admin_emails = authority_admin_emps.mapped('work_email')
                nsa = ','.join(nsa_emails)
                admin = ','.join(admin_emails)
                all_mails = nsa + ',' + admin
        return all_mails

    """ Returns list of emails of all employee's present in HR email notification 
    ('WFH General setting') and Employee's HOD Email in comma separated format"""
    @api.multi
    def emp_request_cc(self):
        emp_cc_mail_list = []
        param = self.env['ir.config_parameter'].sudo()
        if self.employee_id.department_id.manager_id:
            emp_cc_mail_list += self.employee_id.department_id.manager_id.mapped('work_email')
        if self.employee_id.coach_id:
            emp_cc_mail_list += self.employee_id.coach_id.mapped('work_email')
        cc_hr_mails = param.get_param('kw_wfh.hr_email')
        cc_group_mails = literal_eval(param.get_param('kw_wfh.notification_cc_ids'))
        all_jobs = self.env['hr.job'].browse(cc_group_mails)
        if cc_group_mails:
            empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)])
            if empls:
                emp_cc_mail_list += [emp.work_email for emp in empls if emp.work_email]
        if cc_hr_mails and cc_hr_mails != "False":
            emp_cc_mail_list += cc_hr_mails.split(',')
        return ','.join(set(emp_cc_mail_list))

    """ Return list of emails of all employee's present in IT and admin group 
    ('group_kw_onboarding_nsa','group_kw_onboarding_admin') ,
        Employee's HOD email with comma separated format
        """
    @api.multi
    def emp_grant_cc(self):
        unique_mail_list = []
        unique_mail_list += self.employee_id.coach_id.mapped('work_email')
        unique_mail_list += self.employee_id.department_id.manager_id.mapped('work_email')
        param = self.env['ir.config_parameter'].sudo()
        cc_notify = param.get_param('kw_wfh.cc_notification_email')
        authority_nsa_emps = self.env['hr.employee'].sudo().search([('user_id', 'in', self.env.ref('kw_onboarding.group_kw_onboarding_nsa').users.ids)])
        authority_admin_emps = self.env['hr.employee'].sudo().search([('user_id', 'in', self.env.ref('kw_onboarding.group_kw_onboarding_admin').users.ids)])
        if authority_nsa_emps:
            unique_mail_list += [mail.work_email for mail in authority_nsa_emps if mail.work_email not in unique_mail_list]
        if authority_admin_emps:
            unique_mail_list += [mail.work_email for mail in authority_admin_emps if mail.work_email not in unique_mail_list]
        if cc_notify and cc_notify != "False":
            unique_mail_list.append(cc_notify)
        return ','.join(unique_mail_list)

    """ Returns list of emails of all employee's present in IT and admin group 
    ('group_kw_onboarding_nsa','group_kw_onboarding_admin') ,Employee's RA email, Employee's HOD,HR email with 
    comma separated format 
        """
    @api.multi
    def ra_end_cc(self):
        param = self.env['ir.config_parameter'].sudo()
        total_count_days = param.get_param('kw_wfh.count_days') if param.get_param('kw_wfh.count_days') else 15
        unique_mail_list = []
        """Notify RA in CC"""
        emp_ra_mail = self.employee_id.parent_id.work_email
        if emp_ra_mail:
            unique_mail_list.append(emp_ra_mail)

        if total_count_days and int(total_count_days) < int(self.days_count):
            unique_mail_list += self.employee_id.department_id.manager_id.mapped('work_email')

            authority_nsa_emps = self.env['hr.employee'].sudo().search([('user_id', 'in', self.env.ref('kw_onboarding.group_kw_onboarding_nsa').users.ids)])
            authority_admin_emps = self.env['hr.employee'].sudo().search([('user_id', 'in', self.env.ref('kw_onboarding.group_kw_onboarding_admin').users.ids)])
            cc_mail_list = param.get_param('kw_wfh.hr_email')
            cc_group_mails = literal_eval(param.get_param('kw_wfh.notification_cc_ids'))
            all_jobs = self.env['hr.job'].browse(cc_group_mails) if cc_group_mails else False

            if authority_nsa_emps:
                unique_mail_list += [mail.work_email for mail in authority_nsa_emps if mail.work_email not in unique_mail_list]
            if authority_admin_emps:
                unique_mail_list += [mail.work_email for mail in authority_admin_emps if mail.work_email not in unique_mail_list]
            if all_jobs:
                empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)])
                if empls:
                    unique_mail_list += empls.mapped('work_email')
            if cc_mail_list and cc_mail_list != "False":
                unique_mail_list += cc_mail_list.split(',')
        return ','.join(set(unique_mail_list))

    """ Return's list of emails of all employee's present in HR group('group_hr') """
    @api.multi
    def get_hr_users_mail(self):
        hr_user_group = self.env.ref('kw_employee.group_hr')
        if hr_user_group.users:
            authority_hr_emps = self.env['hr.employee'].sudo().search([('user_id', 'in', hr_user_group.users.ids)])
            if authority_hr_emps:
                hr_emails = authority_hr_emps.mapped('work_email')
                return ','.join(hr_emails)

    """ Returns Employee's HOD email """
    @api.multi
    def get_emp_hod_users_mail(self):
        if self.req_department_id:
            hod_mail = self.req_department_id.manager_id.work_email
            return hod_mail

    """ Returns list of emails of all employee's present in RA group('group_hr_ra')"""
    @api.multi
    def get_ra_mail(self):
        ra_user_group = self.env.ref('kw_employee.group_hr_ra')
        if ra_user_group.users:
            authority_ra_emps = self.env['hr.employee'].sudo().search([('user_id', 'in', ra_user_group.users.ids)])
            if authority_ra_emps:
                ra_emails = authority_ra_emps.mapped('work_email')
                return ','.join(ra_emails)

    """ Returns email of all HOD's email selected in department field """
    @api.multi
    def get_hod_users_mail(self):
        hod_mail_list = []
        if self.department_id:
            hod_mail_list += [rec.manager_id.work_email for rec in self.department_id]
            return ','.join(hod_mail_list)

    """ On calling the method
        :Restrict the user for applying extension for the second time with same reference no
        :Redirect to extension form view with default populated field values.
         """
    @api.multi
    def request_extension(self):
        self.env.context.get('is_extended')
        records = self.sudo().search([('employee_id', '=', self.env.user.employee_ids.id)])
        if records:
            for rec in records:
                if rec.old_reff_no and rec.state == 'draft':
                    raise ValidationError("You cannot apply again for same reference number.")
        view_id = self.env.ref('kw_wfh.kw_wfh_requset_extension_form').id
        action = {
            'name': 'Apply Extension',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_wfh',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
            'context': {'default_old_reff_no': self.ref_no,
                        'default_request_from_date': self.request_from_date,
                        'default_request_to_date': self.request_to_date,
                        'default_remark': self.remark,
                        'default_reason_id': self.reason_id.id,
                        'default_req_department_id': self.req_department_id.id,
                        'default_req_division_id': self.req_division_id.id,
                        'default_req_section_id': self.req_section_id.id,
                        'default_req_practise_id': self.req_practise_id.id,
                        'default_employee_code': self.employee_code,
                        'default_employee_id': self.employee_id.id,
                        'default_show_apply_extension_btn': True,
                        'default_hide_emp_request_record': False,
                        'default_hide_extension_grant_btn': False,
                        'default_show_btn_cancel': True,
                        'default_parent_ref_id': self.id,
                        'default_job_id': self.job_id.id,
                        'default_emp_id': self.emp_id.id,
                        'extended_record_id': self.id,
                        'extended_record': True,
                        'default_computer_info': self.computer_info.id,
                        'default_inter_connectivity': self.inter_connectivity,
                        # 'default_vpn_access': self.vpn_access,
                        'default_citrix_access': self.citrix_access},
        }
        return action

    """ On calling the method
        :Redirect to extension form view with default populated field values.
         """
    @api.multi
    def wfh_link_extension(self):
        self.env.context.get('is_extended')
        user_list = []
        current_employee_ids = self.env['kw_wfh'].sudo().search(
            [('employee_id', 'in', self.searched_user.ids), ('manager_created_record_id', '=', self.id),
             ('state', '!=', 'expired')])
        if current_employee_ids:
            user_list += [rec.employee_id.id for rec in current_employee_ids]
        view_id = self.env.ref('kw_wfh.kw_wfh_initiative_extension_by_csm_form').id
        action = {
            'name': 'Extend WFH Link',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_wfh',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
            'context': {'default_old_reff_no': self.ref_no,
                        'default_search_by': self.search_by,
                        'default_request_from_date': self.request_from_date,
                        'default_request_to_date': self.request_to_date,
                        'default_remark': self.remark,
                        'default_reason_id': self.reason_id.id,
                        'default_department_id': [(6, 0, self.department_id.ids)],
                        'default_division': [(6, 0, self.division.ids)],
                        'default_section': [(6, 0, self.section.ids)],
                        'default_practise': [(6, 0, self.practise.ids)],
                        'default_location_type': self.location_type,
                        'default_location_id': [(6, 0, self.location_id.ids)],
                        'default_show_apply_btn': False,
                        'default_show_hr_extension_button': True,
                        'default_hide_hr_request_record': False,
                        'default_parent_ref_id': self.id,
                        'default_searched_user': [(6, 0, user_list)],
                        },
        }
        return action

    """ 'Employee WFH request end-process'
        It fetches all the active Employee's WFH records present in grant state and compares ,
        If today's date matched with any record's to date then it check whether the current day is the employee's
        working day or holiday.
        If the current day is the employee's holiday then it check if the time is > 22:59:59 then expire's the active WFH,
        change the attendance mode ids to existing attendance mode ids and send mail to the employee's RA,HOD,HR,IT,ADMIN.
        If the current day is the employee's working day then it checks if the Employee's Shift time is < the current time then expire's the active WFH,
        change the attendance mode ids to existing attendance mode ids and send mail to the employee's RA,HOD,HR,IT,ADMIN.
        """
    @api.model
    def _wfh_end_process(self):
        """ Mail Data List"""
        employee_name_list = []
        reason_list = []
        location_ids_list = []
        """ HR initiated Mail @from"""
        mail_from = 'tendrils@csm.tech'
        """ WFH Status for Employee in Mail"""
        mail_context = {'action': 'Closed'}
        """wfh_active_link : for fetch all 'grant' state records"""
        current_date = date.today()
        dept_list = {}
        ra_list = {}
        department_list = []
        rec_dept_list = []
        attn_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
        """Fetch all active WFH records"""
        mail_model_id = self.env['kw_wfh_mail'].browse(1)
        wfh_records = self.env['kw_wfh'].sudo().search(['&','|',
                                                        '&','&',('request_to_date', '<=', current_date),('wfh_active_link','=',False),('wfh_type','=','others'),
                                                        '&',('request_to_date', '<=', current_date),('wfh_type','=','self'),
                                                        ('state', '=', 'grant')])
        # print('wfh_records ..... ', wfh_records)
        for rec in wfh_records:
            """Employee timezone """
            timezone = pytz.timezone(rec.employee_id.tz)
            datestring = datetime.now
            tz_user_time = datestring(timezone)
            emp_current_time = str(tz_user_time.hour) + ':' + str(tz_user_time.minute) + ':' + str(tz_user_time.second)
            emp_current_hour = float(tz_user_time.hour)
            # print('tz_user_time >>> ', tz_user_time)
            user_mail = rec.employee_id.work_email
            username = rec.employee_id.name
            emp_code = rec.employee_id.emp_code
            hod_user_mail = rec.req_department_id.manager_id.work_email
            ra_mail = rec.employee_id.parent_id.work_email
            """ HR Initiated Records"""
            if rec.wfh_type == 'others' and not rec.wfh_active_link:
                """ 'HR record end-process'
                It fetches all the active HR WFH records present in grant state and compares ,
                If today's date matched with any record's to date then it check whether the current day is the employee's
                working day or holiday.
                If the current day is the employee's holiday then it check if the time is > 21:59:59 then expire the active WFH/
                If the current day is the employee's working day then it checks 
                if the Employee's Shift time is < the current time then expire the active WFH.
                """
                child_ids = self.env['kw_wfh'].sudo().search([('manager_created_record_id', '=', rec.id)])
                parent_expire_flag = True
                """ counter is used for fetching departments """
                counter = 0
                if rec.department_id and not rec.division and not rec.section and not rec.practise:
                    department_list = rec.department_id.mapped('name')
                    counter = 1
                elif rec.department_id and rec.division and not rec.section and not rec.practise:
                    department_list = rec.division.mapped('name')
                    counter = 2
                elif rec.department_id and rec.division and rec.section and not rec.practise:
                    department_list = rec.section.mapped('name')
                    counter = 3
                else:
                    department_list = rec.practise.mapped('name')
                    counter = 4
                for child in child_ids:
                    emp_shift_info = self.env['kw_daily_employee_attendance']._compute_day_status(child.employee_id, current_date)
                    shift_out_hour = emp_shift_info[4] if emp_shift_info[4] else False

                    """ 2 - Holiday as shift info not found for user"""
                    if ((emp_shift_info[0] and emp_shift_info[0] == '2' and emp_current_time > '21:59:59')
                            or (shift_out_hour <= emp_current_hour)):
                        """ close WFH child record """
                        self._close_record(child)
                        if not rec.is_extended:
                            self.env.ref('kw_wfh.kw_wfh_employees_end_process_email_template').with_context(
                                mail_context,
                                emp_name=child.employee_id.name,
                                emp_code=child.employee_id.emp_code,
                                mail_to=child.employee_id.work_email,
                                mail_from=mail_from).send_mail(child.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                            employee_name_list.append(child.employee_id)
                            reason_list.append({"reason": child.reason_id.reason})
                            location_ids_list.append(child.employee_id.job_branch_id.alias)
                            """ fetching departments using counter """
                            rec_dept_list += [child.department_id.name] if counter == 1 else [child.division.name] if counter == 2 else [child.section.name] if counter == 3 else [child.practise.name]
                            """ dictionary containing parameters to passed in mail context """
                            dept = child.employee_id.department_id
                            ra = child.employee_id.parent_id
                            """Dept dict"""
                            if not dept_list.get(dept.id) and dept.manager_id.name and dept.manager_id.work_email:
                                dept_list.update({dept.id: {'to_name': dept.manager_id.name,
                                                            'to_email': dept.manager_id.work_email,
                                                            'dept_name': dept.name, 'rec_id': rec.id,
                                                            'searched_user': rec.searched_user if rec.searched_user else '',
                                                            'search_by': rec.search_by if rec.search_by else '',
                                                            'rec_dept': set(rec_dept_list) if rec_dept_list else ''}})
                            """RA dict"""
                            if ra.id not in ra_list.keys() and ra.name and ra.work_email:
                                ra_list.update({ra.id: {'to_name': ra.name, 'to_email': ra.work_email,
                                                        'dept_name': ra.department_id.name, 'rec_id': rec.id,
                                                        'searched_user': rec.searched_user if rec.searched_user else '',
                                                        'search_by': rec.search_by if rec.search_by else '',
                                                        'rec_dept': set(rec_dept_list) if rec_dept_list else ''}})
                        """ Remove attendance mode ids """
                        self._remove_mode_id(child, attn_mode)
                    else:
                        parent_expire_flag = False
                if parent_expire_flag:
                    self._close_hr_record(rec)
            """ User Initiated Records  2 – Holiday(shift value), 0 – Regular Working Day(shift)"""
            if rec.wfh_active_link and not rec.manager_created_record_id:
                # rec.wfh_type == 'self' and
                emp_shift_info = self.env['kw_daily_employee_attendance']._compute_day_status(rec.employee_id, current_date)
                shift_out_hour = emp_shift_info[4] if emp_shift_info[4] else False
                """ 2 – Holiday as shift info not found for user"""
                if ((emp_shift_info[0] and emp_shift_info[0] == '2' and emp_current_time > '21:59:59')
                        or (shift_out_hour <= emp_current_hour)):
                    """ close WFH user record """
                    self._close_record(rec)
                    if not rec.is_extended:
                        self.env.ref('kw_wfh.kw_wfh_employees_end_process_by_ra_email_template').with_context(
                            mail_context,
                            mail_from=mail_from,
                            emp=username,
                            emp_code=emp_code,
                            mail_to=user_mail,
                            ra_mail=ra_mail,
                            hod_user_mail=hod_user_mail).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                    """ Remove attendance mode ids """
                    self._remove_mode_id(rec, attn_mode)
        """ Mail Section """
        employees_ids = []
        if employee_name_list:
            employees_ids = list(set(employee_name_list))
        unique_location_ids_list = []
        if location_ids_list:
            location_ids_list = list(set(location_ids_list))
            unique_location_ids_list += [record for record in location_ids_list if record != False]
        joined_location_ids = ','.join(unique_location_ids_list)
        if employees_ids:
            """ mail to IT, ADMIN """
            it_email_ids = self.get_IT_Admin_users_mail()
            if it_email_ids != None:
                self.env.ref('kw_wfh.kw_wfh_schedular_It_admin_end_process_email_template').with_context(mail_context, 
                                                                                                        emp_name=employees_ids, 
                                                                                                        mail_from=mail_from,
                                                                                                        mail_to=it_email_ids,
                                                                                                        dept_ids=','.join(set(department_list)), 
                                                                                                        joined_location_ids=joined_location_ids).send_mail(mail_model_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            """ mail to HR """
            self.env.ref('kw_wfh.kw_wfh_schedular_hr_end_process_email_template').with_context(mail_context,
                                                                                               emp_name=employees_ids,
                                                                                               mail_from=mail_from,
                                                                                               dept_ids=','.join(set(department_list)),
                                                                                               joined_location_ids=joined_location_ids).send_mail(mail_model_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            """ Compute HOD and RA Mail Data """
            for emp in employees_ids:
                dept_id = emp.department_id.id
                if dept_list.get(dept_id):
                    if 'child' in dept_list[dept_id].keys():
                        dept_list[dept_id]['child']+=emp
                        if 'location_name' in dept_list[dept_id].keys() and emp.job_branch_id.alias:
                            dept_list[dept_id]['location_name']+=emp.job_branch_id.alias + ', ' if emp.job_branch_id.alias not in dept_list[dept_id]['location_name'] else ''
                    else:
                        dept_list[dept_id]['child'] = emp
                        if emp.job_branch_id.alias:
                            dept_list[dept_id]['location_name'] = emp.job_branch_id.alias + ', '

                if ra_list.get(emp.parent_id.id):
                    if 'child' in ra_list[emp.parent_id.id].keys():
                        ra_list[emp.parent_id.id]['child'] += emp
                        if 'location_name' in ra_list[emp.parent_id.id].keys() and emp.job_branch_id.alias:
                            ra_list[emp.parent_id.id]['location_name']+=emp.job_branch_id.alias + ', ' if emp.job_branch_id.alias not in ra_list[emp.parent_id.id]['location_name'] else ''
                    else:
                        ra_list[emp.parent_id.id]['child'] = emp
                        if emp.job_branch_id.alias:
                            ra_list[emp.parent_id.id]['location_name'] = emp.job_branch_id.alias + ', '
            """mail to HOD """
            if dept_list:
                for val in dept_list.values():
                    self.env.ref('kw_wfh.kw_wfh_schedular_hod_end_process_email_template').with_context(mail_context, 
                                                                                                        mail_from=mail_from,
                                                                                                        emp_name=val.get('child'),
                                                                                                        hod_name=val.get('to_name'),
                                                                                                        hod_dep=val.get('dept_name'),
                                                                                                        mail_to=val.get('to_email'),
                                                                                                        joined_location_ids=val.get('location_name'),
                                                                                                        searched_user=val.get('searched_user'),
                                                                                                        search_by=val.get('search_by'),
                                                                                                        rec_dept=','.join(val.get('rec_dept')),
                                                                                                        ).send_mail(mail_model_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            """mail to RA"""
            if ra_list:
                for val in ra_list.values():
                    self.env.ref('kw_wfh.kw_wfh_schedular_ra_end_process_email_template').with_context(mail_context,
                                                                                                       mail_from=mail_from,
                                                                                                       emp_name=val.get('child'),
                                                                                                       ra_name=val.get('to_name'),
                                                                                                       ra_dept=val.get('dept_name'),
                                                                                                       mail_to=val.get('to_email'),
                                                                                                       joined_location_ids=val.get('location_name'),
                                                                                                       searched_user=val.get('searched_user'),
                                                                                                       search_by=val.get('search_by'),
                                                                                                       rec_dept=','.join(val.get('rec_dept')),
                                                                                                       ).send_mail(mail_model_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        return True

    """ Enables Employee's attendance mode ids to 'Portal' if it is not present 
    and store the existing mode ids to the current WFH record """
    @api.model
    def _enable_wfh(self):
        current_date = date.today()
        query_list = []
        prev_attn_list = []
        emp_list = []
        emp_rec = []
        attn_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
        wfh_granted_record = self.env['kw_wfh'].sudo().search([('wfh_active_link', '=', True),
                                                               ('state', '=', 'grant'),
                                                               ('request_from_date', '<=', current_date),
                                                               ('request_to_date', '>=', current_date)])
        if wfh_granted_record:
            # emp_rec = wfh_granted_record.mapped('employee_id')  # .filtered(lambda r: not r.is_wfh)
            for wfh_rec in wfh_granted_record:
                previous_mode_ids = wfh_rec.employee_id.attendance_mode_ids
                if previous_mode_ids and not wfh_rec.previous_attendance_mode_ids:
                    # wfh_rec.sudo().write({'previous_attendance_mode_ids': [(6, 0, previous_mode_ids.ids)]})
                    for mode in previous_mode_ids:
                        prev_attn_list.append((wfh_rec.id, mode.id))
                if attn_mode.id not in wfh_rec.employee_id.attendance_mode_ids.ids:
                    emp_rec.append(wfh_rec.employee_id.id)
                    query_list.append((wfh_rec.employee_id.id, attn_mode.id))

            if prev_attn_list:
                prev_attn = str(prev_attn_list)[1:-1]
                query = f"INSERT INTO previous_attendance_mode_ids_wfh_rel (mode_ids, current_mode_ids) VALUES {prev_attn} ON CONFLICT DO NOTHING;"
                self._cr.execute(query)
            
            attendance_report = self.env['kw_daily_employee_attendance'].sudo().search(
                [('employee_id', 'in', emp_rec), ('work_mode', '!=', '0'), ('attendance_recorded_date', '=', current_date)])
            if attendance_report:
                attendance_ids = ','.join(str(v) for v in attendance_report.ids)
                query = f"UPDATE kw_daily_employee_attendance SET work_mode=0 WHERE id in ({attendance_ids});"
                self._cr.execute(query)

            if query_list:
                query_list = str(query_list)[1:-1]
                query = f"INSERT INTO hr_employee_kw_attendance_mode_master_rel (hr_employee_id, kw_attendance_mode_master_id) VALUES {query_list} ON CONFLICT DO NOTHING;"
                self._cr.execute(query)

            # print('WFH start scheduler executed successfully.....')
        else:
            # print('No WFH record found.....')
            pass
        return True

    """ Populate Employee name during initialisation """
    @api.model
    def default_get(self, fields):
        if not self.env.user.employee_ids and not self.env.context.get('manager_view_loaded'):
            raise ValidationError("You cannot apply for WFH.")
        res = super(kw_wfh, self).default_get(fields)
        res['employee_id'] = self.env.user.employee_ids.id
        res['emp_id'] = self.env.user.employee_ids.id
        return res

    def assign_daily_task(self):
        kanban_view_id = self.env.ref('kw_wfh.kw_wfh_deliverables_kanban_dashboard').id
        tree_view_id = self.env.ref('kw_wfh.kw_wfh_deliverables_tree').id
        form_view_id = self.env.ref('kw_wfh.kw_wfh_deliverables_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Assign Task',
            'view_mode': 'kanban,form,tree',
            'res_model': 'kw_wfh_deliverables',
            'target': 'self',
            'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form')],
            'context': {'group_by': 'state',
                        'default_employee_id': self.employee_id.id,
                        'default_mail_sent': True,
                        'default_wfh_record_id': self.id},
            'domain': [('create_uid', '=', self.env.user.employee_ids.user_id.id)],
            'search_view_id': (self.env.ref('kw_wfh.ra_search_view_kw_wfh_deliverables').id,)
        }

        return action

    def view_daily_task(self):
        kanban_view_id = self.env.ref('kw_wfh.kw_wfh_emp_deliverables_kanban_dashboard').id
        tree_view_id = self.env.ref('kw_wfh.kw_wfh_deliverables_tree').id
        form_view_id = self.env.ref('kw_wfh.kw_wfh_emp_deliverables_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Daily Task',
            'view_mode': 'kanban,form,tree',
            'res_model': 'kw_wfh_deliverables',
            'target': 'self',
            'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('employee_id.id', '=', self.env.user.employee_ids.id),
                       ('state', 'in', ['assigned', 'inprogress'])],
            'context': {'group_by': 'state'},
            'flags': {'create': False, 'edit': False},
            'search_view_id': (self.env.ref('kw_wfh.search_view_kw_wfh_emp_deliverables_report').id,)
        }

        return action

    """ Return HR emails added in general setting of WFH """
    @api.multi
    def get_hr_email(self):
        param = self.env['ir.config_parameter'].sudo()
        hr_email = param.get_param('kw_wfh.hr_email')
        if hr_email == "False":
            return " "
        else:
            return hr_email

    """ Return HRD emails added in general setting of WFH """
    @api.multi
    def get_hrd_cc_email(self):
        param = self.env['ir.config_parameter'].sudo()
        cc_notify = param.get_param('kw_wfh.cc_notification_email')
        if cc_notify == "False":
            return " "
        else:
            return cc_notify

    def view_task_report(self):
        self.current_task_emp_id = self.env.context.get('current_record_id')
        tree_view_id = self.env.ref('kw_wfh.kw_wfh_deliverables_self_reports_tree').id
        form_view_id = self.env.ref('kw_wfh.kw_wfh_deliverables_self_reports_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Task Report',
            'view_mode': 'tree,form',
            'res_model': 'kw_wfh_deliverables',
            'target': 'self',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('employee_id.id', '=', self.current_task_emp_id.employee_id.id)],
            'flags': {'create': False, 'edit': False, 'delete': False, },
            'search_view_id': (self.env.ref('kw_wfh.search_view_kw_wfh_deliverables').id,)
        }

        return action

    """ Redirect to form view to submit task """
    def submit_task_redirect(self):
        tree_view_id = self.env.ref('kw_wfh.kw_wfh_emp_deliverables_tree').id
        form_view_id = self.env.ref('kw_wfh.kw_wfh_emp_deliverables_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Report Tasks',
            'view_mode': 'kanban,form,tree',
            'res_model': 'kw_wfh_deliverables',
            'target': 'self',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('employee_id.id', '=', self.env.user.employee_ids.id), ('wfh_record_id', '=', self.id)],
            'context': {'default_wfh_record_id': self.id},
            'search_view_id': (self.env.ref('kw_wfh.search_view_kw_wfh_emp_deliverables_report').id,)
        }
        return action

    def _enable_mode_id(self, wfh_rec, attn_mode=False):
        if wfh_rec:
            if not attn_mode:
                attn_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])

            """ For extended WFH Request else non-extended Request """
            if wfh_rec.request_to_date and wfh_rec.revised_to_date:
                previous_mode_ids = wfh_rec.parent_ref_id.previous_attendance_mode_ids
            else:
                previous_mode_ids = wfh_rec.employee_id.attendance_mode_ids

            """keeping backup of employee's old attendance mode"""
            if previous_mode_ids:
                wfh_rec.sudo().write({'previous_attendance_mode_ids': [(6, 0, previous_mode_ids.ids)]})

            """if employee has not portal enabled, then it will enable portal 
             else it will change is_wfh status only"""
            wfh_rec.employee_id.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)], 'is_wfh': True})
        return True

    def _remove_mode_id(self, rec, attn_mode=False):
        # print("cal8888888")
        if not attn_mode:
            attn_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
        # if rec and mode.id in rec.employee_id.attendance_mode_ids.ids:
        """
        if employee has more than 1 attendance mode, it will assign only bio-metric mode
        if employee has only 1 attendance mode, it will assign the old one
        if employee had no attendance mode, it will assign bio-metric only
        """
        if rec.previous_attendance_mode_ids.ids:
            #delete all current attn mode
            del_query = f"DELETE FROM hr_employee_kw_attendance_mode_master_rel WHERE hr_employee_id={rec.employee_id.id}"
            self._cr.execute(del_query)
            mode_list = []
            #adding all previous attn mode
            for mode in rec.previous_attendance_mode_ids.ids:
                mode_list.append((rec.employee_id.id,mode))

            mode_ids = str(mode_list)[1:-1]
            add_query = f"INSERT INTO hr_employee_kw_attendance_mode_master_rel (hr_employee_id, kw_attendance_mode_master_id) VALUES {mode_ids} ON CONFLICT DO NOTHING;"
            self._cr.execute(add_query)
            # rec.employee_id.sudo().write({'attendance_mode_ids': [(6, 0, attn_mode.ids)]})  # , 'is_wfh': False
            # query = f"DELETE FROM hr_employee_kw_attendance_mode_master_rel WHERE hr_employee_id={rec.employee_id.id} AND kw_attendance_mode_master_id={attn_mode.id}"
            # self._cr.execute(query)
        # elif len(rec.previous_attendance_mode_ids.ids):
        #     rec.employee_id.sudo().write({'attendance_mode_ids': [(6, 0, rec.previous_attendance_mode_ids.ids)]})  # , 'is_wfh': False
        else:
            #delete all current attn mode
            del_query = f"DELETE FROM hr_employee_kw_attendance_mode_master_rel WHERE hr_employee_id={rec.employee_id.id}"
            self._cr.execute(del_query)
            #adding all previous attn mode
            bio_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'bio_metric')])
            add_query = f"INSERT INTO hr_employee_kw_attendance_mode_master_rel (hr_employee_id, kw_attendance_mode_master_id) VALUES {rec.employee_id.id,bio_mode.id} ON CONFLICT DO NOTHING;"
            self._cr.execute(add_query)
            # if attn_mode.id not in rec.previous_attendance_mode_ids.ids:
            #     query = f"DELETE FROM hr_employee_kw_attendance_mode_master_rel WHERE hr_employee_id={rec.employee_id.id} AND kw_attendance_mode_master_id={attn_mode.id}"
            #     self._cr.execute(query)
            # rec.employee_id.sudo().write({'attendance_mode_ids': [(6, 0, attn_mode.ids)]})  # , 'is_wfh': False
        return True

    def _close_hr_record(self, rec):
        if rec:
            rec.write({
                'hide_expired_record': True,
                'hr_wfh_active_link': False,
                'state': 'expired',
                'act_to_date': rec.request_to_date,
            })

    def _close_record(self,  record):
        if record:
            record.write({
                # 'hide_extension_record': True,
                'wfh_active_link': False,
                'wfh_end_process': True,
                'hide_expired_record': True,
                'state': 'expired',
                # 'form_status': 'expired',
                'act_to_date': date.today(),
            })

    def extend_single_record(self):
        extend_to_date = self.process_id.request_to_date
        if extend_to_date <= self.request_to_date:
            raise ValidationError(f"You cannot extend as To Date {self.request_to_date} of active wfh is greater than or equal to the selected To Date {extend_to_date}")
        else:
            view_id = self.env.ref('kw_wfh.kw_wfh_confirmation_wizard_wizard_form_view').id
            return{
                    'name': 'Confirmation',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_wfh_confirmation_wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(view_id, 'form')],
                    'target': 'new',
                    'view_id': view_id,
                }

    def close_single_record(self):
        self._close_record(self)

    def grant_all(self):
        # print(self.id)
        # print("In Grant All")
        pass

    def extend_all(self):
        # print(self.id)
        # print("In Extend All")
        pass

    def close_all(self):
        # print(self.id)
        # print("In Close All")
        pass

    @api.multi
    def enable_portal_mode(self, emp_id, attn_mode):
        if emp_id and attn_mode:
            if attn_mode.id not in emp_id.attendance_mode_ids.ids:
                query = f"INSERT INTO hr_employee_kw_attendance_mode_master_rel(hr_employee_id, kw_attendance_mode_master_id) VALUES ({emp_id.id},{attn_mode.id}) ON CONFLICT DO NOTHING;"
                self._cr.execute(query)
                # print("Query executed successfully. portal added...")
            else:
                # print("portal is already present...")
                pass

    @api.model
    def update_daily_employee_attendance(self, rec_id=False):
        if rec_id:
            query = f"UPDATE kw_daily_employee_attendance SET work_mode=0 WHERE id = {rec_id}"
            self._cr.execute(query)
        return True
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('wfh_manager_check'):
            if self.env.user.has_group('kw_wfh.group_kw_wfh_manager'):
                args += []
            else:
                # wfh_id = self.env['kw_wfh_action'].search([('ra_id.user_id', '=', self.env.uid), ('status', '=', False)]).wfh_id
                # args += [('id', 'in', wfh_id.ids)]
                # args += [('employee_id.parent_id.user_id', '=', self.env.uid)]
                args += [('action_to_be_taken_by.user_id', '=', self.env.uid)]
        return super(kw_wfh, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
