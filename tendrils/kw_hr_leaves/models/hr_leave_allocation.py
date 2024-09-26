from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
# import fiscalyear
from dateutil import relativedelta
from odoo.tools.translate import _

import re

from odoo.addons.kw_hr_leaves.models.kw_leave_type_config import CONFIG_GTYPE_MALE, CONFIG_GTYPE_FEMALE, \
    CONFIG_GTYPE_BOTH, EMP_GENDER_TYPE_MALE, EMP_GENDER_TYPE_FEMALE

# from odoo.addons.kw_hr_leaves.models import hr_leave

# start_date, end_date = hr_leave.lv_get_current_financial_dates()

LAPSE_TYPE_YEARLY, LAPSE_TYPE_CF, LAPSE_TYPE_COMP_OFF, LAPSE_BY_TIMESHEET = 1, 2, 3, 4


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    def _ddefault_holiday_status_id(self):
        # if self.user_has_groups('hr_holidays.group_hr_holidays_user'):
        #     domain = [('valid', '=', True)]
        # else:
        #     domain = [('valid', '=', True), ('allocation_type', 'in', ('fixed_allocation'))]
        return False

    # holiday_type       = fields.Selection(selection_add=[('grade', 'By Grade')])
    # grade_id           = fields.Many2many('kwemp_grade', string="Grade")
    expire_date = fields.Date('Expire date')
    holiday_status_id = fields.Many2one(
        "hr.leave.type", string="Leave Type", required=True, readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        domain=[('valid', '=', True)], default=_ddefault_holiday_status_id)
    cancel_reason = fields.Text('Reason of Cancellation', size=500)
    notes = fields.Text('Reasons', required=True, readonly=True,
                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    validity_start_date = fields.Date('Validity Start date')
    validity_end_date = fields.Date('Validity End date')

    leave_cycle_id = fields.Many2one('kw_leave_cycle_master', string="Leave Cycle")
    cycle_period = fields.Integer(string="Cycle Period")

    cmp_leave_taken = fields.Float(string='Leave Taken', default=0,
                                   help='keep track of leave taken, used only for comp off allocation')

    """Start: Fields used for approval process flow"""
    second_approver_id = fields.Many2one(string="Pending At")
    forward_reason = fields.Text(string='Forward Reason', )

    authority_remark = fields.Text(string='Authority Remark', )
    first_approver_id = fields.Many2one(string="Action Taken By")
    action_taken_on = fields.Datetime(string="Action Taken On", )
    state = fields.Selection(selection_add=[('forward', 'Forwarded')])
    approval_log_ids = fields.One2many(
        string='Approval Logs',
        comodel_name='kw_leave_approval_log',
        inverse_name='allocation_id',
    )

    project_name = fields.Char('Project Name/Activity')
    department = fields.Char(string="Department", related="employee_id.department_id.name")
    division = fields.Char(string="Division", related="employee_id.division.name")
    section = fields.Char(string="Section", related="employee_id.section.name")
    designation = fields.Char(string="Designation", related="employee_id.job_id.name")
    is_carried_forward = fields.Boolean("Is Carried Forward", default=False)

    lapse_alc_type = fields.Integer(
        string="Lapse Allocation")  # 1 - Yearly Lapse, 2- CF Lapse, 3- Comp Off Lapse, 4 - Timesheet Lapse
    is_lapsed = fields.Boolean("Is Lapsed", default=False)

    current_financial_year = fields.Boolean("Current Financial Year", compute='_compute_current_financial_year',
                                            search="_lv_search_current_financial_year")
    previous_financial_year = fields.Boolean("Previous Financial Year", compute='_compute_previous_financial_year',
                                             search="_lv_search_previous_financial_year")

    """End: Fields used for approval process flow"""

    _sql_constraints = [('duration_check', 'CHECK(1=1)', 'Duration must not 0.'), ]

    action_taken_date = fields.Date(string="Action Taken On", compute='_compute_action_taken_date')
    applied_on = fields.Date(string='Applied On', compute='_compute_applied_on')

    @api.multi
    def _compute_applied_on(self):
        for allocation in self:
            allocation.applied_on = allocation.create_date.date()

    @api.multi
    def _compute_action_taken_date(self):
        for allocation in self:
            allocation.action_taken_date = allocation.action_taken_on.date() if allocation.action_taken_on else False

    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass

    @api.multi
    def _compute_previous_financial_year(self):
        for record in self:
            pass

    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        start_date, end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        return [('cycle_period', '=', start_date.year)]

    @api.multi
    def _lv_search_previous_financial_year(self, operator, value):
        start_date, end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        return [('cycle_period', '=', start_date.year - 1)]

    @api.constrains('project_name')
    def validate_project_name(self):
        for record in self:
            if not re.match("^[0-9a-zA-Z_. ]+$", str(record.project_name)) != None:
                raise ValidationError("Project Name/Activity should not contain special characters.")

    @api.constrains('number_of_days')
    def validate_number_of_days(self):
        for record in self:
            if record.number_of_days <= 0:
                raise ValidationError("The number of days must be greater than 0.")

    """method to allocate leave as per the leave cycle and leave type configuration
       Created By : T Ketaki Debadarshini
       Created On : 01-Sep-2020
    """

    def leave_allocation_as_per_cycle(self):
        curr_date = datetime.today().date()
        curr_year = curr_date.year
        # kw_leave_cycle_master
        leave_cycle_master = self.env['kw_leave_cycle_master']
        all_leave_cycle_records = leave_cycle_master.with_context(active_test=False).search([])
        # print(all_leave_cycle_records)
        all_leave_cycles = all_leave_cycle_records.filtered(lambda rec: rec.cycle_id)
        all_config_cycles = all_leave_cycle_records - all_leave_cycles
        # print(all_leave_cycles)
        # print(all_config_cycles)
        for config_cycle in all_config_cycles:
            active_cycle = all_leave_cycles.filtered(
                lambda rec: rec.active == True and rec.cycle_id.id == config_cycle.id)
            # print(active_cycle,active_cycle.from_date,active_cycle.to_date)
            if active_cycle and active_cycle.from_date <= curr_date <= active_cycle.to_date:
                pass
            else:
                if active_cycle:
                    active_cycle.write({'active': False})
                # print('ooooooooooooo')"2020-04-01" "2021-01-22"
                new_active_cycle = all_leave_cycles.filtered(lambda
                                                                 rec: rec.branch_id.id == config_cycle.branch_id.id and rec.cycle_id.id == config_cycle.id and rec.cycle_period == curr_year)

                if not new_active_cycle:
                    leave_cycle_master.create(
                        {'branch_id': config_cycle.branch_id.id if config_cycle.branch_id else False,
                         'from_date': curr_date.replace(day=int(config_cycle.from_day),
                                                        month=int(config_cycle.from_month)),
                         'to_date': curr_date.replace(day=int(config_cycle.to_day), month=int(config_cycle.to_month),
                                                      year=curr_year + 1 if int(config_cycle.to_month) <= int(
                                                          config_cycle.from_month) else curr_year),
                         'cycle_period': curr_year, 'cycle_id': config_cycle.id, 'active': True})

                elif new_active_cycle and new_active_cycle.from_date <= curr_date <= new_active_cycle.to_date:
                    new_active_cycle.write({'active': True})
        # exit()

        all_active_cycle = self.env['kw_leave_cycle_master'].search([('cycle_id', '!=', False), ('active', '=', True)])
        # print(all_active_cycle)

        entitle_active_cycle = all_active_cycle.filtered(lambda rec: rec.from_date <= curr_date <= rec.to_date)
        # only if the allocation type is Fixed, and Fixed by HR + Allocation request, 
        all_leave_type_records = self.env['hr.leave.type'].search(
            [('allocation_type', 'in', ['fixed', 'fixed_allocation']), ('is_comp_off', '=', False)])
        # print(entitle_active_cycle)

        # for each branch leave cycle
        for leave_cycle in entitle_active_cycle:
            # credit_dates,lapse_date         = leave_config_rec.get_leave_config_wise_credit_lapse_days(emp_active_cycle)
            #  and curr_date == credit_dates
            # #if the setting is set for other than no entitlement and leave entitlement date matches
            if leave_cycle.from_date <= curr_date <= leave_cycle.to_date:
                for leave_type in all_leave_type_records:
                    # if employment types configured and  there are leave configuration exists
                    if leave_type.employement_type_ids and leave_type.leave_type_config_ids:
                        # print('----------------------------')
                        leave_type.leave_type_config_ids.get_leave_type_config_wise_employees(leave_cycle)

        return True

    @api.multi
    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state not in ['confirm', 'forward'] for holiday in self):
            raise UserError(_('Leave request must be confirmed ("To Approve") or forwarded in order to approve it.'))

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        self.filtered(lambda hol: hol.validation_type == 'both').write(
            {'state': 'validate1',
             'first_approver_id': current_employee.id})
        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        self.activity_update()

        for holidays in self:
            try:
                if holidays.employee_id:
                    active_cycle = self.env['kw_leave_cycle_master'].search([('branch_id', '=',
                                                                              holidays.employee_id.job_branch_id.id if holidays.employee_id.job_branch_id else False),
                                                                             ('cycle_id', '!=', False),
                                                                             ('active', '=', True)], limit=1)

                    if not holidays.holiday_status_id.is_comp_off:
                        if active_cycle:
                            holidays.write({'validity_start_date': active_cycle.from_date,
                                            'validity_end_date': active_cycle.to_date,
                                            'leave_cycle_id': active_cycle.id,
                                            'cycle_period': active_cycle.cycle_period})
                    else:
                        if not holidays.leave_cycle_id and not holidays.cycle_period:
                            if holidays.attendance_id:
                                attendance_date = holidays.attendance_id.sudo().attendance_recorded_date
                                validity_days = holidays.holiday_status_id.validity_days if holidays.holiday_status_id.validity_days > 0 else 180
                                validity_end_date = attendance_date + timedelta(days=validity_days)
                                holidays.write(
                                    {'validity_start_date': attendance_date,
                                     'validity_end_date': validity_end_date,
                                     'leave_cycle_id': active_cycle.id,
                                     'cycle_period': active_cycle.cycle_period})
                            else:
                                if active_cycle:
                                    holidays.write({'validity_start_date': active_cycle.from_date,
                                                    'validity_end_date': active_cycle.to_date,
                                                    'leave_cycle_id': active_cycle.id,
                                                    'cycle_period': active_cycle.cycle_period})
            except Exception as e:
                # print("Allocation Approve Error ", str(e))
                continue

        return True

    @api.multi
    def action_validate(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1', 'forward']:
                raise UserError(_('Leave request must be confirmed or forwarded in order to approve it.'))

            holiday.write({'state': 'validate'})
            if holiday.validation_type == 'both':
                holiday.write({'second_approver_id': current_employee.id})
            else:
                holiday.write({'first_approver_id': current_employee.id})

            holiday._action_validate_create_childs()
        self.activity_update()
        return True

    """Method to open the take action pop-up action
        Created By : T Ketaki Debadarshini
        Created On : 14-Sep-2020
    """

    @api.multi
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1', 'forward']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'first_approver_id': current_employee.id})
            else:
                holiday.write({'state': 'refuse', 'second_approver_id': current_employee.id})
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self.activity_update()
        return True

    @api.multi
    def action_leave_allocation_take_action(self):
        """action to open the leave allocation pop up with the default values 
            
        """
        # self.ensure_one()

        view_id = self.env.ref('kw_hr_leaves.view_leave_allocation_approval_form').id

        return {
            'name': 'Allocation Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave.allocation',
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': self.id,
            'flags': {'action_buttons': False, 'mode': 'edit', 'toolbar': False, },
            'context': {'create': False}
        }

    @api.multi
    def action_forward(self, forward_reason, forward_to):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1', 'forward']:
                raise UserError('Leave request must be confirmed in order to forward it.')

            # print(forward_to)
            holiday.write({'first_approver_id': current_employee.id,
                           'second_approver_id': forward_to.id,
                           'authority_remark': forward_reason,
                           'state': 'forward'})
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_forward(forward_reason, forward_to)
        self.activity_update()

        return True

    @api.multi
    def action_cancel(self, reason):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm']:
                raise UserError('Leave request must be confirmed in order to cancel it.')

            holiday.write({'first_approver_id': current_employee.id, 'authority_remark': reason})
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_cancel(reason)
        self.activity_update()

        return True

    def _get_responsible_employee_for_approval(self):
        if self.state == 'confirm':
            if self.employee_id.parent_id.user_id:
                return (self.employee_id.parent_id, self.employee_id.parent_id.user_id)
            elif self.employee_id.parent_id.parent_id and self.employee_id.parent_id.parent_id.user_id:
                return (self.employee_id.parent_id.parent_id, self.employee_id.parent_id.parent_id.user_id)
        # elif self.department_id.manager_id.user_id:
        #     return self.department_id.manager_id.user_id
        return (False, False)

    ############################
    # Overriding the existing methods of leave allocation class
    ###########################

    def activity_update(self):
        to_clean, to_do = self.env['hr.leave.allocation'], self.env['hr.leave.allocation']
        for allocation in self:
            if allocation.state == 'draft':
                to_clean |= allocation
            elif allocation.state == 'confirm':
                resp_emp, resp_user = allocation.sudo()._get_responsible_employee_for_approval()
                if resp_user:
                    allocation.activity_schedule('hr_holidays.mail_act_leave_allocation_approval', user_id=resp_user.id)
                if resp_emp:
                    allocation.write({'second_approver_id': resp_emp.id})

            elif allocation.state == 'validate1':
                allocation.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval'])
                allocation.activity_schedule(
                    'hr_holidays.mail_act_leave_allocation_second_approval',
                    user_id=allocation.sudo()._get_responsible_for_approval().id)
            elif allocation.state == 'validate':
                to_do |= allocation
            elif allocation.state == 'refuse':
                to_clean |= allocation
            elif allocation.state == 'cancel':
                to_clean |= allocation
            elif allocation.state == 'forward':
                # to_clean |= allocation
                allocation.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval'])
                if allocation.second_approver_id.user_id:
                    allocation.activity_schedule('hr_holidays.mail_act_leave_allocation_approval',
                                                 user_id=allocation.second_approver_id.user_id.id)

        if to_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_allocation_approval',
                                      'hr_holidays.mail_act_leave_allocation_second_approval'])
        if to_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval',
                                     'hr_holidays.mail_act_leave_allocation_second_approval'])

    @api.multi
    def cancel_allocation(self):

        if any(holiday.state not in ['confirm'] for holiday in self):
            raise UserError(_('Allocation request state must be "To Approve" in order to cancel.'))
        if not self.cancel_reason:
            form_view_id = self.env.ref("kw_hr_leaves.view_kw_hr_allocation_cancel_comment_form").id
            return {
                'name': 'Cancel Allocation',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.leave.allocation',
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
            linked_requests.cancel_allocation()
            linked_requests.unlink()
        self.activity_update()
        return True

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            val_type = holiday.holiday_status_id.sudo().validation_type
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

            if not holiday.holiday_status_id.is_comp_off:

                if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
                    manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
                    if (manager and manager != current_employee) and not self.env.user.has_group(
                            'hr_holidays.group_hr_holidays_manager'):
                        raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (
                            holiday.employee_id.name))

                if state == 'validate' and val_type == 'both':
                    if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                        raise UserError(_('Only an Leave Manager can apply the second approval on leave requests.'))

            elif holiday.second_approver_id != current_employee:
                raise UserError(_('You must have the access to modify this leave.'))

    # # method to lapse the yearly allocated leaves as per the leave cycle and leave type configuration
    #  Created By : T Ketaki Debadarshini
    #  Created On : 09-Feb-2020

    def leave_allocation_lapse_as_per_cycle(self):

        curr_date = datetime.today().date()
        # curr_year             = curr_date.year
        # kw_leave_cycle_master
        # leave_cycle_master           = self.env['kw_leave_cycle_master']
        lapse_leave_cycle_records = self.env['kw_leave_cycle_master'].search(
            [('cycle_period', '>', 0), ('to_date', '<', curr_date)])  #
        # print('-----------------------')
        # print('lapse records--------->',lapse_leave_cycle_records.ids)
        if lapse_leave_cycle_records:
            temp_str = str(tuple(lapse_leave_cycle_records.ids))  # cycle_ids
            # cycle_ids= '('+','.join(str(lapse_leave_cycle_records.ids))  +')'
            # print('************************************',cycle_ids)
            # temp_str = '(2,)'

            if temp_str[-2] == ',':
                len_cycle_ids = len(temp_str)
                final_temp_str = temp_str[:len_cycle_ids - 2]
                cycle_ids = final_temp_str + ')'
            else:
                cycle_ids = temp_str

            self.env.cr.execute(f""" SELECT leave_allocation.employee_id,cycle.cycle_period,leave_allocation.
            leave_cycle_id,leave_allocation.holiday_status_id,
sum(leave_allocation.number_of_days) AS tot_no_of_days,
sum(case when leave_allocation.type ='allocation' then coalesce(leave_allocation.number_of_days,0) else 0 end ) AS entitle,
sum(case when leave_allocation.type ='request' then coalesce(leave_allocation.number_of_days,0) else 0 end) AS taken,
sum(case when leave_allocation.type ='request' then coalesce((leave_allocation.number_of_days * -1),0) 
when leave_allocation.type ='allocation' then coalesce(leave_allocation.number_of_days,0) else 0 end) AS balance 
FROM (select
                    allocation.employee_id as employee_id,
                    allocation.name AS name,
                    allocation.number_of_days AS number_of_days,                    
                    allocation.holiday_status_id AS holiday_status_id,                    
                    allocation.state as state,
                    allocation.holiday_type,
                    null AS date_from,
                    null AS date_to,
                    leave_cycle_id AS leave_cycle_id,
                    null AS leave_id,                    
                    'allocation' AS type
                from hr_leave_allocation AS allocation where state ='validate' AND coalesce(lapse_alc_type,0) != 1
                union all select
                    request.employee_id AS employee_id,
                    request.name AS name,
                    request.number_of_days AS number_of_days,                    
                    request.holiday_status_id AS holiday_status_id,
                    request.state AS state,
                    request.holiday_type,
                    request.request_date_from AS date_from,
                    request.request_date_to AS date_to,
                    request.leave_cycle_id AS leave_cycle_id,
                    request.id AS leave_id,                    
                    'request' AS type
                FROM hr_leave AS request 
                where state ='validate') leave_allocation 
                inner join kw_leave_cycle_master cycle ON cycle.id = leave_allocation.leave_cycle_id 
                inner join hr_leave_type leave_type ON leave_type.id = leave_allocation.holiday_status_id 
                AND (leave_type.is_comp_off is null OR leave_type.is_comp_off= False) 
                AND leave_type.allocation_type in ('fixed','fixed_allocation') 
                AND (leave_type.carry_forward is null OR leave_type.carry_forward = False 
                or leave_type.carry_forward is True OR leave_type.carry_forward = True)    
                where cycle.id in %s

                group by cycle.cycle_period,leave_allocation.leave_cycle_id,leave_allocation.employee_id,
                leave_allocation.holiday_status_id
             """ % (cycle_ids))  #

            res = self.env.cr.dictfetchall()
            # # lapse the balance days of yearly entitlement
            for data in res:
                # if data['balance'] >0:
                # print("iff called",type(cycle_ids))
                # print(data['employee_id'],data['holiday_status_id'],LAPSE_TYPE_YEARLY,cycle_ids)
                yr_lapse_records = self.env['hr.leave.allocation'].sudo().search(
                    [('employee_id', '=', data['employee_id']), ('holiday_status_id', '=', data['holiday_status_id']),
                     ('lapse_alc_type', '=', LAPSE_TYPE_YEARLY),
                     ('leave_cycle_id', 'in', lapse_leave_cycle_records.ids)])
                yr_lapse_record_ids = '(%s)' % tuple(yr_lapse_records.ids)[0] if len(
                    yr_lapse_records.ids) == 1 else str(tuple(yr_lapse_records.ids))
                # print("lapse ids",yr_lapse_record_ids)
                # print("year",yr_lapse_records)

                try:
                    if not yr_lapse_records:
                        self.env.cr.execute(f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,
                        notes,state,holiday_type,number_of_days,leave_cycle_id,cycle_period,create_uid,create_date,
                        is_carried_forward,lapse_alc_type)
                        VALUES ({data['employee_id']},{data['holiday_status_id']},'Yearly Leave Lapse by System',
                        'Yearly Leave Lapse by System','validate','employee',{data['balance'] * -1},
                        {data['leave_cycle_id']},{data['cycle_period']},{self.env.user.id},'{datetime.now()}',
                        False,{LAPSE_TYPE_YEARLY}) 
                        """)
                    else:
                        self.env.cr.execute(f"""UPDATE hr_leave_allocation SET 
                        employee_id = {data['employee_id']},holiday_status_id = {data['holiday_status_id']},
                        name ='Yearly Leave Lapse by System',notes ='Yearly Leave Lapse by System',state ='validate',
                        holiday_type = 'employee',number_of_days = {data['balance'] * -1},
                        leave_cycle_id = {data['leave_cycle_id']},cycle_period = {data['cycle_period']},
                        create_uid = {self.env.user.id},create_date = '{datetime.now()}',is_carried_forward = False,
                        lapse_alc_type = {LAPSE_TYPE_YEARLY}  WHERE id in %s
                        """ % (yr_lapse_record_ids))

                except Exception as e:
                    # print(str(e))
                    pass
            # # invalidate the cache of the model
            if res:
                self.env['hr.leave.allocation'].invalidate_cache()

            # # deactivate the leave cycle
            lapse_leave_cycle_records.write({'active': False})

        # #leave carried forward lapse after 6 months
        # self.leave_yearly_carry_forward_lapse()

        # # Comp Off Leave Lapse
        self.lapse_comp_off_leaves()

        return

        # # method to lapse the yearly allocated leaves as per the leave cycle and leave type configuration

    #  Created By : T Ketaki Debadarshini
    #  Created On : 09-Feb-2021

    def leave_yearly_carry_forward_lapse(self):
        hr_leave_allocation = self.env['hr.leave.allocation'].sudo()
        # hr_leave            = self.env['hr.leave'].sudo()

        leave_cycle_records = self.env['kw_leave_cycle_master'].search([('cycle_period', '>', 0)])
        leave_cycle_ids = leave_cycle_records.ids if leave_cycle_records else []
        # print(leave_cycle_ids) 

        self.env.cr.execute(f""" SELECT employee_id,holiday_status_id,sum(number_of_days)as no_of_days,
        validity_start_date,validity_end_date 
        from hr_leave_allocation where state ='validate' and is_carried_forward =True and holiday_type ='employee' 
        and leave_cycle_id in (select id from kw_leave_cycle_master where cycle_period >0 and active = True)
        and holiday_status_id in (select id from hr_leave_type where carry_forward = True and active = True)
        group by employee_id,holiday_status_id,validity_start_date,validity_end_date
        """)

        allocation_res = self.env.cr.dictfetchall()
        # # lapse the balance days
        for record in allocation_res:
            # print(record)
            # print(record['employee_id'], record['validity_start_date'], record['validity_end_date'],
            #       record['holiday_status_id'], record['no_of_days'])

            if record['employee_id'] and record['no_of_days'] > 0 and record['validity_start_date'] \
                    and record['validity_end_date'] and record['validity_end_date'] < datetime.today().date():
                # cycle_rec     = leave_cycle_records.filtered(lambda rec:rec.id == record['leave_cycle_id'][0])
                # print(cycle_rec)

                self.env.cr.execute(f"""SELECT employee_id,holiday_status_id,sum(number_of_days),
                COALESCE(sum(case when request_date_to >= '{record['validity_start_date']}' and request_date_to <= '{record['validity_end_date']}' then number_of_days 
                when request_date_to > '{record['validity_end_date']}' and request_unit_half=True and request_date_from_period ='pm'  then DATE_PART('day',(TO_DATE('{record['validity_end_date']}', 'YYYY-MM-DD')::timestamp - request_date_from::timestamp)) +0.5  
                when request_date_to > '{record['validity_end_date']}' and request_unit_half=False then DATE_PART('day',(TO_DATE('{record['validity_end_date']}', 'YYYY-MM-DD')::timestamp - request_date_from::timestamp)) +1
                end ),0) as tot_leave_taken

                FROM hr_leave WHERE state ='validate' and holiday_type ='employee' 
                and leave_cycle_id in (select id from kw_leave_cycle_master where cycle_period >0 and active = True)
                and holiday_status_id in (select id from hr_leave_type where carry_forward = True and active = True)
                and employee_id = {record['employee_id']} and holiday_status_id = {record['holiday_status_id']} 
                and request_date_from >= '{record['validity_start_date']}' 
                and request_date_from <= '{record['validity_end_date']}'
                group by employee_id,holiday_status_id """)

                leave_res = self.env.cr.dictfetchall()

                # # check leave days and lapse the balance days
                cf_leave_balance = 0
                for lv_record in leave_res:
                    # print('###########################################')
                    # print(lv_record)
                    cf_leave_balance = record['no_of_days'] - lv_record['tot_leave_taken']

                if not leave_res:
                    cf_leave_balance = record['no_of_days']

                cf_lapse_records = hr_leave_allocation.search([('employee_id', '=', record['employee_id']),
                                                               ('holiday_status_id', '=', record['holiday_status_id']),
                                                               ('number_of_days', '<', 0),
                                                               ('lapse_alc_type', '=', LAPSE_TYPE_CF),
                                                               ('leave_cycle_id', 'in', leave_cycle_ids)])
                cf_lapse_record_ids = '(%s)' % tuple(cf_lapse_records.ids)[0] if len(
                    cf_lapse_records.ids) == 1 else str(tuple(cf_lapse_records.ids))
                # print(cf_lapse_record_ids)

                try:
                    employee_rec = self.env['hr.employee'].browse(record['employee_id'])
                    cycle_rec = leave_cycle_records.filtered(lambda rec: rec.branch_id.id == employee_rec.job_branch_id.id)
                    # print(cycle_rec)
                    # print((f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,notes,state,holiday_type,number_of_days,leave_cycle_id,cycle_period,create_uid,create_date,is_carried_forward)
                    # VALUES ({record['employee_id']},{record['holiday_status_id']},'Carry Forward Leave Lapse by System','Carry Forward Leave Lapse by System','validate','employee',{cf_leave_balance*-1},{cycle_rec.id},{cycle_rec.cycle_period},{self.env.user.id},'{datetime.now()}',False) 
                    # """))
                    if cf_leave_balance > 0:
                        if not cf_lapse_records:
                            self.env.cr.execute(f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,
                            notes,state,holiday_type,number_of_days,leave_cycle_id,cycle_period,create_uid,create_date,
                            is_carried_forward,lapse_alc_type)
                            VALUES ({record['employee_id']},{record['holiday_status_id']},
                            'Carry Forward Leave Lapse by System','Carry Forward Leave Lapse by System','validate',
                            'employee',{cf_leave_balance * -1},{cycle_rec.id},{cycle_rec.cycle_period},
                            {self.env.user.id},'{datetime.now()}',False,{LAPSE_TYPE_CF}) 
                            """)
                        else:
                            self.env.cr.execute(f"""UPDATE hr_leave_allocation SET 
                            employee_id = {record['employee_id']},holiday_status_id = {record['holiday_status_id']},
                            name ='Carry Forward Leave Lapse by System',notes ='Carry Forward Leave Lapse by System',
                            state ='validate',holiday_type = 'employee',number_of_days = {cf_leave_balance * -1},
                            leave_cycle_id = {cycle_rec.id},cycle_period = {cycle_rec.cycle_period},
                            create_uid = {self.env.user.id},create_date = '{datetime.now()}',is_carried_forward = False,
                            lapse_alc_type = {LAPSE_TYPE_CF}  WHERE id in %s
                            """ % (cf_lapse_record_ids))
                    elif cf_leave_balance <= 0 and cf_lapse_records:
                        self.env.cr.execute(
                            f"""DELETE FROM hr_leave_allocation WHERE id in %s""" % (cf_lapse_record_ids))

                except Exception as e:
                    # print(str(e))
                    pass

                # # invalidate the cache of the model
                self.env['hr.leave.allocation'].invalidate_cache()

        return

    # # method to lapse the compensatory off as per the expire dates and leave type configuration
    # Created By : T Ketaki Debadarshini
    # Created On : 04-March-2021

    def lapse_comp_off_leaves(self):
        hr_leave_allocation = self.env['hr.leave.allocation'].sudo()
        leave_cycle_records = self.env['kw_leave_cycle_master'].search([('cycle_period', '>', 0)])

        self.env.cr.execute(f"""SELECT employee_id,holiday_status_id,leave_cycle_id,cycle_period,
            sum(number_of_days-COALESCE(cmp_leave_taken,0)) AS no_of_days, array_agg(id) AS allocation_ids
            FROM hr_leave_allocation 
            WHERE state ='validate' AND validity_end_date < CURRENT_DATE  
            AND (cmp_leave_taken <1 or cmp_leave_taken is null) AND (is_lapsed = False or is_lapsed is null)
            AND holiday_status_id in (select id from hr_leave_type WHERE is_comp_off = True AND active = True)
            group by employee_id,holiday_status_id,leave_cycle_id,cycle_period        
        """)
        #        
        comp_off_lapse_records = self.env.cr.dictfetchall()
        for cmp_record in comp_off_lapse_records:
            # print(cmp_record)
            # print(cmp_record['allocation_ids'])

            try:
                employee_rec = self.env['hr.employee'].browse(cmp_record['employee_id'])
                # cycle_rec     = leave_cycle_records.filtered(lambda rec:rec.branch_id.id == employee_rec.job_branch_id.id)
                # print(cycle_rec)
                # print((f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,notes,state,holiday_type,
                # number_of_days,leave_cycle_id,cycle_period,create_uid,create_date,is_carried_forward,lapse_alc_type)
                #     VALUES ({cmp_record['employee_id']},{cmp_record['holiday_status_id']},
                #     'Comp Off Leave Lapse by System','Comp Off Leave Lapse by System','validate','employee',
                #     {cmp_record['no_of_days'] * -1},{cmp_record['leave_cycle_id']},{cmp_record['cycle_period']},
                #     {self.env.user.id},'{datetime.now()}',False,{LAPSE_TYPE_COMP_OFF})
                #     """))
                if cmp_record['no_of_days'] > 0:

                    self.env.cr.execute(f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,notes,
                    state,holiday_type,number_of_days,leave_cycle_id,cycle_period,create_uid,create_date,
                    is_carried_forward,lapse_alc_type)
                    VALUES ({cmp_record['employee_id']},{cmp_record['holiday_status_id']},
                    'Comp Off Leave Lapse by System','Comp Off Leave Lapse by System','validate','employee',
                    {cmp_record['no_of_days'] * -1},{cmp_record['leave_cycle_id']},{cmp_record['cycle_period']},
                    {self.env.user.id},'{datetime.now()}',False,{LAPSE_TYPE_COMP_OFF})  
                    """)
                    # # update the lapse status
                    if cmp_record['allocation_ids']:
                        lapsed_allocations = hr_leave_allocation.browse(cmp_record['allocation_ids'])
                        # print(lapsed_allocations)
                        lapsed_allocations.write({'is_lapsed': True})

            except Exception as e:
                # print(str(e))
                pass

            # # invalidate the cache of the model
            self.env['hr.leave.allocation'].invalidate_cache()

        return

    @api.model
    def lapse_el_timesheet_integration(self, employee, leave_code, number_of_days):
        leave_type = self.env['hr.leave.type'].search([('leave_code', '=', leave_code)], limit=1)
        leave_cycle_records = self.env['kw_leave_cycle_master'].search([('cycle_period', '>', 0)])
        if employee and leave_type and number_of_days > 0:
            try:
                employee_rec = self.env['hr.employee'].browse(employee)
                cycle_rec = leave_cycle_records.filtered(lambda rec: rec.branch_id.id == employee_rec.job_branch_id.id)
                # print(cycle_rec)
                # print((f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,notes,state,holiday_type,number_of_days,leave_cycle_id,cycle_period,create_uid,create_date,is_carried_forward,lapse_alc_type)
                # VALUES ({employee},{leave_type.id},'EL Lapse by Timesheet','EL Lapse by Timesheet','validate','employee',{number_of_days*-1},{cycle_rec.id},{cycle_rec.cycle_period},{self.env.user.id},'{datetime.now()}',False,{LAPSE_BY_TIMESHEET}) 
                # """))
                # if cf_leave_balance >0 :

                self.env.cr.execute(f"""INSERT INTO hr_leave_allocation (employee_id,holiday_status_id,name,notes,
                state,holiday_type,number_of_days,leave_cycle_id,cycle_period,create_uid,create_date,
                is_carried_forward,lapse_alc_type)
                VALUES ({employee},{leave_type.id},'EL Lapse by Timesheet','EL Lapse by Timesheet','validate',
                'employee',{number_of_days * -1},{cycle_rec.id},{cycle_rec.cycle_period},{self.env.user.id},
                '{datetime.now()}',False,{LAPSE_BY_TIMESHEET})""")
            except Exception as e:
                # print(str(e))
                pass

        # # invalidate the cache of the model
        self.env['hr.leave.allocation'].invalidate_cache()

    def lva_cmp_leave_taken_update(self):
        hr_leave_ids = self.env['hr.leave'].search(
            [('holiday_status_id.leave_code', '=', 'CMP'), ('state', '=', 'validate')])
        # print(hr_leave_ids)
        for leave in hr_leave_ids:
            if leave.holiday_status_id.is_comp_off:
                no_of_days = leave.number_of_days
                if leave.state == 'validate':
                    hr_allocations = self.env['hr.leave.allocation'].sudo().search(
                        [('state', '=', 'validate'), ('holiday_status_id.is_comp_off', '=', True),
                         ('cmp_leave_taken', '<', 1), ('validity_end_date', '>=', leave.request_date_from),
                         ('employee_id', '=', leave.employee_id.id)],
                        order="validity_end_date asc")
                    for alc_rec in hr_allocations:
                        if no_of_days > 0:
                            if no_of_days >= 1:
                                leave_taken = 0.5 if alc_rec.cmp_leave_taken == 0.5 else 1
                            else:
                                leave_taken = 0.5

                            # print('cmp_leave_taken ---- ')
                            cmp_leave_taken = alc_rec.cmp_leave_taken if alc_rec.cmp_leave_taken else 0

                            # print(1 if no_of_days >= 1 else cmp_leave_taken + 0.5)
                            alc_rec.write({'cmp_leave_taken': (1.0 if no_of_days >= 1 else cmp_leave_taken + 0.5)})
                            # print(alc_rec.cmp_leave_taken)
                            no_of_days = no_of_days - leave_taken
                            if no_of_days <= 0:
                                break
