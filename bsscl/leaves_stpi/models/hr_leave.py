from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare,DEFAULT_SERVER_DATE_FORMAT
import datetime
from datetime import datetime, timedelta, date
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from pytz import timezone, UTC
import math
import re
import base64
from odoo.tools.mimetypes import guess_mimetype
from dateutil.relativedelta import relativedelta

class HRLeave(models.Model):
    _inherit = 'hr.leave'

    branch_id = fields.Many2one('res.branch', 'Branch',readonly=True)
#                                 default=lambda self: self.env['res.users']._get_default_branch())

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for employee in self:
#             print("///////////////////")
            employee.branch_id = employee.employee_id.branch_id.id

class HrLeave(models.Model):
    _inherit = 'hr.leave'
    _description = 'Leaves'
    _order_by = "pending_since desc"

    attachement = fields.Boolean(string="attachment")
    branch_id = fields.Many2one('res.branch', 'Branch')
    file_name = fields.Char()
    attachement_proof = fields.Binary(string="Attachment Proof")
    name = fields.Char('Purpose', compute='_compute_description', inverse='_inverse_description', search='_search_description', compute_sudo=False)
    commuted = fields.Boolean(string="Commuted")
    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_stpi', 'Contractual with STPI')], string='Employment Type',
                                     )
    
    commuted_leave_selection = fields.Selection([('Yes', 'Yes'),
                                      ('No', 'No'),
                                      ], default='No',
                                     )
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female'),
                               ('transgender', 'Both')
                               ])
    employee_state = fields.Selection([('test_period', 'Probation'),('contract', 'Contract'),('deputation', 'Deputation'),('employment', 'Regular')], string="Stage")
    leave_type_id = fields.Many2one('hr.leave.type', readonly=True)
    from_date = fields.Date(string="From Date", readonly=True)
    to_date = fields.Date(string="To Date", readonly=True)
    no_of_days_leave = fields.Float(string="No of Days Leave", readonly=True)
    is_rh = fields.Boolean(string='Is RH?')
    half_pay_allowed = fields.Boolean(string="Half Pay Allowed")
    status = fields.Selection([('draft', 'To Submit'),
                               ('cancel', 'Cancelled'),
                               ('confirm', 'To Approve'),
                               ('refuse', 'Reject'),
                               ('validate1', 'Second Approval'),
                               ('validate', 'Approved')
                               ], string="Status", readonly=True)
    applied_on = fields.Datetime(string="Applied On", readonly=True, )
    days_between_last_leave = fields.Float(string="Days Between Last Leave", readonly=True)
    are_days_weekend = fields.Boolean(string="Are Days Weekend", readonly=True)
    allow_request_unit_half = fields.Boolean(string='Allow First Half Day')
    allow_request_unit_half_2 = fields.Boolean(string='Allow Half Day')
    request_unit_half_2 = fields.Boolean(string="Second Half")
    request_unit_half_1 = fields.Boolean(string="First Half")

    request_date_from_period_2 = fields.Selection([
        ('am', 'Morning'),
        ('pm', 'Afternoon')], default='am')

    countpre = fields.Float(string='CountPre')
    countpost = fields.Float(string='CountPost')
    ltc = fields.Boolean(string='For LTC?')
    ltc_apply_done = fields.Boolean(string='LTC Taken')
    no_of_days_display_half = fields.Float(string="Duartion Half",compute="_compute_no_of_days_display_half",store=True) ## Nikunja - Aug 23 2021
    no_of_days_display_half_new = fields.Float(compute="_compute_no_of_days_display_half1",store=True) ## Nikunja - Aug 23 2021
    holiday_half_pay = fields.Boolean(string="Half Pay Holiday")
    pre_post_leaves_ids = fields.One2many('hr.leave.pre.post', 'pre_post_leave', string='Leaves', readonly=True)
    commuted_leave = fields.Text(string="Leave Type")
    manager_designation_id = fields.Many2one('hr.job', string="Pending With")
    pending_since = fields.Date(readonly=True)
    duration_display = fields.Char('Requested(Days)', compute='_compute_duration_display',
                                   help="Field allowing to see the leave request duration in days or hours depending on the leave_type_request_unit")  # details

    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By All Department'),
        ('branch', 'By Branch'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag')],
        string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)]},
        help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category')
    by_branch_id = fields.Many2one("res.branch", string="By Branch")

    address_during_leave = fields.Char(string="Address During Leave Period", required=True)
    fall_back = fields.Char(string="Fall Back")

    public_holiday = fields.Many2many('resource.calendar.leaves',string='RH Holidays',compute='_compute_public_holidays')
    # leave_type = fields.Selection(related='holiday_status_id.leave_type')
    leave_type = fields.Many2one('leave.type.master', related='holiday_status_id.leave_type')
    hide_ltc = fields.Boolean(string='Hide LTC', compute='_compute_ltc_display')
    cancel_req = fields.Boolean(string='Cancellation Request')
    remarks_req = fields.Boolean(string='Remarks Request')
    edit_req = fields.Boolean(string='Edit Request')
    cancel_reason = fields.Char(string="Reason Of Cancellation")
    refuse_reason = fields.Char(string="Refuse Reason")
    refuse_cancel_reason = fields.Char(sting="Reason for refusing cancellation request")
    group_id = fields.Many2one("stpi.group.master","Group", compute='_compute_grp_master',store=True)
    max_leaves = fields.Float(string='Entitle', compute='_compute_waiting_for_approval_leaves')
    leaves_taken = fields.Float(string='Granted', compute='_compute_waiting_for_approval_leaves',
                                help='This value is given by the sum of all leaves requests with a negative value.')
    remaining_leaves = fields.Float(string='Balance', compute='_compute_waiting_for_approval_leaves',
                                    help='Maximum Leaves Allowed - Leaves Already Taken')
    virtual_remaining_leaves = fields.Float(string='Virtual Remaining Leaves',
                                            compute='_compute_waiting_for_approval_leaves',
                                            help='Maximum Leaves Allowed - Leaves Already Taken - Leaves Waiting Approval')

    waiting_for_approval_leaves = fields.Float(string='Waiting Approval',
                                               compute='_compute_waiting_for_approval_leaves')
    virtual_leaves_taken = fields.Float(
        compute='_compute_waiting_for_approval_leaves', string='Virtual Time Off Already Taken',
        help='Sum of validated and non validated time off requests.')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', compute=False, readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")
    pending_with = fields.Char("Pending At",compute="_compute_pending_with")
    
    # start : merged from hr_employee_stpi
    is_commuted = fields.Boolean('Is Commuted')
    medical_certificate = fields.Binary("Medical Certificate")
    is_half_pay = fields.Boolean('Is Half-pay')
    half_invisible = fields.Boolean("Half Invisible",compute="_compute_half_pay" )
    check_self = fields.Boolean('check_self',compute='_compute_self_name')
    employee_invsible = fields.Boolean("Half Invisible",compute="_compute_emp_invisible" )

    @api.depends('employee_id')
    def _compute_emp_invisible(self):
        for rec in self:
            is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
            print("ismanager", is_manager)
            if is_manager:
                rec.employee_invsible = True
            else:
                rec.employee_invsible = False


    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return
        # current_employee = self.env.user.employee_id
        # if not current_employee:
        #     return
        # is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        # is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        # for holiday in self:
        #     val_type = holiday.holiday_status_id.sudo().allocation_validation_type
        #     if state == 'confirm':
        #         continue
        #
        #     if state == 'draft':
        #         if holiday.employee_id != current_employee and not is_manager:
        #             raise UserError(_('Only a time off Manager can reset other people allocation.'))
        #         continue
        #
        #     if not is_officer and self.env.user != holiday.employee_id.leave_manager_id:
        #         raise UserError(_('Only a time off Officer/Responsible or Manager can approve or refuse time off requests.'))
        #
        #     if is_officer or self.env.user == holiday.employee_id.leave_manager_id:
        #         # use ir.rule based first access check: department, members, ... (see security.xml)
        #         holiday.check_access_rule('write')
        #
        #     if holiday.employee_id == current_employee and not is_manager:
        #         raise UserError(_('Only a time off Manager can approve its own requests.'))
        #
        #     if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
        #         if self.env.user == holiday.employee_id.leave_manager_id and self.env.user != holiday.employee_id.user_id:
        #             continue
        #         manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
        #         if (manager != current_employee) and not is_manager:
        #             raise UserError(_('You must be either %s\'s manager or time off manager to approve this time off') % (holiday.employee_id.name))
        #
        #     if state == 'validate' and val_type == 'both':
        #         if not is_officer:
        #             raise UserError(_('Only a Time off Approver can apply the second approval on allocation requests.'))


    @api.depends('number_of_days')
    def _compute_half_pay(self):
        for rec in self:
            if rec.number_of_days > 1:
                rec.half_invisible = True
            else:
                rec.half_invisible = False

    # (wagisha) check RA of an employee
    @api.depends('employee_id')
    def _compute_self_name(self):
        for rec in self:
            if rec.employee_id.parent_id.user_id.id == self.env.user.id:
                rec.check_self= True
            else :
                rec.check_self= False

    #(wagisha) for Address validation               
    @api.constrains('address_during_leave')
    @api.onchange('address_during_leave')          
    def _check_address_during_leave_validation(self):
        for rec in self:
            if rec.address_during_leave:
                if not (re.match('^[ a-zA-Z0-9,-]+$', rec.address_during_leave)):
                    raise ValidationError("Address should be in alphanumeric. For special symbol , and - can only be used. ")
                if len(rec.address_during_leave)>500:
                    raise ValidationError("Address should not be greater than 500")
                
    #(wagisha) for Address validation               
    @api.constrains('name')
    @api.onchange('name')          
    def _check_purpose_validation(self):
        for rec in self:
            if rec.name and not (re.match('^[A-Za-z][ a-zA-Z]+$', rec.name)):
                    raise ValidationError(_('Purpose should start with alphabets and it should be in alphabets only. '))
            if rec.name and len(rec.name)>500:
                raise ValidationError("Purpose should not be greater than 500")
                
    #(wagisha) for attachment file validation       
    @api.constrains('attachement_proof')
    def _check_document_upload(self):
        for rec in self:
            allowed_file = ['application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/msword']
            if rec.attachement_proof:
                app_size = ((len(rec.attachement_proof) * 3/4) / 1024) / 1024
                if app_size > 2:
                    raise ValidationError("Document allowed is size less than 2MB")
                mimetype = guess_mimetype(base64.b64decode(rec.attachement_proof))
                if str(mimetype) not in allowed_file:
                    raise ValidationError("Only PDF/docx format is allowed")
    
    #(wagisha) maternity leave should not be taken more than 2 timesself.state
    @api.constrains('holiday_status_id','number_of_days')
    def _check_maternity_validation(self):
        # maternity_count = self.env['hr.leave'].search_count([('holiday_status_id.leave_type', '=', 'Maternity Leave'),('state', 'in', ['confirm', 'validate'])])
        if self.max_leaves < self.number_of_days_display:
            raise ValidationError(_('Leave duration should be less than entitled leave.'))
        if self.virtual_remaining_leaves<0:
            raise ValidationError(_('Your requested leave should not be more than entitle leave.'))
        # if maternity_count >2:
        #     raise ValidationError("You cannot take Maternity leave more than 2")
        if self.holiday_status_id.leave_type == 'Half Pay Leave' and self.no_of_days_display_half_new > self.virtual_remaining_leaves:
            raise ValidationError(_('Your requested leave should not be more than entitle leave.'))


    def activity_update(self):
        to_clean, to_do = self.env['hr.leave'], self.env['hr.leave']
        for holiday in self:
            start = UTC.localize(holiday.date_from).astimezone(timezone(holiday.employee_id.tz or 'UTC'))
            end = UTC.localize(holiday.date_to).astimezone(timezone(holiday.employee_id.tz or 'UTC'))
            note = _('New %s Request created by %s from %s to %s') % (holiday.holiday_status_id.leave_type.code, holiday.create_uid.name, start, end)
            if holiday.state == 'draft':
                to_clean |= holiday
            elif holiday.state == 'confirm':
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_approval',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif holiday.state == 'validate1':
                holiday.activity_feedback(['hr_holidays.mail_act_leave_approval'])
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_second_approval',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif holiday.state == 'validate':
                to_do |= holiday
            elif holiday.state == 'refuse':
                to_clean |= holiday
        if to_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
        if to_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])

    @api.onchange('holiday_status_id')
    def onchange_is_holiday_status_id(self):
        for rec in self:
            rec.is_half_pay = rec.holiday_status_id.is_half_pay
            rec.hr_consider_sandwich_rule = rec.holiday_status_id.hr_consider_sandwich_rule
            if rec.holiday_status_id and rec.holiday_status_id.is_maternity == True:
                if rec.employee_id.gender == 'female':
                    if rec.number_of_days > 180.00:
                        raise ValidationError(_('You are not able to take more than 180 days Maternity leave'))
                else:
                    raise ValidationError(_('You are not able to take Maternity leave'))

    
    def name_get(self):
        res = []
        for leave in self:
            if self.env.context.get('short_name'):
                if leave.leave_type_request_unit == 'hour':
                    res.append((leave.id, _("%s : %.2f hour(s)") % (leave.name or leave.holiday_status_id.name, leave.number_of_hours_display)))
                else:
                    res.append((leave.id, _("%s : %.2f day(s)") % (leave.name or leave.holiday_status_id.name, leave.number_of_days)))
            else:
                if leave.holiday_type == 'company':
                    target = leave.mode_company_id.name
                elif leave.holiday_type == 'department':
                    target = leave.department_id.name
                elif leave.holiday_type == 'category':
                    target = leave.category_id.name
                else:
                    target = leave.employee_id.sudo().name
                if leave.leave_type_request_unit == 'hour':
                    res.append(
                        (leave.id,
                        _("%s on %s : %.2f hour(s)") %
                        (target, leave.holiday_status_id.name.code, leave.number_of_hours_display))
                    )
                else:
                    res.append(
                        (leave.id,
                        _("%s on %s : %.2f day(s)") %
                        (target, leave.holiday_status_id.name.code, leave.number_of_days))
                    )
        return res

    # @api.onchange('is_commuted')
    # def onchange_is_commuted(self):
    #     for rec in self:
    #         if rec.is_commuted == True:
    #             if rec.holiday_status_id:
    #                 pass


    @api.onchange('number_of_days', 'is_commuted', 'holiday_status_id')
    def onchange_number_od(self):
        for rec in self:
            print('holiday_status_idholiday_status_id', rec.holiday_status_id,rec.is_half_pay,rec.is_commuted)
            if rec.holiday_status_id and rec.is_half_pay == True and rec.is_commuted == True:
                if rec.no_of_days_display_half_new:
                    rec.number_of_days = 2*rec.no_of_days_display_half_new
                    print("rec.number_of_daysrec.number_of_days",rec.number_of_days)
            self.compute_number_of_leave()
            # else:
            #     if rec.holiday_status_id and rec.is_half_pay == True and rec.is_commuted == False:
            #             5/0
            #             rec.number_of_days = rec.no_of_days_display_half_new
        print("rec.number_of_daysrec.number_of_days1", rec.number_of_days)
    # end : merged from hr_employee_stpi

    
    def _compute_pending_with(self):
        for leave in self:
            if leave.state == 'confirm':
                if leave.main_exception_id:
                    leave.pending_with = leave.main_exception_id.name
                else:
                    leave.pending_with = leave.employee_id.parent_id and leave.employee_id.parent_id.name
            else:
                leave.pending_with = False

    
    @api.depends('employee_id')
    def _compute_grp_master(self):
        for rec in self:
            contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),('state','=', 'open')], limit=1)
            if contract_id:
                print("------------------------", contract_id,contract_id.pay_level_id.group_id)
                if contract_id.pay_level_id.group_id:
                    rec.group_id = contract_id.pay_level_id.group_id.id
                    print('-----------group', rec.group_id)

    @api.depends('holiday_status_id', 'employee_id')
    def _compute_waiting_for_approval_leaves(self):
        for holiday in self:
            if holiday.holiday_status_id and holiday.employee_id:

                # print(holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).max_leaves, holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).leaves_taken, holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).remaining_leaves)

                # if holiday.holiday_status_id:
                holiday.max_leaves = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).max_leaves
                holiday.leaves_taken = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).leaves_taken
                holiday.remaining_leaves = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).remaining_leaves
                holiday.virtual_remaining_leaves = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).virtual_remaining_leaves
                holiday.virtual_leaves_taken = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).virtual_leaves_taken

                holiday.waiting_for_approval_leaves = holiday.remaining_leaves - holiday.virtual_remaining_leaves
            else:
                holiday.max_leaves = 0
                holiday.leaves_taken = 0
                holiday.remaining_leaves = 0
                holiday.virtual_remaining_leaves = 0
                holiday.waiting_for_approval_leaves = 0
           
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if self._context.get('branch_check'):
            args += [('branch_id','in',self.env.user.branch_ids.ids)]
        
        return super(HrLeave, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        if self._context.get('branch_check'):
            domain += [('branch_id','in',self.env.user.branch_ids.ids)]

        return super(HrLeave, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

    @api.constrains('employee_id')
    def joining_date_leave_apply_validation(self):
        for record in self:
            if record.date_from.date() < record.employee_id.transfer_date:
                raise ValidationError("You should not apply leave before your date of joining.")

    
    @api.depends('holiday_status_id')
    def _compute_public_holidays(self):
        for record in self:
            # if record.employee_id and record.holiday_status_id and record.holiday_status_id == record.employee_id.resource_calendar_id.rh_leave_type:
                # record.public_holiday = record.employee_id.resource_calendar_id.global_leave_ids.filtered(lambda res:res.holiday_type == 'rh').ids
            if record.employee_id and record.holiday_status_id.leave_type.code== 'Restricted Holiday': 
                if record.employee_id.resource_calendar_id:
                    record.public_holiday = record.employee_id.resource_calendar_id.global_leave_ids.filtered(lambda res:res.holiday_type == 'rh').ids
                else:

                    raise ValidationError("Please enter the working shifts in the employee profile or ask administration for the same.")
            else:
                record.public_holiday = False
    ## Nikunja - Aug 23 2021

    
    
    @api.depends('number_of_days')
    def _compute_no_of_days_display_half(self):
        for record in self:
            record.no_of_days_display_half = record.number_of_days

    
    @api.depends('number_of_days')
    def _compute_no_of_days_display_half1(self):
        for record in self:
            if record.request_date_to and record.request_date_from:
                # duration_user = (record.request_date_to - record.request_date_from).days
                # record.no_of_days_display_half_new = float(duration_user) + float(1)
                record.no_of_days_display_half_new = record.number_of_days
            else:
                record.no_of_days_display_half_new = 0


    
    
    @api.depends('holiday_status_id')
    def _compute_ltc_display(self):
        for rec in self:
            print("------------------------", rec.holiday_status_id.is_ltc)
            if rec.holiday_status_id.is_ltc == True:
                rec.hide_ltc = True
                print('-----------ltc', rec.hide_ltc)
            else:
                rec.hide_ltc = False
    
    ## Nikunja - Aug 23 2021
    
    @api.constrains('request_date_from','request_date_to')
    def _validate_rh_holidays(self):
        for record in self:
            if record.public_holiday:
                dates = record.public_holiday.mapped('date')
                dates = [pdate.strftime(DEFAULT_SERVER_DATE_FORMAT) for pdate in dates]
                if record.request_date_from.strftime(DEFAULT_SERVER_DATE_FORMAT) not in dates or record.request_date_to.strftime(DEFAULT_SERVER_DATE_FORMAT) not in dates or record.number_of_days_display > 1:
                    raise ValidationError("Applied Leave period is not part of RH Holiday Calender.")
            if record.employee_id and record.holiday_status_id.leave_type.code!= 'Maternity Leave':    
                if record.request_date_to:
                    year = record.request_date_to.year
                    if date.today().year != year:
                        raise ValidationError(_("You are not allowed to create leave of another year."))
                if record.number_of_days_display<=0:
                        raise ValidationError(_("You are not allowed to create leave of 0 days."))

    @api.constrains('request_unit_half_2','request_unit_half')
    @api.onchange('request_unit_half_2', 'request_unit_half')
    def onchange_request_date_from_period_2(self):
        for leave in self:
            if leave.request_unit_half == True:
                leave.request_date_from_period = 'am'
                leave.request_date_from_period_2 = 'am'
            elif leave.request_unit_half_2 == True:
                leave.request_date_from_period = 'pm'
                leave.request_date_from_period_2 = 'pm'
            else:
                leave.request_date_from_period = 'am'
                leave.request_date_from_period_2 = 'pm'

    @api.constrains('holiday_status_id','ltc')
    def validate_chldcare_leave(self):
        for leave in self:
            if leave.holiday_status_id and leave.holiday_status_id.leave_type.code.lower() == 'child care leave'\
            and leave.ltc:
                raise ValidationError("LTC is not Applicable with Childcare leave.")


    @api.model
    def create(self, vals):
        res = super(HrLeave, self).create(vals)
        print(res.state,res.holiday_status_id.leave_validation_type, 'before change 111')
        res.state = 'draft'
        created_date = datetime.now().date()
        res.manager_designation_id = res.employee_id.parent_id.job_id
        res.pending_since = created_date.strftime('%Y-%m-%d')
        res.is_half_pay = res.holiday_status_id.is_half_pay
        print("res.is_half_pay", res.is_half_pay)
        if res.holiday_status_id.leave_validation_type == 'no_validation':
            print(res.state, 'before change ')
            res.state = 'draft'
            print(res.state, 'after cange')
        if res.holiday_status_id and res.employee_id:
            lst1 = []
            lst2 = []
            type = dict(res.fields_get(["employee_type"], ['selection'])['employee_type']["selection"]).get(
                res.employee_type)
            state = dict(res.fields_get(["employee_state"], ['selection'])['employee_state']["selection"]).get(
                res.employee_state)
            for leave_type_emp in res.holiday_status_id.allow_service_leave:
                lst1.append(leave_type_emp.name)
            for leave_type_state in res.holiday_status_id.allow_emp_stage:
                lst2.append(leave_type_state.name)
            print("state is",state)
            print("Inside Leave")
            print("datas are",res.holiday_status_id.gende,lst1,lst2)
            if not (res.holiday_status_id.gende == 'transgender' or res.gender == res.holiday_status_id.gende):
                raise ValidationError(
                    _("Your are not allow to take this leave as this leave type is applicable only for %s") % (
                        res.holiday_status_id.gende))
            if type not in lst1:
                raise ValidationError(
                    _("Your are not allow to take this leave as this leave type is applicable only for %s") % (lst1))
            if state not in lst2:
                raise ValidationError(
                    _("Your are not allow to take this leave as this leave type is applicable only for %s") % (lst2))

            # if res.holiday_status_id.leave_type == 'Maternity Leave':
            #     leave_ids = self.env['hr.leave'].search([('employee_id', '=', res.employee_id.id),
            #                                             ('holiday_status_id.leave_type', '=', 'Maternity Leave'),
            #                                             ('state', 'not in', ['cancel', 'refuse']),
            #                                             ('id', '!=', res.id)])
            #     print('-=====', leave_ids)
            #     if len(leave_ids)>1:
            #         raise ValidationError(_(
            #                     'You are not allowed to apply for this leave because of 2 leave rule applicability.'))
            # if res.holiday_status_id.leave_type == 'Paternity Leave':
            #     leave_ids = self.env['hr.leave'].search([('employee_id', '=', res.employee_id.id),
            #                                             ('holiday_status_id.leave_type', '=', 'Paternity Leave'),
            #                                             ('state', 'not in', ['cancel', 'refuse']),
            #                                             ('id', '!=', res.id)])
            #     print('-=====', leave_ids,len(leave_ids))
            #     if len(leave_ids)>1:
            #         raise ValidationError(_(
            #                     'You are not allowed to apply for this leave because of 2 leave rule applicability.'))
            # print('==========================Employee shift===================================', res.employee_id.resource_calendar_id)
            res.countpre = 0.00
            res.countpost = 0.00
            if res.pre_post_leaves_ids and res.holiday_status_id.sandwich_rule == True:
                for preh in res.pre_post_leaves_ids:
                    if preh.pre_post == 'pre' and preh.leave == 'holiday':
                        res.countpre += 1
                print('======================Pre Holiday Count===========================',res.holiday_status_id.name, res.countpre)
                for posth in res.pre_post_leaves_ids:
                    if posth.pre_post == 'post' and posth.leave == 'holiday':
                        res.countpost += 1
                for ldate in res.pre_post_leaves_ids:
                    if ldate.pre_post == 'pre' and ldate.leave == 'leave':
                        countpredays = (res.request_date_from - ldate.to_date).days
                        # print('======================Pre Leave Count===========================', (countpredays - 1))
                        if int(countpredays - 1) == int(res.countpre):
                            for hpre in res.pre_post_leaves_ids:
                                if hpre.pre_post == 'pre' and hpre.holiday != False:
                                    raise ValidationError(_(
                                        'You are not allowed to apply for this leave because of Sandwich rule applicability. Please cancel this leave and correct the existing Leave to cover the holidays/weekends'))
                    if ldate.pre_post == 'post' and ldate.leave == 'leave':
                        countpostdays = (ldate.from_date - res.request_date_to).days
                        # print('======================Post Leave Count===========================', (countpostdays - 1))
                        if int(countpostdays - 1) == int(res.countpost):
                            for hpre in res.pre_post_leaves_ids:
                                if hpre.pre_post == 'post' and hpre.holiday != False:
                                    raise ValidationError(_(
                                        'You are not allowed to apply for this leave because of Sandwich rule applicability. Please cancel this leave and correct the existing Leave to cover the holidays/weekends'))
            count = 0
            prefix = []
            for allow_comb in res.holiday_status_id.allowed_prefix_leave:
                prefix.append(allow_comb.name)
                count += 1
                print('---------------------======', prefix,count)
            # print("===========================Number of Allowed Prefix Leave==============================", count)
            if count > 0:
                for pr_po in res.pre_post_leaves_ids:
                    print("pr_popr_popr_popr_popr_popr_po", pr_po)
                    if pr_po.pre_post == 'pre' and pr_po.leave == 'leave':
                        # print("==========================List of Allowed Prefix Leave==================================",prefix)
                        # print("==========================Current Pre leave type==================================",pr_po.leave_type_id.name)
                        countpre_club_days = (res.request_date_from - pr_po.to_date).days
                        print('-------------=====',res.request_date_from,pr_po.to_date,countpre_club_days)
                        if countpre_club_days == 1:
                            if pr_po.leave_type_id.name.code not in prefix:
                                raise ValidationError(_('Leave Type is not allowed to be clubbed with  %s ') % (
                                    pr_po.leave_type_id.name.code))
                    if pr_po.pre_post == 'post' and pr_po.leave == 'leave':
                        # print("==========================List of Allowed Prefix Leave==================================",prefix)
                        # print("==========================Current Post leave type==================================",pr_po.leave_type_id.name)
                        countpost_club_days = (pr_po.from_date - res.request_date_to).days
                        if countpost_club_days == 1:
                            if pr_po.leave_type_id.name.code not in prefix:
                                raise ValidationError(_('Leave Type is not allowed to be clubbed with  %s ') % (
                                    pr_po.leave_type_id.name.code))
                    print("-======================",pr_po.pre_post,pr_po.leave)
                    if pr_po.pre_post == 'pre' and pr_po.leave == 'holiday':
                        if pr_po.holiday != False and pr_po.holiday != 'Saturday' and pr_po.holiday != 'Sunday':
                            countpre_club_days = (res.request_date_from -  timedelta(days=2))
                            leave_ids = self.env['hr.leave'].search([('employee_id', '=', res.employee_id.id),
                                                                     ('request_date_from', '>=', countpre_club_days),
                                                                     ('request_date_to', '<=', countpre_club_days),
                                                                     ('state', 'not in', ['cancel', 'refuse'])],)
                            print('-------------=====',res.request_date_from,pr_po.to_date,countpre_club_days,leave_ids,leave_ids.holiday_status_id.name)
                            if leave_ids:
                                if leave_ids.holiday_status_id.name not in prefix:
                                    raise ValidationError(_('Leave Type is not allowed to be clubbed with  %s ') % (
                                        leave_ids.holiday_status_id.name))
                    if pr_po.pre_post == 'post' and pr_po.leave == 'holiday':
                        if pr_po.holiday != False and pr_po.holiday != 'Saturday' and pr_po.holiday != 'Sunday':
                            countpre_club_days = (res.request_date_to +  timedelta(days=2))
                            leave_ids = self.env['hr.leave'].search([('employee_id', '=', res.employee_id.id),
                                                                     ('request_date_from', '>=', countpre_club_days),
                                                                     ('request_date_to', '<=', countpre_club_days),
                                                                     ('state', 'not in', ['cancel', 'refuse'])],)
                            print('-------------=====',res.request_date_to,pr_po.to_date,countpre_club_days,leave_ids,leave_ids.holiday_status_id.name)
                            if leave_ids:
                                if leave_ids.holiday_status_id.name not in prefix:
                                    raise ValidationError(_('Leave Type is not allowed to be clubbed with  %s ') % (
                                        leave_ids.holiday_status_id.name))
            # 5/0

            # count = 0
            # leave_ids = self.env['hr.leave'].search([('employee_id', '=', res.employee_id.id),
            #                                          ('request_date_from', '>=', (date.today().year, 1, 1)),
            #                                          ('request_date_to', '<=', (date.today().year, 12, 31)),
            #                                          ('holiday_status_id.leave_type', '=', 'Restricted Leave'),
            #                                          ('state', 'not in', ['cancel', 'refuse'])],
            #                                         order="request_date_to desc")
            # for leaves in leave_ids:
            #     count += 1
            # if count > res.employee_id.resource_calendar_id.max_allowed_rh and res.holiday_status_id.leave_type == 'Restricted Leave':
            #     raise ValidationError(_(
            #         'You are not allowed to take leave'))
            # count1 = 0
            # leave_ids1 = self.env['hr.leave'].search([('employee_id', '=', res.employee_id.id),
            #                                          ('request_date_from', '>=', (date.today().year, 1, 1)),
            #                                          ('request_date_to', '<=', (date.today().year, 12, 31)),
            #                                          ('holiday_status_id.leave_type', '=', 'Gestured Leave'),
            #                                          ('state', 'not in', ['cancel', 'refuse'])],
            #                                         order="request_date_to desc")
            # for leaves in leave_ids1:
            #     count1 += 1
            # if count1 > res.employee_id.resource_calendar_id.max_allowed_rh and res.holiday_status_id.leave_type == 'Gestured Leave':
            #     raise ValidationError(_(
            #         'You are not allowed to take leave'))
            # rh_dates=[]
            # if res.holiday_status_id.leave_type == 'Restricted Leave':
            #     for allow_comb in res.employee_id.resource_calendar_id.global_leave_ids:
            #         if allow_comb.restricted_holiday == True:
            #             rh_dates.append(allow_comb.date)
            #     if not(res.request_date_from in rh_dates and res.request_date_to in rh_dates):
            #         raise ValidationError(_(
            #             'You are not allowed to take leave'))
            # gh_dates=[]
            # if res.holiday_status_id.leave_type == 'Gestured Leave':
            #     for allow_comb in res.employee_id.resource_calendar_id.global_leave_ids:
            #         if allow_comb.gestured_holiday == True:
            #             gh_dates.append(allow_comb.date)
            #     if not(res.request_date_from in gh_dates and res.request_date_to in gh_dates):
            #         raise ValidationError(_(
            #             'You are not allowed to take leave'))

            if res.employee_id.resource_calendar_id.rh_leave_type == res.holiday_status_id:
                for line in res.employee_id.resource_calendar_id.global_leave_ids:
                    if res.request_date_from == line.date and res.request_date_to == line.date and line.holiday_type == 'rh':
                        res.is_rh = True
            if res.holiday_status_id and res.is_half_pay == True:
                res.onchange_number_od()

            # if res.is_rh == True:
            #     count = 0
            #     leave_ids = self.env['hr.leave'].search([('employee_id', '=', res.employee_id.id),
            #                                              ('request_date_from', '>=', (date.today().year, 1, 1)),
            #                                              ('request_date_to', '<=', (date.today().year, 12, 31)),
            #                                              ('is_rh', '=', True),
            #                                              ('state', 'not in', ['cancel', 'refuse'])],
            #                                             order="request_date_to desc")
            #     for leaves in leave_ids:
            #         count += 1
            # if count > res.employee_id.resource_calendar_id.max_allowed_rh:
            #     raise ValidationError(_(
            #         'You are not allowed to take leave as maximum allowed RH should be {name}'.format(name=res.employee_id.resource_calendar_id.max_allowed_rh)))
        ## Nikunja - Aug 23 2021
        # if res.holiday_status_id.leave_type == 'Half Pay Leave':
        #     res.number_of_days_display = res.no_of_days_display_half
        # if res.holiday_status_id:
        #     if res.holiday_status_id.sandwich_rule == True:
        #         print('====================================================TTTTTTTTTTT')
        #         res.number_of_days = (res.request_date_to - res.request_date_from).days + 1
        #         res.number_of_days_display = (res.request_date_to - res.request_date_from).days + 1
        # if self.commuted_leave_selection == 'Yes':
        #     self.commuted_leave = 'Commuted Leaves'
        #     self.no_of_days_display_half = self.number_of_days_display * 2
        #     self.duration_display = self.number_of_days_display * 2
        #     self.number_of_days_display = self.no_of_days_display_half
        # else:
        #     self.no_of_days_display_half = self.number_of_days_display
        ## Nikunja - Aug 23 2021
        return res


    @api.constrains('request_date_from', 'request_date_to', 'employee_id')
    @api.onchange('request_date_from', 'request_date_to', 'employee_id')
    def create_pre_post_lines(self, working_list=None):
        for rec in self:
            rec.countpre = 0.00
            rec.countpost = 0.00
            pre_ids = []
            pre_holiday_ids = []
            leave_ids = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
                                                     ('request_date_to', '!=', rec.request_date_to),
                                                     ('request_date_to', '<=', rec.request_date_from),
                                                     ('state', 'not in', ['cancel', 'refuse'])], limit=1,
                                                    order="request_date_to desc")
            # print("==============Leave Ids pre onchange=======================", leave_ids)
            if leave_ids:

                for leave in leave_ids:
                    # print('======================Check Date pre========================================', leave.request_date_to)
                    # print('======================Check Date current from========================================', rec.request_date_from)
                    if leave.request_date_to < rec.request_date_from:
                        #                         if not rec.pre_post_leaves_ids:
                        pre_ids.append((0, 0, {
                            'pre_post_leave': rec.id,
                            'pre_post': 'pre',
                            'leave': 'leave',
                            'leave_type_id': leave.holiday_status_id.id,
                            'from_date': leave.request_date_from,
                            'to_date': leave.request_date_to,
                            'no_of_days_leave': leave.number_of_days_display,
                            'status': leave.state,
                        }))
                    else:
                        rec.pre_post_leaves_ids = working_list
                    for gli in rec.employee_id.resource_calendar_id.global_leave_ids:
                        if gli.date and leave.request_date_to < gli.date < rec.request_date_from:
                            # print('rec=======================', rec.request_date_from, gli.date)
                            #                             if not rec.pre_post_leaves_ids:
                            pre_holiday_ids.append((0, 0, {'pre_post_leave': rec.id,
                                                           'pre_post': 'pre',
                                                           'leave': 'holiday',
                                                           'leave_type_id': False,
                                                           'holiday': gli.name,
                                                           'from_date': gli.date,
                                                           'to_date': gli.date,
                                                           'no_of_days_leave': 1,
                                                           'status': 'validate',
                                                           }))
                        else:
                            rec.pre_post_leaves_ids = working_list
                rec.pre_post_leaves_ids = pre_ids
                rec.pre_post_leaves_ids = pre_holiday_ids
            else:
                rec.pre_post_leaves_ids = working_list

            post_leave_ids = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
                                                          ('request_date_to', '!=', rec.request_date_to),
                                                          ('request_date_from', '>=', rec.request_date_to),
                                                          ('state', 'not in', ['cancel', 'refuse'])], limit=1,
                                                         order="request_date_from asc")
            # print("==============Leave Ids post onchange=======================", post_leave_ids)

            if post_leave_ids:
                post_ids = []
                post_holiday_ids = []
                for leave in post_leave_ids:
                    #                     print("1111111111111111111111111")
                    if leave.request_date_from > rec.request_date_to:
                        #                         print("22222222222222222222222222")
                        #                         if not rec.pre_post_leaves_ids:
                        post_ids.append((0, 0, {'pre_post_leave': rec.id,
                                                'pre_post': 'post',
                                                'leave': 'leave',
                                                'leave_type_id': leave.holiday_status_id.id,
                                                'from_date': leave.request_date_from,
                                                'to_date': leave.request_date_to,
                                                'no_of_days_leave': leave.number_of_days_display,
                                                'status': leave.state,
                                                }))
                    #                     print("OOOOOOOOOOOrequest_date_fromOOOOOOOOOOOOOOO",post_ids)
                    #                     else:
                    #                         rec.pre_post_leaves_ids = working_list

                    for gli in rec.employee_id.resource_calendar_id.global_leave_ids:
                        if gli.date and leave.request_date_from > gli.date > rec.request_date_to:
                            #                             if not rec.pre_post_leaves_ids:
                            #                             print("gggggggggggggggggggg",gli)
                            post_holiday_ids.append((0, 0, {'pre_post_leave': rec.id,
                                                            'pre_post': 'post',
                                                            'leave': 'holiday',
                                                            'leave_type_id': False,
                                                            'holiday': gli.name,
                                                            'from_date': gli.date,
                                                            'to_date': gli.date,
                                                            'no_of_days_leave': 1,
                                                            'status': 'validate',
                                                            }))
                            # print("PPPPPPPPPPPPPPrequest_date_fromholidayPPPPPPPPPPPPP",post_holiday_ids)
                #                         else:
                #                             rec.pre_post_leaves_ids = working_list
                if post_ids or post_holiday_ids:
                    rec.pre_post_leaves_ids = post_ids
                    rec.pre_post_leaves_ids = post_holiday_ids
                    # print("resulttttttttttt",rec.pre_post_leaves_ids)
            else:
                rec.pre_post_leaves_ids = working_list
                # print("elsssssssssssssssssssssssssss",rec.pre_post_leaves_ids)

            if leave_ids and not post_leave_ids:
                rec.pre_post_leaves_ids = pre_ids
                rec.pre_post_leaves_ids = pre_holiday_ids

    @api.constrains('date_from', 'date_to', 'employee_id')
    @api.onchange('date_from', 'date_to', 'employee_id')
    def onchange_employee(self):
        for leave in self:
            leave.branch_id = leave.employee_id.branch_id.id
            leave.employee_type = leave.employee_id.employee_type
            leave.employee_state = leave.employee_id.state
            leave.gender = leave.employee_id.gende
            leave.manager_designation_id = leave.employee_id.parent_id.job_id
            leave.onchange_number_od()

    #             if leave.create_date:
    #                 created_date = leave.create_date
    #                 leave.pending_since = created_date.strftime('%Y-%m-%d')
    # #             print("{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{",leave.employee_state,leave.employee_type,leave.branch_id)
    #             leave_ids = self.env['hr.leave'].search([('employee_id','=',leave.employee_id.id),
    #                                                      ('state','=','validate')],limit=1, order="request_date_to desc")
    # #             print("<<<<<<<<<<<<<<<<<<<<",leave_ids)
    #             if leave_ids:
    #                 leave.leave_type_id = leave_ids.holiday_status_id.id
    #                 leave.from_date = leave_ids.request_date_from
    #                 leave.to_date = leave_ids.request_date_to
    #                 leave.no_of_days_leave = leave_ids.number_of_days_display
    #                 leave.status = leave_ids.state
    #                 leave.applied_on = leave_ids.create_date
    #                 days_between_last_leave = leave.request_date_from - leave_ids.request_date_to
    #                 leave.days_between_last_leave = days_between_last_leave.days - 1
    #
    #                 d1 = leave_ids.request_date_to   # start date
    #                 d2 = leave.request_date_from  # end date
    # #                 print("////////////////////////////////////",((d2-d1).days + 1),leave_ids.request_date_to )
    #                 days = [d1 + timedelta(days=x) for x in range((d2-d1).days + 1)]
    # #                 print("????????????????????????????????",days)
    #                 for day in days:
    #                     week = day.strftime('%Y-%m-%d')
    #                     print("weekkkkkkk",week)
    #                     year, month, day = (int(x) for x in week.split('-'))
    #                     answer = date(year, month, day).strftime('%A')
    # #                     print(":<<<<<<<<<<<<<<<<<<<<<<<<<<",answer)
    #                     if answer == 'Saturday' or answer == 'Sunday' or answer == 'Saturday' and answer == 'Sunday':
    #                         leave.are_days_weekend = True
    #                         raise ValidationError(_('You are not allowed to apply for leave during this date range because of Sandwich rule applicability on this leave type'))

    #

    @api.constrains('date_from', 'date_to', 'holiday_status_id')
    @api.onchange('date_from', 'date_to', 'holiday_status_id')
    def get_validate_on_holiday_status_id(self):
        employee_id = self.env['hr.employee'].search([('identify_id', '=', self.env.user.login)], limit=1)
        print('--====nmbmmnbnbmmmmmmmmmmmmmmmmmmm====', employee_id)
        if self.holiday_status_id:
            if self.holiday_status_id.half_pay_allowed == True:
                self.half_pay_allowed = True
            else:
                self.half_pay_allowed = False
            print('===========================half_pay_allowed====================================', self.half_pay_allowed)
            if self.holiday_status_id.maximum_allow_leave != 0:
                if self.holiday_status_id.maximum_allow_leave < self.number_of_days_display:
                    raise ValidationError(_('Crossing allowed limit'))
                
            # if self.max_leaves < self.number_of_days_display:
            #     raise ValidationError(_('Leave duration should be less than entitled leave.'))

            ## Modified : Nikunja (May 27 2021) : Start
            # if self.request_date_from and self.request_date_to and self.holiday_status_id.minimum_allow_leave > self.number_of_days_display:
            #     raise ValidationError(f"Minimum '{self.holiday_status_id.minimum_allow_leave}' day(s) required.")
            ## Modified : Nikunja (May 27 2021) : End

        if self.holiday_status_id:
            if self.holiday_status_id.cerificate == True:
                self.attachement = True
            else:
                self.attachement = False

        # if self.holiday_status_id:
        #     if self.holiday_status_id.commuted == True:
        #         # self.commuted_leave_selection = 'Yes'
        #         self.commuted = True
        #         # self.commuted_leave = 'Commuted Leaves'
        #     else:
        #         # self.commuted_leave_selection = 'No'
        #         self.commuted = False

        if self.holiday_status_id:
            if self.holiday_status_id.leave_type.code == 'Half Pay Leave':
                self.holiday_half_pay = True
                # self.no_of_days_display_half = self.number_of_days_display
            else:
                self.holiday_half_pay = False
