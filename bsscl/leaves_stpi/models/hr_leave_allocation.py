from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    _description = 'HR Leave Allocation'


    def _default_holiday_status_id(self):
        res = super(HrLeaveAllocation, self)._default_holiday_status_id()

        return res

    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By All Department'),
        ('branch','By Branch'),
        ('department', 'By Department')],
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
        ('validate', 'Done')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")

    gende = fields.Selection(related='holiday_status_id.gende')
    is_lapsed = fields.Boolean(string='Is Lapsed')
    branch_id = fields.Many2one("res.branch",string="Branch",related='employee_id.branch_id',store=True)
    holiday_status_id = fields.Many2one(
        "hr.leave.type", string="Leave Type",compute='_compute_from_employee_id',  required=True, domain=[], default=_default_holiday_status_id,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    _sql_constraints = [
        ('duration_check', 'CHECK(1=1)',
         'Duration must not 0.'),
    ]

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        default_holiday_status_id = self._default_holiday_status_id()
        for holiday in self:
            holiday.manager_id = holiday.employee_id and holiday.employee_id.parent_id
            if not holiday.holiday_status_id and not holiday._origin.holiday_status_id:
                holiday.holiday_status_id = default_holiday_status_id

    @api.model
    def create(self, values):
        if 'number_of_days_display' in values and values.get('number_of_days_display') <= 0:
            raise UserError(_("Duration must be greater than 0."))
        return super(HrLeaveAllocation, self).create(values)

    def write(self, values):
        if 'number_of_days_display' in values and values.get('number_of_days_display') <= 0:
            raise UserError(_("Duration must be greater than 0."))
        return super(HrLeaveAllocation, self).write(values)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if self._context.get('branch_check'):
            args += [('branch_id', 'in', self.env.user.branch_ids.ids)]

        return super(HrLeaveAllocation, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                      access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        if self._context.get('branch_check'):
            domain += [('branch_id', 'in', self.env.user.branch_ids.ids)]

        return super(HrLeaveAllocation, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                         orderby=orderby, lazy=lazy)

    def action_approve(self):
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        print('=================user_id=================', self.env.uid)
        print('==================================', current_employee.name)

        self.filtered(lambda hol: hol.validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})
        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        self.activity_update()
        return True

    @api.onchange('holiday_type', 'holiday_status_id')
    def _onchange_holiday_type_status(self):
        for leave in self:
            if leave.holiday_status_id and leave.holiday_type == 'employee':
                leave.employee_id = False
                employee_type = leave.holiday_status_id.allow_service_leave.mapped('tech_name')
                print('employee_type=====================', employee_type)
                if leave.holiday_status_id.gende == 'male':

                    return {'domain': {'employee_id': [('gende', '=', 'male'), ('employee_type', 'in', employee_type),
                                                       ('current_office_id', 'in', self.env.user.branch_ids.ids)]}}
                elif leave.holiday_status_id.gende == 'female':
                    return {'domain': {'employee_id': [('gende', '=', 'female'), ('employee_type', 'in', employee_type),
                                                       ('current_office_id', 'in', self.env.user.branch_ids.ids)]}}
                else:
                    return {'domain': {'employee_id': [('employee_type', 'in', employee_type),
                                                       ('current_office_id', 'in', self.env.user.branch_ids.ids)]}}

    # @api.constrains('number_of_days')
    # def _check_leave_per_year(self):
    #     for leave in self:
    #         if leave.holiday_status_id and leave.holiday_status_id.leave_per_year > 0 and leave.number_of_days > leave.holiday_status_id.leave_per_year:
    #             raise ValidationError(f"Maximum exceed as leave per year is {leave.holiday_status_id.leave_per_year}.")

    @api.onchange('holiday_type')
    def _onchange_type(self):
        if self.holiday_type == 'employee':
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

    def name_get(self):
        result = []
        for record in self:
            record_name = "Allocation of Leave"
            result.append((record.id, record_name))
        return result

    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'first_approver_id': current_employee.id})
            else:
                holiday.write({'state': 'refuse', 'second_approver_id': current_employee.id})
            holiday.linked_request_ids.action_refuse()
        self.activity_update()
        return True

    # start : merged from hr_employee_stpi
    @api.onchange('holiday_status_id')
    def hr_take_leave(self):
        for rec in self:
            check_casual = self.env['hr.leave.type'].search([('is_casual_lt', '=', True)], limit=1)
            if rec.holiday_status_id == check_casual.id:
                if rec.number_of_days > 5.00:
                    raise ValidationError(_('You are not able to take more than 5 days casual leave'))



    def hr_leave_casual_cron(self):
        first_day = datetime.now().date().replace(month=1, day=1)
        last_day = first_day + relativedelta(months=12) - relativedelta(days=1)
        name = 'Casual Leave ' + str(first_day.year)
        c_leave_type_name = self.env['leave.type.master'].create({
            'name': name,
            'code' : name,
            })
        c_leave_type = self.env['hr.leave.type'].create({
            'name': c_leave_type_name.id,
            'color_name': 'lightgreen',
            'request_unit': 'day',
            'time_type': 'leave',
            'allocation_type': 'fixed',
            'validity_start': first_day,
            'validity_stop': last_day,
            'is_casual_lt': True,
        })
        n_name = str(self.env.user.company_id.name) + ' - ' + str(name)
        allocate_leave = self.env['hr.leave.allocation'].create({
                    'name': n_name,
                    'holiday_status_id': c_leave_type.id,
                    'holiday_type': 'company',
                    'mode_company_id': self.env.user.company_id.id,
                    'number_of_days': 8.00,
                }
            )
        allocate_leave.sudo().action_approve()



    def hr_leave_half_pay_cron(self):
        first_day = datetime.now().date().replace(day=1)
        last_day = first_day + relativedelta(months=7) - relativedelta(days=1)
        name = 'Half Pay Leave ' + str(first_day.year)
        c_leave_type_name = self.env['leave.type.master'].create({
            'name': name,
            'code' : name,
            })
        c_leave_type = self.env['hr.leave.type'].create({
            'name': c_leave_type_name.id,
            'color_name': 'lightgreen',
            'request_unit': 'day',
            'time_type': 'leave',
            'allocation_type': 'fixed',
            'validity_start': first_day,
            'validity_stop': last_day,
            'is_half_pay': True,
        })
        n_name = str(self.env.user.company_id.name) + ' - ' + str(name)
        allocate_leave = self.env['hr.leave.allocation'].create({
                    'name': n_name,
                    'holiday_status_id': c_leave_type.id,
                    'holiday_type': 'company',
                    'mode_company_id': self.env.user.company_id.id,
                    'number_of_days': 10.00,
                }
            )
        allocate_leave.sudo().action_approve()

    def hr_leave_earned_cron(self):
        name = 'Earned Leave'
        c_leave_type_name = self.env['leave.type.master'].create({
            'name': name,
            'code' : name,
            })
        c_leave_type = self.env['hr.leave.type'].create({
            'name': c_leave_type_name,
            'color_name': 'lightgreen',
            'request_unit': 'day',
            'time_type': 'leave',
            'allocation_type': 'fixed',
            'hr_consider_sandwich_rule': True,
        })
        n_name = str(self.env.user.company_id.name) + ' - ' + str(name)
        allocate_leave = self.env['hr.leave.allocation'].create({
                    'name': n_name,
                    'holiday_status_id': c_leave_type.id,
                    'holiday_type': 'company',
                    'mode_company_id': self.env.user.company_id.id,
                    'number_of_days': 15.00,
                }
            )
        allocate_leave.sudo().action_approve()
    # end : merged from hr_employee_stpi