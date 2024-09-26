# -*- coding: utf-8 -*-
from datetime import datetime, time, timedelta, date
from pytz import timezone, UTC
from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError, Warning
from datetime import date

from odoo.tools.misc import format_date
from odoo.addons.kw_hr_leaves.models.kw_leave_approval_log import STS_PENDING, STS_APPROVE, STS_REJECT, STS_CANCEL, \
    STS_FORWARD, STS_HOLD

from odoo.addons.kw_utility_tools import kw_validations


# def lv_get_current_financial_dates():
#     current_date = date.today()
#     current_year = date.today().year
#     if current_date < date(current_year, 4, 1):
#         start_date = date(current_year-1, 4, 1)
#         end_date = date(current_year, 3, 31)
#     else:
#         start_date = date(current_year, 4, 1)
#         end_date = date(current_year+1, 3, 31)
#     return start_date,end_date

# start_date, end_date = lv_get_current_financial_dates()

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    """Overriding the existing default get method of hr.leave model"""

    @api.model
    def default_get(self, fields_list):
        defaults = super(HrLeave, self).default_get(fields_list)
        defaults = self._default_get_request_parameters(defaults)

        LeaveType = self.env['hr.leave.type'].with_context(employee_id=defaults.get('employee_id'),
                                                           default_date_from=defaults.get('date_from',
                                                                                          fields.Datetime.now()))
        lt = LeaveType.search([('valid', '=', True)])

        defaults['holiday_status_id'] = False  # lt[0].id if len(lt) > 0 else defaults.get('holiday_status_id')

        return defaults

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=False,
                                  default=_default_employee,
                                  track_visibility='onchange')  # readonly=True,states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
    department = fields.Char(string="Department", related="employee_id.department_id.name")
    division = fields.Char(string="Division", related="employee_id.division.name")
    section = fields.Char(string="Section", related="employee_id.section.name")
    designation = fields.Char(string="Designation", related="employee_id.job_id.name")
    date_from = fields.Datetime(
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)], 'hold': [('readonly', False)],
                'forward': [('readonly', False)]})
    date_to = fields.Datetime(
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)], 'hold': [('readonly', False)],
                'forward': [('readonly', False)]})
    number_of_days = fields.Float(
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)], 'hold': [('readonly', False)],
                'forward': [('readonly', False)]})

    request_date_from_period = fields.Selection([('am', 'First Half'), ('pm', 'Second Half')],
                                                string="Date Period Start", default='am')

    request_date_to_period = fields.Selection([('am', 'First Half'), ('pm', 'Second Half')],
                                              string="Date Period End", default='am')
    # request type
    request_unit_half_to_period = fields.Boolean('Half Day')
    name = fields.Text('Reason', size=500, required=True)

    leave_address1 = fields.Text(string="Leave Address(1)", size=300, )
    leave_address2 = fields.Text(string="Leave Address(2)", size=300)
    phone_no = fields.Char(string="Mobile No", size=15)
    medical_doc = fields.Binary(string='Document', attachment=True)
    ref_name = fields.Char(string='File Name')

    leave_code = fields.Char(string="Leave Code", related="holiday_status_id.leave_code")
    # state                       = fields.Selection(selection_add=[('hold', 'On Hold'),('forward', 'Forwarded')])
    state = fields.Selection([('draft', 'To Submit'),
                              ('cancel', 'Cancelled'),
                              ('confirm', 'To Approve'),
                              ('refuse', 'Rejected'),
                              ('validate1', 'Second Approval'),
                              ('validate', 'Approved'),
                              ('hold', 'On Hold'),
                              ('forward', 'Forwarded')
                              ], string='Status', readonly=True, track_visibility='onchange', copy=False,
                             default='confirm',
                             help="The status is set to 'To Submit', when a leave request is created." +
                                  "\nThe status is 'To Approve', when leave request is confirmed by user." +
                                  "\nThe status is 'Rejected', when leave request is refused by manager." +
                                  "\nThe status is 'Approved', when leave request is approved by manager.")

   

    holiday_status_id = fields.Many2one("hr.leave.type", string="Leave Type", required=True, readonly=True,
                                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)],
                                                'hold': [('readonly', False)],
                                                'forward': [('readonly', False)]},)
    leave_sub_type_id = fields.Many2one("hr.leave.type", string="Sub-Leave Type", readonly=True,
                                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)],
                                                'hold': [('readonly', False)],
                                                'forward': [('readonly', False)]},
                                                )
    parent_holiday_status_id = fields.Many2one("hr.leave.type", string="Leave Type", required=True, readonly=True,
                                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)],
                                                'hold': [('readonly', False)],
                                                'forward': [('readonly', False)]},domain=[('parent_leave_id','=',False)])
    leave_sub_type_required = fields.Boolean(string='Leave Sub Type Required')
    
    @api.onchange('parent_holiday_status_id') 
    def get_leave_sub_type(self):
        if self.parent_holiday_status_id:
            child_sub_types = self.env['hr.leave.type'].search([('parent_leave_id', '=', self.parent_holiday_status_id.id)])
            self.leave_sub_type_id = False
            if child_sub_types:
                self.holiday_status_id = False
                self.leave_sub_type_required = True
                return {'domain': {'leave_sub_type_id': [('parent_leave_id', '=', self.parent_holiday_status_id.id)]}}
            else:
                self.leave_sub_type_required = False
                self.holiday_status_id = self.parent_holiday_status_id.id
                return {'domain': {'leave_sub_type_id': []}}
        else:
            self.leave_sub_type_id = False
            self.leave_sub_type_required = False
            self.holiday_status_id = False
            return {'domain': {'leave_sub_type_id': []}}
        
    @api.onchange('leave_sub_type_id')
    def onchange_leave_sub_type_id(self):
        if self.leave_sub_type_id:
            self.holiday_status_id = self.leave_sub_type_id.id
        else:
            self.holiday_status_id = self.parent_holiday_status_id.id if self.parent_holiday_status_id else False
            
        
    status = fields.Boolean(string="Status", compute='_compute_number_of_days_warning')
    message = fields.Text(string="Message", compute='_compute_number_of_days_warning')

    apply_for = fields.Selection([('self', 'Self'), ('others', 'Others')], default='self', string='Apply for')

    def _default_action_taken_by(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.employee_ids.parent_id.user_id.id)],
                                              limit=1)

    cancel_reason = fields.Text('Reason of Cancellation', size=500)

    is_approver = fields.Boolean(string="Action Taken Authority", compute='_compute_is_approver')
    from_day_half = fields.Char(string="From", compute='_compute_from')
    to_day_half = fields.Char(string="To", compute='_compute_to')

    # """Start : for displaying leave statistics"""
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
    # """End : for displaying leave statistics"""

    # """Start: Fields used for approval process flow"""
    second_approver_id = fields.Many2one(string="Pending At", default=_default_action_taken_by)
    forward_reason = fields.Text(string='Forward Reason', )

    authority_remark = fields.Text(string='Authority Remark', )
    first_approver_id = fields.Many2one(string="Action Taken By")
    action_taken_on = fields.Datetime(string="Action Taken On")
    action_type = fields.Char('Action Type', )
    leave_cycle_id = fields.Many2one('kw_leave_cycle_master', string="Leave Cycle")
    cycle_period = fields.Integer(string="Cycle Period")
    actual_number_of_days = fields.Float(string='No. Of Days Applied')

    current_financial_year = fields.Boolean("Current Financial Year", compute='_compute_current_financial_year',
                                            search="_lv_search_current_financial_year")

    previous_financial_year = fields.Boolean("Previous Financial Year", compute='_compute_current_financial_year',
                                            search="_lv_search_previous_financial_year")
    applied_by = fields.Selection(selection=[('1', 'Employee'), ('2', 'RA'), ('3', 'HR Manager')],
                                  compute='_compute_applied_by', string='Applied By')

    action_taken_date = fields.Date(string="Action Taken On", compute='_compute_action_taken_date')
    employee_company_id = fields.Many2one('res.company',related_sudo=True,related="employee_id.user_id.company_id", string="Employee Company")

    @api.multi
    def _compute_action_taken_date(self):
        for leave in self:
            leave.action_taken_date = leave.action_taken_on.date() if leave.action_taken_on else False

    # fields used for forwarding the request
    @api.onchange('employee_id')
    def get_leave_types(self):
        company_id = self.env['res.company'].sudo().search([('id','=',self.employee_id.user_id.company_id.id)])
        return {'domain': {'holiday_status_id': ([('valid', '=', True),('company_id','=',company_id.id)])}}
    
    @api.constrains('medical_doc')
    def _check_uploaded_image(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        if self.medical_doc:
            kw_validations.validate_file_mimetype(self.medical_doc, allowed_file_list)
            kw_validations.validate_file_size(self.medical_doc, 10)

    @api.constrains('holiday_status_id')
    def _check_maternity_leave_cycle(self):
        for holiday in self:
            cycle_record = self.env['kw_leave_cycle_master'].search(
                [('branch_id', '=', holiday.employee_id.job_branch_id.id or False), ('cycle_id', '!=', False),
                 ('active', '=', True)], limit=1)
            if cycle_record:
                existing_record = self.env['hr.leave'].search([('holiday_status_id', '=', holiday.holiday_status_id.id),
                                                               ('employee_id', '=', holiday.employee_id.id),
                                                               ('holiday_status_id.leave_code', '=', 'MT'),
                                                               ('leave_cycle_id', '=', cycle_record.id),
                                                               ('cycle_period', '=', cycle_record.cycle_period),
                                                               ('state', 'not in', ['cancel', 'refuse'])]) - holiday
                if existing_record:
                    raise ValidationError("Maternity leave can only take once in a single cycle period.")
            
            
            if holiday.holiday_status_id.encashable == True:
                if holiday.holiday_status_id.leave_code == 'EL':
                    encashment_id = self.env['kw_compute_cf_encashment'].search([('employee_id','=',holiday.employee_id.id),('fisc_year_id.date_start','<=',holiday.request_date_from),('fisc_year_id.date_stop','>=',holiday.request_date_from)],limit=1)
                    # print(encashment_id)
                    if encashment_id:
                        raise ValidationError("You can not apply Earned Leave as your leave encashment has been processed.")

    @api.multi
    def _compute_applied_by(self):
        for record in self:
            create_emp = self.env['hr.employee'].search([('user_id', '=', record.create_uid.id)], limit=1)
            if record.employee_id == create_emp:
                record.applied_by = '1'
            elif record.employee_id != create_emp and record.employee_id.parent_id == create_emp:
                record.applied_by = '2'
            else:
                record.applied_by = '3'

    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass

    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        start_date, end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        return ['&', ('create_date', '>=', start_date), ('create_date', '<=', end_date)]
    
    @api.multi
    def _lv_search_previous_financial_year(self, operator, value):
        start_date, end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        return [('cycle_period', '=', start_date.year - 1)]

    @api.onchange('employee_id', 'holiday_status_id')
    def _onchange_employee_id(self):
        leave_cyle = self.env['kw_leave_cycle_master'].search([('branch_id', '=', self.employee_id.job_branch_id.id if self.employee_id.job_branch_id else False),('cycle_id', '!=', False), ('active', '=', True)], limit=1)
        if self.employee_id and self.holiday_status_id and self.holiday_status_id.leave_code == 'EL':
            self.phone_no = self.employee_id.mobile_phone or self.employee_id.whatsapp_no
            self.leave_cycle_id = leave_cyle.id
        else:
            self.leave_cycle_id = leave_cyle.id
            self.phone_no = False

    @api.model
    def _get_forward_employees(self):
        leave_id = self._context.get('active_id', False)
        employee = self.env.user.employee_ids
        domain = [('user_id', '!=', False)]
        eos_con = self._context.get('hr_eos_leave_action')
        if leave_id and not eos_con:
            leave_id = self.env['hr.leave'].browse(leave_id)
            if leave_id and leave_id.employee_id:
                employee += leave_id.employee_id
                domain.append(('id', 'not in', employee.ids))
        
        return domain

    forward_to = fields.Many2one('hr.employee', string="Forward To", domain=_get_forward_employees)
    action_remark = fields.Text(string="Remark")
    forward_request = fields.Boolean(string='Forward Request', )

    approval_log_ids = fields.One2many(string='Approval Logs', comodel_name='kw_leave_approval_log',
                                       inverse_name='leave_id', )
    # """End: Fields used for approval process flow"""

    is_my_leave_request = fields.Boolean(string="My Leave Request", compute='_compute_is_my_leave_request')
    cancellation_log_ids = fields.One2many(string='Leave Cancellation Logs', comodel_name='kw_cancel_leave',
                                           inverse_name = 'approved_leave_id')

    is_cancel = fields.Boolean(compute="_compute_is_cancel")
    compute_log = fields.Boolean(compute="_compute_approval_log")

    @api.multi
    def _compute_approval_log(self):
        for record in self:
            record.compute_log = True if record.approval_log_ids else False

    @api.multi
    def _compute_is_cancel(self):
        for record in self:
            cancel_record = record.cancellation_log_ids.filtered(lambda res: res.status in ['apply', 'forward'])
            record.is_cancel = True if cancel_record else False

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        if self.date_from and self.date_to:
            if self.employee_id.resource_calendar_id.cross_shift == True:
                self.number_of_days = self._get_number_of_dayss(self.date_from, self.date_to, self.employee_id.id) - 1
            else:
                self.number_of_days = self._get_number_of_dayss(self.date_from, self.date_to, self.employee_id.id)
        else:
            self.number_of_days = 0

    @api.multi
    def _compute_is_my_leave_request(self):
        for rec in self:
            rec.is_my_leave_request = True if rec.user_id.id == self.env.uid else False

    @api.constrains('state', 'number_of_days', 'holiday_status_id','leave_sub_type_id')
    def _check_holidays(self):
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.allocation_type == 'no':
                continue
            if holiday.holiday_status_id.leave_code == 'CMP':
                leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id,None,None)[holiday.holiday_status_id.id]
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                    float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                        raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                        'Please also check the leaves waiting for validation.'))
            else:
                leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id,holiday.leave_cycle_id.id,None)[holiday.holiday_status_id.id]
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                    float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                        raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                            'Please also check the leaves waiting for validation.'))

    @api.depends('holiday_status_id','leave_sub_type_id', 'employee_id','leave_cycle_id')
    def _compute_waiting_for_approval_leaves(self):
        for holiday in self:
            # print("leave cycle",holiday.leave_cycle_id)
            if holiday.holiday_status_id and holiday.employee_id and holiday.leave_cycle_id:
                if holiday.holiday_status_id.leave_code == 'CMP':
                    holiday.max_leaves = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id,leave_cycle_id=None).max_leaves
                    holiday.leaves_taken = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id,leave_cycle_id=None).leaves_taken
                    holiday.remaining_leaves = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id,leave_cycle_id=None).remaining_leaves
                    holiday.virtual_remaining_leaves = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id,leave_cycle_id=None).virtual_remaining_leaves

                    holiday.waiting_for_approval_leaves = holiday.remaining_leaves - holiday.virtual_remaining_leaves
                else:
                    holiday.max_leaves = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id,leave_cycle_id=holiday.leave_cycle_id.id).max_leaves
                    holiday.leaves_taken = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id,cycle_period=holiday.leave_cycle_id.cycle_period).leaves_taken
                    holiday.virtual_remaining_leaves = holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id,cycle_period=holiday.leave_cycle_id.cycle_period).virtual_remaining_leaves

                    applied_leaves = self.search([('employee_id','=',holiday.employee_id.id),('holiday_status_id','=',holiday.holiday_status_id.id),('cycle_period','=',holiday.leave_cycle_id.cycle_period),('state','not in',['cancel', 'refuse','validate'])])
                    holiday.waiting_for_approval_leaves = sum(applied_leaves.mapped('number_of_days'))
                    holiday.remaining_leaves = holiday.max_leaves - holiday.leaves_taken
            
            else:
                holiday.max_leaves = 0
                holiday.leaves_taken = 0
                holiday.remaining_leaves = 0
                holiday.virtual_remaining_leaves = 0
                holiday.waiting_for_approval_leaves = 0

    @api.constrains('name')
    def _check_name(self):
        for holiday in self:
            if holiday.name and len(holiday.name) > 500:
                raise ValidationError('Please enter the reason within 500 characters only')

    @api.constrains('number_of_days', 'number_of_days_display')
    def _check_no_of_days(self):
        for holiday in self:
            if holiday.number_of_days == 0 or holiday.number_of_days_display == 0:
                raise ValidationError('No of days should be grater than 0')

    @api.constrains('request_date_from_period', 'request_date_to_period')
    def _check_no_of_days(self):
        for holiday in self:
            if holiday.request_date_to and holiday.request_date_from:
                if holiday.request_date_to == holiday.request_date_from:
                    if (holiday.request_unit_half_to_period and not holiday.request_unit_half) or (not holiday.request_unit_half_to_period and holiday.request_unit_half):
                        raise ValidationError('Leave duration combination is not correct.')

                    if holiday.request_date_from_period == 'pm' and holiday.request_date_to_period == 'am':
                        raise ValidationError('Leave duration combination is not correct.')

    # #validate if two type of leaves taken on a single day
    @api.constrains('request_unit_half', 'request_unit_half_to_period', 'holiday_status_id')
    def _check_duplicate_half_holiday_type(self):
        for holiday in self:
            domain = [
                ('holiday_status_id', '!=', holiday.holiday_status_id.id),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            if holiday.request_unit_half:
                fdomain = domain + [
                    ('request_date_from', '=', holiday.request_date_from),
                    ('request_date_from_period', '!=', holiday.request_date_from_period),
                ]

                nfholidays = self.search_count(fdomain)
                if nfholidays:
                    raise ValidationError('You can not have 2 type of leaves on the same day.')
            if holiday.request_unit_half_to_period:
                tdomain = domain + [
                    ('request_date_to', '=', holiday.request_date_to),
                    ('request_date_to_period', '!=', holiday.request_date_to_period),
                ]
                ntholidays = self.search_count(tdomain)
                if ntholidays:
                    raise ValidationError('You can not have 2 type of leaves on the same day.')
    

    @api.constrains('employee_id', 'holiday_status_id', 'request_date_from', 'request_date_to')
    def _validate_new_requests(self):
        """ Validate leave requests
        by requesting a resource leaves."""
        model_leave_type_config = self.env['kw_leave_type_config']
        model_leave_cycle = self.env['kw_leave_cycle_master']
        for holiday in self:
            # print(holiday)
            if holiday.employee_id and holiday.holiday_status_id:

                # if holiday.employee_id.resignation_aplied:
                #     raise ValidationError("You are Applied Resignation or on Notice period, You are not allowed to avail Leaves")   #do
                #{holiday.holiday_status_id.name}

                """Probation Period"""
                if not holiday.holiday_status_id.for_probationary and holiday.employee_id.on_probation:
                    raise ValidationError(f"You are in probation period, You are not allowed to avail {holiday.holiday_status_id.name}")

                """Service Days"""
                config_records = model_leave_type_config.search([('leave_type_id', '=', holiday.holiday_status_id.id)])
                filtered_result = []
                if config_records:
                    filtered_result = config_records.filtered(lambda res: res.branch_id.id == holiday.employee_id.job_branch_id.id) if config_records.filtered( lambda res: res.branch_id.id == holiday.employee_id.job_branch_id.id) else config_records.filtered(lambda res: res.branch_id.id == False)
                    if filtered_result and filtered_result.service_days > 0:
                        start_date = holiday.employee_id.date_of_joining if holiday.employee_id.date_of_joining else False
                        end_date = holiday.request_date_from if holiday.request_date_from else False
                        if start_date and end_date:
                            total_service_days = (end_date - start_date).days
                            if filtered_result.service_days > total_service_days:
                                raise ValidationError(f"You are not allowed to avail {holiday.holiday_status_id.name}, required service days {filtered_result.service_days}.\n {holiday.employee_id.name} has working days {total_service_days}.")

                """Leave Availability Restrict"""
                if not holiday.holiday_status_id.is_comp_off and filtered_result and filtered_result.avail_leave_within_cycle:

                    cycle_records = model_leave_cycle.search(
                        [('branch_id', '=', holiday.employee_id.job_branch_id.id or False), ('cycle_id', '!=', False),
                         ('active', '=', True)], limit=1)
                    if cycle_records:
                        cycle_results = cycle_records.filtered(lambda cycle: cycle.from_date <= holiday.request_date_from and cycle.to_date >= holiday.request_date_from and cycle.from_date <= holiday.request_date_to and cycle.to_date >= holiday.request_date_to)
                        if not cycle_results:
                            raise ValidationError(f"You can apply leave in between cycle {cycle_records.from_date.strftime('%d-%b-%Y')} to {cycle_records.to_date.strftime('%d-%b-%Y')}.")

    @api.onchange('request_unit_half_to_period')
    def _onchange_request_unit_half_to(self):
        if self.request_unit_half_to_period:
            self.request_unit_hours = False
            self.request_unit_custom = False
        self._onchange_request_parameters()

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        if self.holiday_status_id:
            self._onchange_request_parameters()
            self._compute_number_of_days_warning()

            # @api.multi

    def _get_number_of_dayss(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            # resource_calendar_id.branch_id
            branch_config = self.holiday_status_id.leave_type_config_ids.filtered(lambda res: res.branch_id.id == employee.job_branch_id.id) if self.holiday_status_id.leave_type_config_ids.filtered(lambda res: res.branch_id.id == employee.job_branch_id.id) else self.holiday_status_id.leave_type_config_ids.filtered(lambda res: res.branch_id.id == False)
            # self.holiday_status_id.leave_type_config_ids.filtered(lambda rec: rec.branch_id.id == employee.job_branch_id.id or False)
            
            exclude_leaves = branch_config.exclude_holiday if branch_config else False
            # print(branch_config.exclude_holiday)
            roaster_shift = self.env['kw_employee_roaster_shift'].search(
                    [('employee_id', '=', employee_id), ('date', '>=', date_from.date()), ('date', '<=', date_to.date())])
            global_leave_ids = self.env['resource.calendar.leaves'].search([('start_date','>=',date_from.date()),('start_date','<=',date_to.date())])
            if roaster_shift:
                total_days = employee.kw_get_work_days_data(datetime.combine(date_from.date(), time.min),
                                                        datetime.combine(date_to.date(), time.max), exclude_leaves)['days']
                # print(total_days)
                total_days = total_days + 1 if global_leave_ids and exclude_leaves else total_days
                
            else:
                total_days = employee.kw_get_work_days_data(datetime.combine(date_from.date(), time.min),
                                                        datetime.combine(date_to.date(), time.max), exclude_leaves)['days']
            
            if self.request_unit_half and self.request_date_from_period:
                if self.request_date_from_period == 'pm':
                    total_days -= .5
            if self.request_unit_half_to_period and self.request_date_to_period:
                if self.request_date_to_period == 'am':
                    total_days -= .5

            # if employee.resource_calendar_id.cross_shift == True:
            #     if self.request_date_from_period == 'pm' and self.request_date_to_period == 'pm':
            #         total_days -= 1
            # print(total_days)
            return total_days

        today_hours = self.env.user.company_id.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(), time.min),
            datetime.combine(date_from.date(), time.max),
            False)

        return self.env.user.company_id.resource_calendar_id.get_work_hours_count(date_from, date_to) / (today_hours or HOURS_PER_DAY)

    # #override the existing method
    @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to', 'request_date_from',
                  'request_date_to', 'request_date_to_period', 'request_unit_half_to_period', 'employee_id')
    def _onchange_request_parameters(self):
        if not self.request_date_from:
            self.date_from = False
            return

        # if self.request_unit_half or self.request_unit_hours:
        #     self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return

        domain = [('calendar_id', '=', self.employee_id.resource_calendar_id.id or self.env.user.company_id.resource_calendar_id.id)]
        attendances = self.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

        # find first attendance coming after first_day
        attendance_from = next((att for att in attendances if int(att.dayofweek) >= self.request_date_from.weekday()), attendances[0])
        # find last attendance coming before last_day
        attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= self.request_date_to.weekday()), attendances[-1])
        if self.request_unit_half or self.request_unit_half_to_period:
            if self.request_date_from_period == 'am' and self.request_date_to_period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            elif self.request_date_from_period == 'am' and self.request_date_to_period == 'pm':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
            elif self.request_date_from_period == 'pm' and self.request_date_to_period == 'am':
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)

        elif self.request_unit_hours:
            # This hack is related to the definition of the field, basically we convert
            # the negative integer into .5 floats
            hour_from = float_to_time(
                abs(self.request_hour_from) - 0.5 if self.request_hour_from < 0 else self.request_hour_from)
            hour_to = float_to_time(
                abs(self.request_hour_to) - 0.5 if self.request_hour_to < 0 else self.request_hour_to)
        elif self.request_unit_custom:
            hour_from = self.date_from.time()
            hour_to = self.date_to.time()
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)

        # print(hour_from,hour_to)
        tz = self.env.user.tz if self.env.user.tz and not self.request_unit_custom else 'UTC'  # custom -> already in UTC
        if self.employee_id.resource_calendar_id.cross_shift ==  True:
            self.date_from = datetime.combine(self.request_date_from, time.min)
            self.date_to = datetime.combine(self.request_date_to, time.max)
        else:
            self.date_from = timezone(tz).localize(datetime.combine(self.request_date_from, hour_from)).astimezone(UTC).replace(tzinfo=None)
            self.date_to = timezone(tz).localize(datetime.combine(self.request_date_to, hour_to)).astimezone(UTC).replace(tzinfo=None)
        self._onchange_leave_dates()
    @api.multi
    def action_approve(self):
        if any(holiday.state not in ['validate1','confirm', 'hold', 'forward'] for holiday in self):
            raise UserError(_('Leave request must be confirmed ("To Approve")  or on hold or forwarded in order to approve it.'))

        self.action_taken_on = datetime.now()
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1',
                                                                        'first_approver_id': current_employee.id})
        self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1',
                                                                        'second_approver_id': current_employee.id})
        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()
        if self.holiday_status_id.parent_leave_id :
            core_hr = self.env.ref("kw_hr_leaves.group_kw_leave_core_hr_user")
            core_hr_employees = core_hr.users.mapped('employee_ids') if core_hr else ''
            mail_to = ','.join(core_hr_employees.mapped('work_email'))  or ''
            template = self.env.ref('kw_hr_leaves.kw_hr_leave_second_approval_mail')
            template.with_context(mail_to=mail_to).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            template = self.env.ref('kw_hr_leaves.kw_hr_leave_approval_mail')
            template.send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        try:
            # #call the attendance leave approval update method
            self.env['kw_daily_employee_attendance'].attendance_leave_approval_update(self,False)
        except Exception as e:
            print(str(e))
            # pass

        return True

    @api.multi
    def action_validate(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if any(holiday.state not in ['confirm', 'validate1', 'hold', 'forward'] for holiday in self):
            raise UserError(_('Leave request must be confirmed or on hold or forwarded in order to approve it.'))
        if self.holiday_status_id.parent_leave_id :
            core_hr_group = self.env.ref("kw_hr_leaves.group_kw_leave_core_hr_user")
            core_hr_employees = self.env['hr.employee'].search([('user_id.groups_id', 'in', core_hr_group.id)])
            hr_emp_id = core_hr_employees[0].id if core_hr_employees else False
            self.write({'state': 'validate1'})
            self.write({'second_approver_id': hr_emp_id})
            if self.second_approver_id.user_id.id == self.env.uid:
                self.write({'state': 'validate'})
        else:
            self.write({'state': 'validate'})
        self.filtered(lambda holiday: holiday.validation_type == 'both').write({'second_approver_id': current_employee.id})
        self.filtered(lambda holiday: holiday.validation_type != 'both').write({'first_approver_id': current_employee.id})

        for holiday in self.filtered(lambda holiday: holiday.holiday_type != 'employee'):
            if holiday.holiday_type == 'category':
                employees = holiday.category_id.employee_ids
            elif holiday.holiday_type == 'company':
                employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
            else:
                employees = holiday.department_id.member_ids

            if self.env['hr.leave'].search_count(
                    [('date_from', '<=', holiday.date_to), ('date_to', '>', holiday.date_from),
                     ('state', 'not in', ['cancel', 'refuse']), ('holiday_type', '=', 'employee'),
                     ('employee_id', 'in', employees.ids)]):
                raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

            values = [holiday._prepare_holiday_values(employee) for employee in employees]
            leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
            ).create(values)
            leaves.action_approve()
            # FIXME RLi: This does not make sense, only the parent should be in validation_type both
            if leaves and leaves[0].validation_type == 'both':
                leaves.action_validate()

        employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
        employee_requests._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            employee_requests.activity_update()
        return True

    def _validate_leave_request(self):
        """ Validate leave requests (holiday_type='employee')
        by creating a calendar event and a resource leaves. """
        holidays = self.filtered(lambda request: request.holiday_type == 'employee')
        holidays._create_resource_leave()
        # for holiday in holidays:
        #     meeting_values = holiday._prepare_holidays_meeting_values()
        #     meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
        #     holiday.write({'meeting_id': meeting.id})

    @api.model
    def create(self, values):

        # print(self.max_leaves)
        # print(values)
        res = super(HrLeave, self).create(values)
        if res.apply_for == 'others' or (res.apply_for == 'self' and not res.employee_id.parent_id):

            res.write({'authority_remark': "Auto Approved."})
            res.action_approve()
            self.env['kw_leave_approval_log'].create_approval_log(False, res, False,
                                                                  False, "Auto Approved.",
                                                                  self.env.user.employee_ids.id, STS_APPROVE)
        else:
            # (self,allocation_id,leave_id,cancel_leave_id,pending_at,authority_remark,action_taken_by,state)
            # print('#########################',res.second_approver_id)
            # print(sdfsdfd)
            self.env['kw_leave_approval_log'].create_approval_log(False, res, False, res.second_approver_id,
                                                                  'Leave Request', self.env.user.employee_ids.id,
                                                                  STS_PENDING)

            template = self.env.ref('kw_hr_leaves.kw_hr_leave_apply_mail')
            template.send_mail(res.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        active_cycle = self.env['kw_leave_cycle_master'].search(
            [('branch_id', '=', res.employee_id.job_branch_id.id if res.employee_id.job_branch_id else False),
             ('cycle_id', '!=', False), ('active', '=', True)], limit=1)
        if active_cycle:
            res.write({
                'leave_cycle_id': active_cycle.id,
                'cycle_period': active_cycle.cycle_period,
            })
        res.write({
            'actual_number_of_days': res.number_of_days or res.number_of_days_display
        })
        return res

    @api.multi
    def add_follower(self, employee_id):
        pass
        # employee = self.env['hr.employee'].browse(employee_id)
        # if employee.user_id:
        #     self.message_subscribe(partner_ids=employee.user_id.partner_id.ids)

    @api.multi
    def hold_leave(self):
        self.state = 'hold'
        self.action_taken_on = datetime.now()
        template = self.env.ref('kw_hr_leaves.kw_hr_leave_hold_mail')
        template.send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.multi
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if any(holiday.state not in ['confirm', 'validate', 'validate1', 'hold', 'forward'] for holiday in self):
            raise UserError(_('Leave request must be confirmed or hold or validated or forwarded in order to refuse it.'))

        # if not self.report_note:
        #     form_view_id = self.env.ref("kw_hr_leaves.view_kw_hr_leaves_comment_form").id
        #     return  {
        #         'type': 'ir.actions.act_window',
        #         'res_model': 'hr.leave',
        #         'view_mode': 'form',
        #         'view_type': 'form',
        #         'target': 'new',
        #         'res_id':self.ids[0],
        #         'view_id':form_view_id,
        #         'context': {'static': 'reject'}
        #     }         
        self.action_taken_on = datetime.now()
        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        # Delete the meeting
        self.mapped('meeting_id').unlink()
        # If a category that created several holidays, cancel all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_refuse()
        self._remove_resource_leave()
        self.activity_update()
        template = self.env.ref('kw_hr_leaves.kw_hr_leave_reject_mail')
        template.send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        return True

    @api.multi
    def action_draft(self):
        if any(holiday.state not in ['confirm', 'refuse', 'hold'] for holiday in self):
            raise UserError(
                ('Leave request state must be "Refused" or "To Approve" or hold in order to be reset to draft.'))
        self.write({
            'state': 'draft',
            'first_approver_id': False,
            'second_approver_id': False,
        })
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_draft()
            linked_requests.unlink()
        self.activity_update()
        return True

    @api.multi
    def cancel_leave(self):
        for rec in self:
            if not rec.cancel_reason:
                form_view_id = self.env.ref("kw_hr_leaves.view_kw_hr_leaves_cancel_comment_form").id
                return {
                    'name': 'Cancel Reason',
                    'type': 'ir.actions.act_window',
                    'res_model': 'hr.leave',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'res_id': self.ids[0],
                    'view_id': form_view_id,
                }
            self.write({
                'state': 'cancel',
                'first_approver_id': False,
                'second_approver_id': False,
            })
            linked_requests = self.mapped('linked_request_ids')
            if linked_requests:
                linked_requests.cancel_leave()
            self._remove_resource_leave()
            self.activity_update()
            self.env['kw_leave_approval_log'].create_approval_log(False, rec, False, False, rec.cancel_reason,
                                                                  self.env.user.employee_ids.id, STS_CANCEL)
            template = self.env.ref('kw_hr_leaves.kw_hr_leave_cancel_mail')
            template.send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            return True

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            val_type = holiday.holiday_status_id.validation_type
            if state == 'confirm':
                continue
            if state == 'draft':
                if holiday.employee_id != current_employee and not is_manager:
                    raise UserError(_('Only a Leave Manager can reset other people leaves.'))
                continue

            if not is_officer:
                raise UserError(_('Only a Leave Officer or Manager can approve or refuse leave requests.'))

            if is_officer:
                # use ir.rule based first access check: department, members, ... (see security.xml)
                holiday.check_access_rule('write')

            if state != 'cancel' and holiday.employee_id == current_employee and not is_manager:
                raise UserError(_('Only a Leave Manager can approve its own requests.'))

            manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
            if state != 'cancel' and holiday.second_approver_id != current_employee and (manager and manager != current_employee) and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (holiday.employee_id.name))

            # if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
            #     manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
            #     if (manager and manager != current_employee) and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            #         raise UserError(('You must be either %s\'s manager or Leave manager to approve this leave') % (holiday.employee_id.name))

            # if state == 'validate' and val_type == 'both':
            #     if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            #         raise UserError(('Only an Leave Manager can apply the second approval on leave requests.'))

    def activity_update(self):
        """
            odoo method
            method to update the activities
        """
        to_clean, to_do = self.env['hr.leave'], self.env['hr.leave']
        for holiday in self:
            if holiday.state == 'cancel':
                to_clean |= holiday
            if holiday.state == 'draft':
                to_clean |= holiday
            elif holiday.state == 'confirm':
                approver = holiday.sudo()._get_responsible_for_approval()
                holiday.with_context(mail_activity_quick_update=True).activity_schedule(
                    'hr_holidays.mail_act_leave_approval', user_id=approver.id or self.env.user.id)
                # #reporting authority as pending at
                holiday.write({'second_approver_id': approver.employee_ids[:1].id})

            elif holiday.state == 'validate1':
                holiday.activity_feedback(['hr_holidays.mail_act_leave_approval'])
                holiday.with_context(mail_activity_quick_update=True).activity_schedule(
                    'hr_holidays.mail_act_leave_second_approval',
                    user_id=holiday.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif holiday.state == 'validate':
                to_do |= holiday
            elif holiday.state == 'refuse':
                to_clean |= holiday

            elif holiday.state == 'forward':
                holiday.activity_feedback(['hr_holidays.mail_act_leave_approval'])
                if holiday.second_approver_id.user_id:
                    holiday.with_context(mail_activity_quick_update=True).activity_schedule('hr_holidays.mail_act_leave_approval', user_id=holiday.second_approver_id.user_id.id)

        if to_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
        if to_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])

    @api.onchange('apply_for')
    def _onchange_apply_for(self):
        emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.apply_for == "others":
            self.employee_id = False
            if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                return {'domain': {'employee_id': ([('parent_id', 'in', emp_ids.ids)])}}
            else:
                return {'domain': {'employee_id': ([('id', 'not in', emp_ids.ids)])}}
        else:
            self.employee_id = emp_ids.id
            return {'domain': {'employee_id': ([('id', 'in', emp_ids.ids)])}}

        # domain=[('id','not in',self.env.user.employee_ids.ids)]
        # if self.apply_for == 'others':
        #     if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
        #         print(self.employee_id)
        #         if self.employee_id:
        #             if self.env.user.employee_ids.id == self.employee_id.id:
        #                 domain += [('id','in',self.employee_id.child_ids.ids)]
        #             else:
        #                  domain += [('id','in',self.env.user.employee_ids.child_ids.ids)]
        #         else:
        #             domain += [('id','not in',[])]

        #     self.employee_id =False
        #     print(domain)
        #     return {'domain':{'employee_id':domain}} 
        # else:
        #     print(self.env.user.employee_ids.id)
        #     self.employee_id = self.env.user.employee_ids.id  
        #     print(self.employee_id) 

    @api.multi
    def _compute_number_of_days_warning(self):
        for rec in self:
            if rec.holiday_status_id:
                leave_config_wbranch = self.env['kw_leave_type_config'].search(
                    [('branch_id', '=', rec.env.user.branch_id.id), ('leave_type_id', '=', rec.holiday_status_id.id)])

                if leave_config_wbranch:
                    if leave_config_wbranch.monthly_allowed_leave > 0 and rec.number_of_days_display > leave_config_wbranch.monthly_allowed_leave:
                        rec.status = True
                        rec.message = f'Employee is not allowed to take more than {leave_config_wbranch.monthly_allowed_leave} days of {rec.holiday_status_id.name}.'
                    else:
                        rec.status = False
                else:
                    leave_config = self.env['kw_leave_type_config'].search(
                        [('branch_id', '=', False), ('leave_type_id', '=', rec.holiday_status_id.id)])
                    if leave_config and leave_config.monthly_allowed_leave > 0 and rec.number_of_days_display > leave_config.monthly_allowed_leave:
                        rec.status = True
                        rec.message = f'Employee is not allowed to take more than {leave_config.monthly_allowed_leave} days of {rec.holiday_status_id.name}.'
                    else:
                        rec.status = False

    @api.onchange('number_of_days_display')
    def _onchange_number_of_days_display(self):
        if self.number_of_days_display:
            self._compute_number_of_days_warning()

    @api.multi
    def name_get(self):
        res = []
        for leave in self:
            if self.env.context.get('short_name'):
                if leave.leave_type_request_unit == 'hour':
                    res.append((leave.id, ("%s : %.2f hour(s)") % (leave.name or leave.holiday_status_id.name, leave.number_of_hours_display)))
                else:
                    res.append((leave.id, ("%s : %.2f day(s)") % (leave.name or leave.holiday_status_id.name, leave.number_of_days)))
            else:
                if leave.holiday_type == 'company':
                    target = leave.mode_company_id.name
                elif leave.holiday_type == 'department':
                    target = leave.department_id.name
                elif leave.holiday_type == 'category':
                    target = leave.category_id.name
                else:
                    target = leave.employee_id.name
                if leave.leave_type_request_unit == 'hour':
                    res.append(
                        (leave.id,
                         ("%s on %s : %.2f hour(s)") %
                         (target, leave.holiday_status_id.name, leave.number_of_hours_display))
                    )
                else:
                    res.append(
                        (leave.id,
                         ("%s on %s : %.2f day(s) ( %s to %s)") %
                         (target, leave.holiday_status_id.name, leave.number_of_days, leave.request_date_from,
                          leave.request_date_to))
                    )
        return res

    @api.multi
    def action_forward(self, forward_reason, forward_to):

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1', 'hold', 'forward']:
                raise UserError('Leave request must be confirmed in order to forward it.')

            holiday.write({'first_approver_id': current_employee.id, 'second_approver_id': forward_to.id,
                           'authority_remark': forward_reason, 'state': 'forward', 'action_taken_on': datetime.now()})

            holiday.linked_request_ids.action_forward(forward_reason, forward_to)

            # holiday.action_taken_on = datetime.now()
            # print(forward_to)    
            holiday.activity_update()
            template = holiday.env.ref('kw_hr_leaves.kw_hr_leave_forward_mail')
            template.send_mail(holiday.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        return True

    @api.multi
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if not self.env.context.get('leave_fast_create') and values.get('state'):
            self._check_approval_update(values['state'])
        result = super(HrLeave, self).write(values)
        if not self.env.context.get('leave_fast_create'):
            self.add_follower(employee_id)
            if 'employee_id' in values:
                self._sync_employee_details()
        return result

    @api.multi
    def _compute_is_approver(self):
        # if self.second_approver_id.user_id == self.env.user.employee_ids.user_id:
        #     self.is_approver = True

        for rec in self:
            emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).ids

            rec.is_approver = True if rec.second_approver_id.id in emp_ids and rec.state in ['confirm', 'hold',
                                                                                             'forward'] else False

    @api.multi
    def _compute_from(self):
        for leave in self:
            if leave.request_unit_half:
                if leave.request_date_from_period == 'am':
                    leave.from_day_half = str(format_date(self.env, leave.request_date_from) if leave.request_date_from else '') + " First Half"
                if leave.request_date_from_period == 'pm':
                    leave.from_day_half = str(format_date(self.env, leave.request_date_from) if leave.request_date_from else '') + " Second Half"
            else:
                leave.from_day_half = format_date(self.env, leave.request_date_from) if leave.request_date_from else ''

    @api.multi
    def _compute_to(self):
        for leave in self:
            if leave.request_unit_half_to_period:
                if leave.request_date_to_period == 'am':
                    leave.to_day_half = str(format_date(self.env, leave.request_date_to) if leave.request_date_to else '') + " First Half"
                if leave.request_date_to_period == 'pm':
                    leave.to_day_half = str(format_date(self.env, leave.request_date_to) if leave.request_date_to else '') + " Second Half"
            else:
                leave.to_day_half = format_date(self.env, leave.request_date_to) if leave.request_date_to else ''

    # #cancel approved leave
    @api.multi
    def cancel_approved_leave(self):
        self.ensure_one()

        form_view_id = self.env.ref("kw_hr_leaves.kw_cancel_leave_form").id
        return {
            'name': 'Cancel Leave',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_cancel_leave',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            # 'res_id':self.ids[0],
            'view_id': form_view_id,
            'context': {'default_approved_leave_id': self.id, "hide_leave": True}
        }

    ###################################
    #   Leave Approvals/ Take Action
    #         
    ##################################
    @api.multi
    def leave_take_action(self):
        self.ensure_one()
        form_view_id = self.env.ref("kw_hr_leaves.view_kw_apply_leave_take_action_form").id
        # print(self._context)
        return {
            "name": 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'res_id': self.id,
            'view_id': form_view_id,
            'context': {'default_action_type': self._context.get('action_type', False),
                        "default_forward_request": self._context.get('forward_request', False)}
        }

    @api.multi
    def leave_request_forward_action(self):
        self.ensure_one()
        # print(self.action_remark)
        self.action_forward(self.action_remark, self.forward_to)
        # #insert into log
        self.env['kw_leave_approval_log'].create_approval_log(False, self, False, self.forward_to, self.action_remark,
                                                              self.env.user.employee_ids.id, STS_FORWARD)

        # reset the fields
        self.write({'forward_request': False, 'action_remark': False, 'forward_to': False})

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def leave_request_hold_action(self):
        self.ensure_one()

        self.write({'authority_remark': self.action_remark})
        self.hold_leave()
        # #insert into log
        self.env['kw_leave_approval_log'].create_approval_log(False, self, False, self.second_approver_id,
                                                              self.action_remark, self.env.user.employee_ids.id,
                                                              STS_HOLD)
        self.write({'action_remark': False})

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def leave_request_approve_action(self):
        self.ensure_one()

        self.write({'authority_remark': self.action_remark})
        self.action_approve()
        # #insert into log
        self.env['kw_leave_approval_log'].create_approval_log(False, self, False, False, self.action_remark,
                                                              self.env.user.employee_ids.id, STS_APPROVE)

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def leave_request_reject_action(self):
        self.ensure_one()

        self.write({'authority_remark': self.action_remark})
        self.action_refuse()
        # #insert into log
        self.env['kw_leave_approval_log'].create_approval_log(False, self, False, False, self.action_remark,
                                                              self.env.user.employee_ids.id, STS_REJECT)

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def generate_days_with_from_and_to_date(self, from_date, to_date):
        # from_date = datetime(2021, 1, 1).date()
        # to_date = datetime(2021, 1, 19).date()
        leave_records = self.env['hr.leave'].sudo().search([
            '&', ('state', '=', 'validate'),
            '|',
            '|',
            '&', ('date_from', '<=', from_date), ('date_to', '>=', from_date),
            '|',
            '&', ('date_from', '<=', to_date), ('date_to', '>=', to_date),
            '&', ('date_from', '<=', from_date), ('date_to', '>=', to_date),
            '|',
            '&', ('date_from', '>=', from_date), ('date_from', '<=', to_date),
            '&', ('date_to', '>=', from_date), ('date_to', '<=', to_date)
        ])
        return leave_records

    def lv_get_current_financial_dates(self):
        current_date = date.today()
        current_year = date.today().year

        if current_date < date(current_year, 4, 1):
            start_date = date(current_year - 1, 4, 1)
            end_date = date(current_year, 3, 31)
        else:
            start_date = date(current_year, 4, 1)
            end_date = date(current_year + 1, 3, 31)

        return start_date, end_date

    def get_employee_leave_detail(self, employee_id, date_from, date_to):
        leave_days = []
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            # print(employee, date_from, date_to, type(date_from))
            if employee:
                leave_records = self.env['hr.leave'].sudo().search([
                    '&', ('state', '=', 'validate'),
                    '&', ('employee_id', '=', employee.id),
                    '|',
                    '|',
                    '&', ('date_from', '<=', date_from), ('date_to', '>=', date_from),
                    '|',
                    '&', ('date_from', '<=', date_to), ('date_to', '>=', date_to),
                    '&', ('date_from', '<=', date_from), ('date_to', '>=', date_to),
                    '|',
                    '&', ('date_from', '>=', date_from), ('date_from', '<=', date_to),
                    '&', ('date_to', '>=', date_from), ('date_to', '<=', date_to)
                ])

                if leave_records:
                    for leave in leave_records:
                        # print("dt >> ", leave.date_from.date(), leave.date_to.date())
                        from_date = leave.date_from.date()
                        while from_date <= leave.date_to.date():
                            leave_days.append(from_date)
                            from_date += timedelta(days=1)

        return leave_days

    def auto_approve_leave_scheduler(self):
        query = "delete from hr_leave_allocation where id = 16798"
        self._cr.execute(query)
        # start_date = date(datetime.today().year,3,26)
        # end_date = date(datetime.today().year,3,31)
        # leave_ids = self.env['hr.leave'].sudo().search([('date_from','>=',start_date),('date_to','<=',end_date),('state','not in',['validate','refuse','cancel'])])
        # print(leave_ids)
        # for leave in leave_ids:
        #     leave.write({'authority_remark': 'Auto Approved'})
        #     leave.action_approve()
        #     # #insert into log
        #     self.env['kw_leave_approval_log'].create_approval_log(False, leave, False, False, 'Auto Approved',
        #                                                         self.env.user.employee_ids.id, STS_APPROVE)