## Nikunja - Aug 23 2021
        # if self.commuted_leave_selection == 'Yes':
        #     self.commuted_leave = 'Commuted Leaves'
        #     self.no_of_days_display_half = self.number_of_days_display * 2
        #     self.duration_display = self.number_of_days_display * 2
        #     self.number_of_days_display = self.no_of_days_display_half
        if employee_id:
            return {'domain': {'holiday_status_id': ['|', ('gende', '=', 'transgender'), ('gende', '=', employee_id.gende)]}}
        print("no_of_days_display_half ----------------------",self.no_of_days_display_half)
        print("duration_display ----------------------",self.duration_display)
        print("number_of_days_display ------------------------",self.number_of_days_display)


## Nikunja - Aug 23 2021
    # @api.constrains('commuted_leave_selection')
    # @api.onchange('commuted_leave_selection')
    # def get_validate_on_commuted_leave_selection(self):
    #     if self.holiday_status_id:
    #         if self.commuted_leave_selection == 'Yes':
    #             self.commuted_leave = 'Commuted Leaves'
    #             # self.no_of_days_display_half = self.number_of_days_display * 2
    #             # self.duration_display = self.number_of_days_display * 2
    #         else:
    #             self.no_of_days_display_half = self.number_of_days_display

    #     print("O -- no_of_days_display_half ---------------------",self.no_of_days_display_half)
    #     print("O -- duration_display ------------------------",self.duration_display)
    #     print("O -- number_of_days_display-------------------",self.number_of_days_display)
