from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    _description = 'HR Leave Allocation'
    

    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By All Department'),
        ('branch','By Branch'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag')],
        string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Allow to create requests in batchs:\n- By Employee: for a specific employee"
             "\n- By Company: all employees of the specified company"
             "\n- By Department: all employees of the specified department"
             "\n- By Employee Tag: all employees of the specific employee group category")
    by_branch_id = fields.Many2one("res.branch",string="By Branch")
    duration_display = fields.Char('Allocated(Days)', compute='_compute_duration_display',
        help="Field allowing to see the allocation duration in days or hours depending on the type_request_unit")
    
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Reject'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")

    gende = fields.Selection(related='holiday_status_id.gende')
    is_lapsed = fields.Boolean(string='Is Lapsed')
    branch_id = fields.Many2one("res.branch",string="Branch",related='employee_id.branch_id',store=True)

    _sql_constraints = [
        ('duration_check', 'CHECK(1=1)',
         'Duration must not 0.'),
    ]

    @api.model
    def create(self, values):
        if 'number_of_days_display' in values and values.get('number_of_days_display') <= 0:
            raise UserError(_("Duration must be greater than 0."))
        return super(HrLeaveAllocation, self).create(values)

    @api.multi
    def write(self, values):
        if 'number_of_days_display' in values and values.get('number_of_days_display') <= 0:
            raise UserError(_("Duration must be greater than 0."))
        return super(HrLeaveAllocation, self).write(values)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if self._context.get('branch_check'):
            args += [('branch_id','in',self.env.user.branch_ids.ids)]
        
        return super(HrLeaveAllocation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        if self._context.get('branch_check'):
            domain += [('branch_id','in',self.env.user.branch_ids.ids)]

        return super(HrLeaveAllocation, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

    @api.multi
    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        print('=================user_id=================', self.env.uid)
        print('==================================', current_employee.name)

        self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})
        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        self.activity_update()
        self.env.user.notify_success("Leave Allocation Approved.")
        return True

    @api.onchange('holiday_type','holiday_status_id')
    def _onchange_holiday_type_status(self):
        for leave in self:
            if leave.holiday_status_id and leave.holiday_type == 'employee':
                leave.employee_id = False
                employee_type = leave.holiday_status_id.allow_service_leave.mapped('tech_name')
                if leave.holiday_status_id.gende == 'male':
                    return {'domain': {'employee_id': [('gende', '=', 'male'),('employee_type','in',employee_type),('branch_id','in',self.env.user.branch_ids.ids)]}}
                elif leave.holiday_status_id.gende == 'female':
                    return {'domain': {'employee_id': [('gende', '=', 'female'),('employee_type','in',employee_type),('branch_id','in',self.env.user.branch_ids.ids)]}}
                else:
                    return {'domain': {'employee_id': [('employee_type','in',employee_type),('branch_id','in',self.env.user.branch_ids.ids)]}}
    
    @api.multi
    @api.constrains('number_of_days')
    def _check_leave_per_year(self):
        for leave in self:
            if leave.holiday_status_id.leave_type.code == 'Casual Leave':
                if leave.employee_id.differently_abled == 'yes':
                    if leave.holiday_status_id and leave.number_of_days > 12:
                        raise ValidationError("Maximum exceed as leave per year is 12.")
                else:
                    if leave.holiday_status_id and leave.holiday_status_id.leave_per_year > 0 and leave.number_of_days > leave.holiday_status_id.leave_per_year:
                        raise ValidationError(f"Maximum exceed as leave per year is {leave.holiday_status_id.leave_per_year}.")
            else:
                if leave.holiday_status_id and leave.holiday_status_id.leave_per_year > 0 and leave.number_of_days > leave.holiday_status_id.leave_per_year:
                    raise ValidationError(f"Maximum exceed as leave per year is {leave.holiday_status_id.leave_per_year}.")

    @api.onchange('holiday_type')
    def _onchange_type(self):
        if self.holiday_type == 'employee':
            # if not self.employee_id:
            #     self.employee_id = self.env.user.employee_ids[:1].id
            self.employee_id = False
            self.mode_company_id = False
            self.category_id = False
        elif self.holiday_type == 'company':
            self.employee_id = False
            if not self.mode_company_id:
                self.mode_company_id = self.env.user.company_id.id
            self.category_id = False
        elif self.holiday_type == 'department':
            self.employee_id = False
            self.mode_company_id = False
            self.category_id = False
            if not self.department_id:
                self.department_id = self.env.user.employee_ids[:1].department_id.id
        elif self.holiday_type == 'category':
            self.employee_id = False
            self.mode_company_id = False
            self.department_id = False

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = "Allocation of Leave"
            result.append((record.id, record_name))
        return result
    
    @api.multi
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'first_approver_id': current_employee.id})
            else:
                holiday.write({'state': 'refuse', 'second_approver_id': current_employee.id})
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self.activity_update()
        self.env.user.notify_info("Leave Allocation Rejected.")
        return True