## Nikunja - Aug 23 2021
    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.allocation_type == 'no':
                continue
            leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id)[holiday.holiday_status_id.id]
            # if holiday.holiday_status_id.leave_per_year != 0:
            if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                    float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                        'Please also check the leaves waiting for validation.'))    
                   
    # @api.constrains('date_from', 'date_to', 'holiday_status_id')
    # @api.onchange('date_from', 'date_to', 'holiday_status_id')
    # def check_date_from_live(self):
    #     res = {}
    #     if self.employee_id:
    #         if self.holiday_status_id.sandwich_rule == False:
    #             days = []
    #             for each in self.employee_id.resource_calendar_id.attendance_ids:
    #                 if int(each.dayofweek) not in days:
    #                     days.append(int(each.dayofweek))
    #             if self.date_from:
    #
    #                 start_date = self.date_from
    #                 date_number = start_date.weekday()
    #                 #                     print("==================",date_number,days)
    #                 if date_number not in days:
    #                     res.update({'value': {'date_to': '', 'date_from': '', 'number_of_days_display': 0.00,
    #                                           'sandwich_rule': False}, 'warning': {
    #                         'title': 'Validation!',
    #                         'message': 'Since the leave you are applying has got weekends/holidays in between.You are requested to edit the last leave and apply covering the weekends/Holidays..'}})
    #             if self.date_to:
    #                 end_date = self.date_to
    #                 date_number = end_date.weekday()
    #                 if date_number not in days:
    #                     res.update({'value': {'date_to': '', 'number_of_days_display': 0.00, 'sandwich_rule': False},
    #                                 'warning': {
    #                                     'title': 'Validation!',
    #                                     'message': 'Since the leave you are applying has got weekends/holidays in between. You are requested to edit the last leave and apply covering the weekends/Holidays..'}})
    #
    #     return res

    # @api.constrains('request_date_from', 'request_date_to', 'employee_id')
    # @api.onchange('request_date_from', 'request_date_to', 'employee_id')
    # def get_half_pay_leave_2(self):
    #     if self.request_date_from and self.request_date_to:
    #         if self.request_date_from == self.request_date_to:
    #             self.allow_request_unit_half_2 = True
    #         else:
    #             self.allow_request_unit_half_2 = False

    # @api.constrains('request_date_from', 'request_date_to', 'employee_id','request_unit_half','request_unit_half_2')
    # @api.onchange('request_date_from', 'request_date_to', 'employee_id','request_unit_half','request_unit_half_2')
    # def get_half_pay_leave_2(self):
    #     if self.request_date_from and self.request_date_to:
    #         if self.request_date_from == self.request_date_to:
    #             # print("Yes")
    #             if self.request_unit_half:
    #                 self.request_unit_half_2 = False
    #                 self.allow_request_unit_half_2 = True
    #                 self.allow_request_unit_half = False
    #             elif self.request_unit_half_2:
    #                 self.request_unit_half = False
    #                 self.allow_request_unit_half_2 = False
    #                 self.allow_request_unit_half = True
    #             else:
    #                 self.allow_request_unit_half_2 = False
    #                 self.allow_request_unit_half = False
    #         else:
    #             self.allow_request_unit_half_2 = False
    #             self.allow_request_unit_half = False


## Nikunja - Aug 23 2021
    @api.constrains('date_from', 'date_to', 'employee_id', 'request_unit_half_2')
    @api.onchange('date_from', 'date_to', 'employee_id', 'request_unit_half_2','holiday_status_id')
    def _onchange_leave_dates(self):
        if self.date_from and self.date_to and self.holiday_status_id.leave_type.code != 'Restricted Holiday':
            days = 0.0
            days += self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)['days']
            if self.request_unit_half_2 == True:
                days = days - 0.5
            # print("days", days)
                self.number_of_days = days
                print("days", days)

            # 5/0
            # else:
            #     self.number_of_days = 0

            # self.no_of_days_display_half = 0
## Nikunja - Aug 23 2021
    
    def fun_action_refuse(self):
        today = date.today()
        refuse = True
        for leave in self:
            print('0000',leave.cancel_req )
            if leave.cancel_req == False and leave.state == 'validate':
                raise ValidationError(_("You are not allowed to cancel any leave untill the cancellation request is not send."))
            leave.manager_designation_id = None
            leave.pending_since = None
            leave.cancel_req = False
        if self.holiday_status_id.carried_forward != True and self.holiday_status_id.leave_type.code!= 'Maternity Leave':
            if self.request_date_from:
                year = self.request_date_from.year
                #                 print("LLLLLLLLLLLLLLLLLLLLLLLLLLLL",year,today.year)
                if today.year != year:
                    #                     print("?///////////////////")
                    raise ValidationError(_("You are not allowed to carried forward leave because leave is not in current year"))
                else:
                    refuse = super(HrLeave, self).action_refuse()
        else:
            refuse = super(HrLeave, self).action_refuse()
        self.env.user.notify_info("Leave Refused.")
        return refuse

    # 
    def action_approve_cancel(self):
        self.fun_action_refuse()
        # pass
    
    #(wagisha) cancellation reason
    def action_cancel_rejection(self):
        form_view_id = self.env.ref("leaves_stpi.ra_cancell_remark_form").id 
        action= {
            'name':'Cancellation Reason',
            'type': 'ir.actions.act_window',
            'res_model': 'leave.cancellation.request',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'default_leave_id': self.id}
            
        }
        return action
        # self.cancel_req = False

    #(wagisha) refuse reason
    def action_refuse(self):
        form_view_id = self.env.ref("leaves_stpi.ra_remark_form").id 
        action= {
            'name':'Cancellation Reason',
            'type': 'ir.actions.act_window',
            'res_model': 'leave.cancellation.request',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'default_leave_id': self.id}
            
        }
        return action
    
    def action_confirm(self):
        for leave in self:
            created_date = leave.create_date
            leave.manager_designation_id = leave.employee_id.parent_id.job_id
            leave.pending_since = created_date.strftime('%Y-%m-%d')
        if self.virtual_leaves_taken + self.number_of_days_display > self.max_leaves:
             raise ValidationError(_('You cannot take leave more than entitled leave. Please edit and add valid dates.'))
        return super(HrLeave, self).action_confirm()

    
    def action_approve(self):
        today = date.today()
        approve = True
        for leave in self:
            #             print("Pppppppppppppppppppppp")
            leave.pending_since = None
            leave.manager_designation_id = None
            #             print("??????????????????????????/??",leave.pending_since)
            if not leave.name:
                leave.name = '-'
                approve =  super(HrLeave, self).action_approve()
            else:
                approve = super(HrLeave, self).action_approve()
        # self.env.user.notify_success("Leave Approved.")
        return approve

    
    def action_cancel(self):
        self.pending_since = None
        self.write({'state': 'cancel'})


    
    def _create_resource_leave(self):
        """ This method will create entry in resource calendar leave object at the time of holidays validated """
        for leave in self:
            date_from = fields.Datetime.from_string(leave.date_from)
            date_to = fields.Datetime.from_string(leave.date_to)
            # print("resource_calendar_leavesresource_calendar_leavesresource_calendar_leaves")
            self.env['resource.calendar.leaves'].create({
                'name': leave.name,
                'date_from': fields.Datetime.to_string(date_from),
                'holiday_id': leave.id,
                'date_to': fields.Datetime.to_string(date_to),
                'resource_id': leave.employee_id.resource_id.id,
                'calendar_id': leave.employee_id.resource_calendar_id.id,
                'time_type': leave.holiday_status_id.time_type,
                'date': leave.date_from
            })
        return True

    @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
                  'request_date_from', 'request_date_to',
                  'employee_id','request_unit_half','request_unit_half_2')
    def _onchange_request_parameters(self):
        if self.request_date_from and self.request_date_to:
            if self.request_date_from == self.request_date_to:
                # print("Yes")
                if self.request_unit_half == True:
                    self.request_unit_half_2 = False
                    self.allow_request_unit_half_2 = True
                    self.allow_request_unit_half = False
                elif self.request_unit_half_2 == True:
                    self.request_unit_half = False
                    self.allow_request_unit_half_2 = False
                    self.allow_request_unit_half = True
                else:
                    self.allow_request_unit_half_2 = False
                    self.allow_request_unit_half = False
            else:
                self.allow_request_unit_half_2 = False
                self.allow_request_unit_half = False
            
        if not self.request_date_from:
            self.date_from = False
            return

        if self.request_unit_half or self.request_unit_hours:
            print()
            # comment below line because when we select half day it change the to date
        #             self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return

        #         roster_id = self.env['hr.attendance.roster'].search([('employee_id','=',self.employee_id.id),('date','=',self.date_from.date())],limit=1)
        #         # print("-------------roster_id", roster_id)
        #         if roster_id and roster_id.shift_id:
        #             if roster_id.shift_id.night_shift:
        #                 self.night_shift = True
        #             else:
        #                 self.night_shift = False
        #             domain =[('calendar_id', '=',roster_id.shift_id.id)]
        #         else:
        #             if self.employee_id.resource_calendar_id.night_shift or self.env.user.company_id.resource_calendar_id.night_shift:
        #                 self.night_shift = True
        #             else:
        #                 self.night_shift = False
        domain = [('calendar_id', '=',
                   self.employee_id.resource_calendar_id.id or self.env.user.company_id.resource_calendar_id.id)]
        attendances = self.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

        # find first attendance coming after first_day
        attendance_from = next((att for att in attendances if int(att.dayofweek) >= self.request_date_from.weekday()),
                               attendances[0])
        # find last attendance coming before last_day
        attendance_to = next(
            (att for att in reversed(attendances) if int(att.dayofweek) <= self.request_date_to.weekday()),
            attendances[-1])

        if self.request_unit_half:
            if self.request_date_from_period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                # print("hour_fromhour_fromhour_fromhour_from",hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
                # print("???????//hour_fromhour_fromhour_from",hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)

        elif self.request_unit_hours:
            # This hack is related to the definition of the field, basically we convert
            # the negative integer into .5 floats
            hour_from = float_to_time(
                abs(self.request_hour_from) - 0.5 if self.request_hour_from < 0 else self.request_hour_from)
            #             print("111111111111111111111111111111111",hour_from)
            hour_to = float_to_time(
                abs(self.request_hour_to) - 0.5 if self.request_hour_to < 0 else self.request_hour_to)
        #             print("22222222222222222222222222222",hour_to)
        elif self.request_unit_custom:
            hour_from = self.date_from.time()
            hour_to = self.date_to.time()
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)

        tz = self.env.user.tz if self.env.user.tz and not self.request_unit_custom else 'UTC'  # custom -> already in UTC
        self.date_from = timezone(tz).localize(datetime.combine(self.request_date_from, hour_from)).astimezone(
            UTC).replace(tzinfo=None)
        self.date_to = timezone(tz).localize(datetime.combine(self.request_date_to, hour_to)).astimezone(UTC).replace(
            tzinfo=None)
        
        self._onchange_leave_dates()
        self.onchange_number_od()
    
    def get_employee_leave_detail(self,leave_code, employee_id, date_from, date_to):
    # def get_employee_leave_detail(self,leave_code, employee_id = 1, date_from = date(2021, 8, 1), date_to = date(2021, 8, 31)):
        leave_days = []
        domain = []
        # leave_code = 'HPL'
        print(leave_code,employee_id,date_from,date_to)
        employee = self.env['hr.employee'].browse(employee_id)
        if employee:
            if leave_code == 'HPL':
                domain = [
                        '&', ('state', '=', 'validate'),
                        '&', ('employee_id', '=', employee.id),
                        '&', ('is_commuted', '=', False),
                        '&', ('holiday_status_id.leave_type.code', '=', 'Half Pay Leave'),
                        '|',
                        '|',
                        '&', ('request_date_from', '<=', date_from), ('request_date_to', '>=', date_from),
                        '|',
                        '&', ('request_date_from', '<=', date_to), ('request_date_to', '>=', date_to),
                        '&', ('request_date_from', '<=', date_from), ('request_date_to', '>=', date_to),
                        '|',
                        '&', ('request_date_from', '>=', date_from), ('request_date_from', '<=', date_to),
                        '&', ('request_date_to', '>=', date_from), ('request_date_to', '<=', date_to)
                    ]
            elif leave_code == 'CCL':
                domain = [
                        '&', ('state', '=', 'validate'),
                        '&', ('employee_id', '=', employee.id),
                        '&', ('holiday_status_id.leave_type.code', '=', 'Child Care Leave'),
                        '|',
                        '|',
                        '&', ('request_date_from', '<=', date_from), ('request_date_to', '>=', date_from),
                        '|',
                        '&', ('request_date_from', '<=', date_to), ('request_date_to', '>=', date_to),
                        '&', ('request_date_from', '<=', date_from), ('request_date_to', '>=', date_to),
                        '|',
                        '&', ('request_date_from', '>=', date_from), ('request_date_from', '<=', date_to),
                        '&', ('request_date_to', '>=', date_from), ('request_date_to', '<=', date_to)
                    ]

            leave_records = self.env['hr.leave'].sudo().search(domain)
            print("Leaves in ",leave_records)

            for leaves in leave_records:
                leave_days += [leaves.request_date_from + timedelta(days=day) for day in range((leaves.request_date_to-leaves.request_date_from).days + 1)]
            
            counts = []
            for days in leave_days:
                if days >= date_from and days <= date_to:
                    counts.append(days)

        print("Final count ",counts,"length = ",len(counts))   
        return {'code':leave_code,'days':counts, 'leave_records': leave_records}

    def create_cancellation(self):
        form_view_id = self.env.ref("leaves_stpi.create_cancellationform").id 
        action= {
            'name':'Cancellation Request',
            'type': 'ir.actions.act_window',
            'res_model': 'leave.cancellation.request',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'default_leave_id': self.id}
        }
        return action

    # def add_remarks(self):
    #     form_view_id = self.env.ref("leaves_stpi.create_remarksform").id 
    #     action= {
    #         'name': 'Remarks',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'leave.remarks',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'view_id': form_view_id,
    #         'target': 'new',
    #         'context': {'default_leave_id': self.id, 'default_remarks': self.report_note if self.report_note else False}
    #     }
    #     return action

class HRLeavePrePost(models.Model):
    _name = 'hr.leave.pre.post'
    _description = 'HR Leave Pre Post'

    pre_post_leave = fields.Many2one('hr.leave', string="Leaves", store=True)

    pre_post = fields.Selection([('pre', 'Pre'),
                                 ('post', 'Post')
                                 ], string="Pre/Post")
    leave_type_id = fields.Many2one('hr.leave.type', readonly=True)
    holiday = fields.Char(readonly=True)
    from_date = fields.Date(string="From Date", readonly=True)
    to_date = fields.Date(string="To Date", readonly=True)
    no_of_days_leave = fields.Float(string="No of Days Leave", readonly=True)
    leave = fields.Selection([('holiday', 'H'),
                              ('leave', 'L')
                              ], string="Leave Is")
    status = fields.Selection([('draft', 'To Submit'),
                               ('cancel', 'Cancelled'),
                               ('confirm', 'To Approve'),
                               ('refuse', 'Refused'),
                               ('validate1', 'Second Approval'),
                               ('validate', 'Approved')
                               ], string="Status", readonly=True)
    applied_on = fields.Datetime(string="Applied On", readonly=True, invisible=True)
    days_between_last_leave = fields.Float(string="Days Between Last Leave", readonly=True)
    are_days_weekend = fields.Boolean(string="Are Days Weekend", readonly=True)

class LeaveCancellationRequest(models.Model):
    _name = 'leave.cancellation.request'
    _description = 'Leave Cacellation'

    leave_id = fields.Many2one('hr.leave', string="Leaves")
    reasons = fields.Char(string="Reason for cancellation")
    refuse_reason = fields.Char(string="Reason for refusing cancel request")
    my_refuse_reason = fields.Char(string="Reason for Refusal")
    
    def action_request(self):
        for req in self:
            req.leave_id.cancel_req = True
            req.leave_id.ignore_exception = False
            req.leave_id.approved = False
            req.leave_id.cancel_reason = req.reasons

    def refuse_cancel_request(self):
        for rec in self:
            rec.leave_id.cancel_req = False
            rec.leave_id.refuse_cancel_reason = rec.refuse_reason

    def refuse_reason_manager(self):
        for rec in self:
            rec.leave_id.refuse_reason = rec.my_refuse_reason
        self.leave_id.fun_action_refuse()

    @api.constrains('reasons')
    def _check_reasons_validation(self):
        for rec in self:
            if rec.reasons and not (re.match('^[A-Za-z][ a-zA-Z0-9]+$', rec.reasons)):
                raise ValidationError("Reasons should start with alphabets. In reason alphabets and numbers are allowed")
            if rec.reasons:
                if len(rec.reasons) > 500:
                    raise ValidationError('Number of characters must not exceed 500.')
                
    @api.constrains('refuse_reason')
    def _check_refuse_reason_validation(self):
        for rec in self:
            if rec.refuse_reason and not (re.match('^[A-Za-z][ a-zA-Z0-9]+$', rec.refuse_reason)):
                raise ValidationError("Reasons should start with alphabets. In reason alphabets and numbers are allowed")
            if rec.refuse_reason:
                if len(rec.refuse_reason) > 500:
                    raise ValidationError('Number of characters must not exceed 500.')
                
    @api.constrains('my_refuse_reason')
    def _check_my_refuse_reason_validation(self):
        for rec in self:
            if rec.my_refuse_reason and not (re.match('^[A-Za-z][ a-zA-Z0-9]+$', rec.my_refuse_reason)):
                raise ValidationError("Reasons should start with alphabets. In reason alphabets and numbers are allowed")
            if rec.my_refuse_reason:
                if len(rec.my_refuse_reason) > 500:
                    raise ValidationError('Number of characters must not exceed 500.')


class LeaveRemarks(models.Model):
    _name = 'leave.remarks'
    _description = 'Leave Remarks'

    leave_id = fields.Many2one('hr.leave', string="Leaves")
    remarks = fields.Char(string="Remarks")

    # 
    def action_done(self):
        for req in self:
            req.leave_id.remarks_req = True
            req.leave_id.edit_req = True
            req.leave_id.report_note = req.remarks
