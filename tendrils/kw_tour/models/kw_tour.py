import pytz
import uuid
import requests, json
from ast import literal_eval
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from odoo.tools.profiler import profile

'''
    Removal of escalation process from Apr 1 2021 (Gouranga)
'''


class Tour(models.Model):
    _name = "kw_tour"
    _description = "Tour Application"
    _rec_name = "employee_id"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.model
    def get_project_domain(self):
        domain = []
        if not self.env.user.has_group('kw_tour.group_kw_tour_super_manager'):
            record_employee = False
            if self._context.get('params') and self._context.get('params').get('id'):
                tour = self.env['kw_tour'].browse(self._context['params']['id'])
                record_employee = tour and tour.employee_id or False
            employee = record_employee or self._default_employee()
            if employee:
                domain = [('resource_id.emp_id', 'in', employee.ids)]
            else:
                domain = [('id', 'in', [])]
        return domain

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_loop = dt.replace(hour=23, minute=45, second=0, microsecond=0)

        time_list = [(start_loop.strftime('%H:%M:%S'),start_loop.strftime('%I:%M %p'))]

        while start_loop < end_loop:
            start_loop = (start_loop+relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'),
                              start_loop.strftime('%I:%M %p')))
        return time_list

    def _default_access_token(self):
        return uuid.uuid4().hex


    city_ids = fields.Many2many('kw_tour_city', compute='get_val', store=False)
    access_token = fields.Char('Access Token', default=_default_access_token)
    apply_for = fields.Selection(string='Apply for', selection=[('1', 'Self'), ('2', 'Others')],default='1')
    employee_id = fields.Many2one('hr.employee', string="Employee Name",
                                  default=_default_employee, required=True, ondelete='cascade', index=True)
    # other_emp_ids = fields.Many2many('hr.employee', 'other_emp_rel', 'other_id', 'emp_id', string="Employee Name")
    tour_type_new = fields.Many2one('kw_tour_type_new', string="Tour Type")
    tour_type_id = fields.Many2one('kw_tour_type', required=True, string="Purpose")
    project = fields.Boolean(string="Project Enabled ?", default=False, compute="_compute_project")
    project_type = fields.Selection(string='Project Type', selection=[('70', 'Work Order'), ('3', 'Opportunity')])
    project_id = fields.Many2one('crm.lead', string='Project')
    actual_project_id = fields.Many2one('project.project', string="Project", compute='_compute_get_project', store=True)
    # domain=get_project_domain
    purpose = fields.Text("Description", required=True)

    date_travel = fields.Date("Date Of Travel", required=True)
    date_return = fields.Date("Return Date", required=True)
    # used for reschedule case
    old_date_travel = fields.Date("Old Date Of Travel")
    old_date_return = fields.Date("Old Return Date")
    # used for reschedule case

    city_id = fields.Many2one('kw_tour_city', "Originating Place", required=True)

    tour_detail_ids = fields.One2many('kw_tour_details', 'tour_id', string="Tour Details", required=True)
    # total_ticket_cost = fields.Integer("Total Ticket Cost")
    acc_arrange = fields.Selection(string="Accommodation Arrangement", selection=[
        ('Self', 'Self'), ('Company', 'Company')], default="Company")
    accomodation_ids = fields.One2many('kw_tour_accomodation', 'tour_id', string="Accommodation Details")
    travel_detail_ids = fields.One2many('kw_tour_travel_details', 'tour_id', string="Travel Details")

    ancillary_expense_ids = fields.One2many('kw_tour_ancillary_expense_details', 'tour_id', string="Ancillary Expenses")
    settlement_ids = fields.One2many("kw_tour_settlement", "tour_id", string="Settlements")

    # csg_group_tour_id = fields.Many2one(string='CSG Tour', comodel_name='kw_group_tour_csg', ondelete='cascade')
    csg_group_tour_code=  fields.Char(string="Group/Tour No.",readonly="1")

    advance = fields.Float("Advance(In Domestic)", track_visibility='onchange')
    advance_usd = fields.Float("Advance(In USD)", track_visibility='onchange')
    exchange_rate = fields.Float(string="Exchange Rate", track_visibility='onchange')

    disbursed_inr = fields.Float("Amount Disbursed(Domestic)", track_visibility='onchange')
    disbursed_usd = fields.Float("Amount Disbursed(USD)", track_visibility='onchange')

    to_disbursed_inr = fields.Float("To be Disbursed(Domestic)", tracksettlement_ids_visibility='onchange')
    to_disbursed_usd = fields.Float("To be Disbursed(USD)", track_visibility='onchange')

    public_view = fields.Boolean("Enable Public View", default=True, track_visibility='onchange')
    ra_access = fields.Boolean("RA Access", compute="compute_ra_access")
    admin_access = fields.Boolean(string="Admin Access", compute="_compute_approve")
    travel_desk_access = fields.Boolean(string="Traveldesk Access", compute="_compute_approve")
    finance_access = fields.Boolean(string="Finance Access", compute="_compute_approve")

    state = fields.Selection(string='Status',
                             selection=[('Draft', 'Draft'),
                                        ('Applied', 'Applied'),
                                        ('Approved', 'Approved'),
                                        ('Forwarded', 'Forwarded'),
                                        ('Traveldesk Approved', 'Traveldesk Approved'),
                                        ('Finance Approved', 'Finance Approved'),
                                        ('Rejected', 'Rejected'),
                                        ('Cancelled', 'Cancelled')])

    # Start : for forwarding of application to any employee
    remark = fields.Text("Remark")
    forward = fields.Boolean("Forward", default=False)
    approver_id = fields.Many2one('hr.employee', 'Approver')
    final_approver_id = fields.Many2one('hr.employee', 'Final Approver')
    # End : for forwarding of application to any employee

    own_record = fields.Boolean("Own Record ?", compute="compute_own_access")
    current_user = fields.Many2one("res.users", string="Curent User", compute="compute_own_access")
    is_valid_authority = fields.Boolean(string="Valid User ?", compute="compute_own_access")

    last_city_id = fields.Many2one("kw_tour_city", string="Last City", compute="compute_last_city")
    last_travel_date = fields.Date(string="Last Date", compute="compute_last_city")
    last_travel_time = fields.Selection(selection='_get_time_list', string="Last Travel Time")

    cancellation_id = fields.Many2one("kw_tour_cancellation", "Cancellation", ondelete="set null")
    cancellation_status = fields.Boolean("Applied Cancellation ?", compute="compute_settlement_apply")

    advance_request_id = fields.Many2one("kw_tour_advance_request", "Advance Request", ondelete="set null")
    code = fields.Char(string="Reference No.", default="New", readonly="1")

    parent_id = fields.Many2one('kw_tour', "Old Tour", ondelete="cascade")
    child_id = fields.Many2one('kw_tour', "New Tour", ondelete="set null")
    status = fields.Selection(string='Type', required=True,
                              selection=[('Tour', 'Tour'), ('Rescheduled', 'Rescheduled')], default='Tour')

    city_days_spend_ids = fields.One2many('kw_tour_city_days_spend', 'tour_id', string="Days Spend")
    travel_expense_details_ids = fields.One2many('kw_tour_travel_expense_details', 'tour_id',
                                                 string="Travel Expenses", )
    job_id = fields.Many2one('hr.job', string="Designation", related="employee_id.job_id")
    dept_id = fields.Many2one('hr.department', string="Department Name", related="employee_id.department_id")

    end_date_over = fields.Boolean("Tour End Date Over", compute="compute_tour_start_end_date")
    tour_at_end_date_or_greater = fields.Boolean("Tour At End Date Or Greater", compute="compute_tour_start_end_date")

    actual_state = fields.Char("Status", compute="compute_pending_at", store=False)
    pending_at = fields.Char("Pending At", compute="compute_pending_at", store=False)

    action_log_ids = fields.One2many('kw_apply_tour_action_log', 'apply_tour_id', string='Action Logs')
    action_datetime = fields.Datetime(string="Action Time", default=fields.Datetime.now)
    applied_datetime = fields.Datetime(string="Applied Time")
    pending_time = fields.Char('Pending Time', compute="compute_pending_time")
    settlement_applied = fields.Boolean("Applied Settlement ?", compute="compute_settlement_apply")
    baggage_details = fields.Selection(string='Extra Baggage (in kg)',
                                       selection=[('0', '0-5'),
                                                  ('1', '5-8'),
                                                  ('2', '8-10'),
                                                  ('3', '10-15'),
                                                  ('4', '15-30'),
                                                  ('5', 'More Than 30')])
    destination_str = fields.Char('Desting String', compute="get_tour_destinations_string")
    tour_city_list_ids = fields.Many2many('kw_tour_city', compute="compute_tour_city_ids", store=False)
    advance_ids = fields.One2many(
        'kw_tour_advance_given_log', 'tour_id', string="Advance Action Logs")

    travel_ticket_cost_ids = fields.One2many(
        'kw_tour_travel_ticket_cost_log', 'tour_id', string="Travel Ticket Cost Logs")

    can_apply_inr = fields.Boolean(string='Can Apply For Advance INR ?', compute="_compute_advance_inr_usd")
    can_apply_usd = fields.Boolean(string='Can Apply For Advance USD ?', compute="_compute_advance_inr_usd")

    # upper_ra_id = fields.Many2one('hr.employee',string="Upper RA")
    # pending_status_at   = fields.Selection(string='Pending At (status)',
    #                                    selection=[('RA', 'Reporting Authority'),
    #                                               ('UA', 'Upper RA')])
    # upper_ra_switched_datetime    = fields.Datetime(string="UA Switched Datetime")

    tour_travel_detail_ids = fields.One2many(related="tour_detail_ids", string="Travel Arrangements")

    reschedule_count = fields.Integer("Reschedule Count", default=0)
    reschedule_log_ids = fields.One2many("kw_tour_reschedule_log", "tour_id", string="Reschedule Log")

    settlement_id = fields.Many2one("kw_tour_settlement", string="Settlement",
                                    help="Final Settlement Approved By Finance Team")
    settlement_granted_date = fields.Date(string="Settlement Granted Date", related="settlement_id.grant_date")
    settlement_granted_datetime = fields.Datetime(string="Settlement Granted Datetime",
                                                  related="settlement_id.grant_datetime")

    have_public_access = fields.Boolean("Can have access to change public view", compute="_compute_tour_public_access")
    budget_head = fields.Char(string="Budget Head", track_visibility='onchange')
    budget_head_id = fields.Many2one('kw_tour_budget_head', string="Budget Head", track_visibility='onchange')
    travel_arrangement = fields.Selection(string="Travel Arrangement",
                                          selection=[('Self', 'Self'), ('Company', 'Company')], required=True,
                                          default="Company")
    travel_ticket_ids = fields.One2many("kw_tour_travel_ticket", "tour_id", string="Ticket Details")
    
    travel_prerequisite_ids = fields.One2many('kw_tour_travel_prerequisite_details', 'tour_id',
                                              string="Travel Prerequisite")
    api_exchange_rate = fields.Float('API Exchange Rate')
    currency_id = fields.Many2one('res.currency', string="Currency of Total Budget Amount", store=True)
    total_budget_expense = fields.Float("Amount Blocked towards the total tour expenses", compute='_get_total_budget_expense', track_visibility='onchange', store=True)
    budget_limit_crossed = fields.Boolean('Budget Limit Crossed', compute='_compute_budget_limit_crossed')
    project_budget_id = fields.Many2one('kw_tour_project_budget', string='Project Budget',
                                        compute='_compute_project_budget')
    treasury_budget_id = fields.Many2one('kw_tour_treasury_budget', string='Treasury Budget',
                                        compute='_compute_project_budget')
    tour_others_applied_by = fields.Many2one('hr.employee', string="Applied By")
    bool_obj = fields.Boolean(string='Boolean', compute='_compute_dept_id')
    # department_id = fields.Many2one('hr.department', 'Treasury Department')
    emp_budget_amount = fields.Char('Revise Budget Amount(In Domestic Currency)')
    user_budget_boolean = fields.Boolean()
    csg_group_tour_boolean = fields.Boolean()
    pr_boolean = fields.Boolean()
    blocked_department_id = fields.Many2one('kw_tour_treasury_budget', 'Blocked Department')


    # @profile
    @api.onchange('tour_type_new')
    def get_tour_data_new(self):
        self.project_type = False
        self.tour_type_id = False
        p_id = self.env['kw_tour_type'].sudo().search([('code', '=', 'project')]).id
        if self.tour_type_new.name == 'Project':
            self.tour_type_id = p_id
            self.project_type = '70'
            self.pr_boolean = True
        elif self.tour_type_new.name == 'Opportunity':
            self.tour_type_id = p_id
            self.project_type = '3'
            self.pr_boolean = True
        else:
            self.pr_boolean = False


    @api.depends('employee_id')
    def get_val(self):
        if self.state != 'Draft':
            self.city_ids = [(6, 0, self.env['kw_tour_city'].search([('company_id', '=', self.employee_id.company_id.id)]).ids)]
        else:
            self.city_ids = [(6, 0, self.env['kw_tour_city'].search([('company_id', '=', self.env.user.company_id.id)]).ids)]



    @api.onchange('emp_budget_amount')
    def _onchange_emp_budget_amount(self):
        for record in self:
            if record.emp_budget_amount:
                try:
                    dataa = self.env['account.fiscalyear'].sudo().search(
                    [('date_start', '<=', self.date_travel), ('date_stop', '>=', self.date_travel)]).mapped('id')
                    self.total_budget_expense = float(self.emp_budget_amount)
                    self.user_budget_boolean = True
                    data = self.env['kw_tour_treasury_budget'].sudo().search([('fiscal_year_id', 'in', dataa), ('department_id', 'in', [self.create_uid.employee_ids.section.id,self.create_uid.employee_ids.division.id,self.create_uid.employee_ids.department_id.id])], limit=1)
                    spent_amount = sum(data.tour_ids.mapped('total_budget_expense')) + sum(data.settlement_ids.mapped('total_budget_expense'))
                    remaining_amount = data.budget_amount - spent_amount
                except:
                    raise ValidationError('Please Give Only Numeric Value.')

    def re_calculate_old_value(self):
        # old_amt = self.total_budget_expense
        self.user_budget_boolean = False
        self._get_total_budget_expense()



    def tour_apply_flow(self):
        data = self.env['account.fiscalyear'].sudo().search([
            ('date_start', '<=', self.date_travel),
            ('date_stop', '>=', self.date_travel)
        ]).mapped('id')
        settlement_pending = self.validate_tour_advance_process()
        treasury_budget =  self.env['kw_tour_treasury_budget'].sudo().search([])
        project_budget = self.env['kw_tour_project_budget'].sudo()
        if self.tour_type_id.name == 'Project' and self.project_type == '70':
            # project budget
            budget_amount = project_budget.search([('budget_head_id', '=', self.budget_head_id.id),
                                                   ('project_id', '=', self.project_id.id),
                                                   ])
            total_tour_amount = 0
            if self.cancellation_status is False and self.settlement_applied is False:
                total_tour_amount += self.total_budget_expense
            if budget_amount:
                threshold_amount = float(budget_amount.remaining_amount) * budget_amount.threshold_limit / 100
                if threshold_amount < 0:
                    raise ValidationError(
                        'Insufficient Balance Found in your Project budget. Please Contact Your PM for Further Information.')
                elif threshold_amount > 0 and threshold_amount <  total_tour_amount:
                    raise ValidationError(
                        'Insufficient Balance Found in your Project budget. Please Contact Your PM for Further Information.')
                elif threshold_amount == 0:
                    raise ValidationError(
                        'No Budget Data Found in your Project. Please Contact your PM for Further Information.')
                else:
                    pass
            else:
                raise ValidationError(
                    'No Budget Data Found in your Project. Please Contact Finance Dept. for Further Information.')

        else:
            # treasury budget
            data = self.env['account.fiscalyear'].sudo().search([
                ('date_start', '<=', self.date_travel),
                ('date_stop', '>=', self.date_travel)
            ]).mapped('id')

            sec_data = self.env['kw_tour_treasury_budget'].sudo().search([
                ('fiscal_year_id', 'in', data),
                ('department_id', '=', self.create_uid.employee_ids.section.id),
                ('currency_id', '=', self.currency_id.id)
            ])
            div_data = self.env['kw_tour_treasury_budget'].sudo().search([
                ('fiscal_year_id', 'in', data),
                ('department_id', '=', self.create_uid.employee_ids.division.id),
                ('currency_id', '=', self.currency_id.id)
            ])
            dep_data = self.env['kw_tour_treasury_budget'].sudo().search([
                ('fiscal_year_id', 'in', data),
                ('department_id', '=', self.create_uid.employee_ids.department_id.id),
                ('currency_id', '=', self.currency_id.id)
            ])
            if self.create_uid.employee_ids.section and sec_data:
                self.blocked_department_id = sec_data.id
            elif self.create_uid.employee_ids.division and div_data:
                self.blocked_department_id = div_data.id
            elif self.create_uid.employee_ids.department_id and dep_data:
                self.blocked_department_id = dep_data.id
            else:
                raise ValidationError('No Budget Data Found. Please Contact Your PM/RA For Further Information.')

            total_tour_amount = 0
            if self.cancellation_status is False and self.settlement_applied is False:
                total_tour_amount += self.total_budget_expense
            if self.sudo().blocked_department_id:
                if self.sudo().blocked_department_id.remaining_amount < total_tour_amount:
                    raise ValidationError(
                        'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
            else:
                department_sec = self.env['kw_tour_treasury_budget'].sudo().search(
                    [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.section.id), ('company_id', '=', self.employee_id.user_id.company_id.id)],
                    limit=1)
                department_div = self.env['kw_tour_treasury_budget'].sudo().search(
                    [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.division.id), ('company_id', '=', self.employee_id.user_id.company_id.id)],
                    limit=1)
                department_dep = self.env['kw_tour_treasury_budget'].sudo().search(
                    [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.department_id.id), ('company_id', '=', self.employee_id.user_id.company_id.id)],
                    limit=1)
                if department_sec:
                    if department_sec.remaining_amount < total_tour_amount:
                        raise ValidationError(
                            'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
                elif department_div:
                    if department_div.remaining_amount < total_tour_amount:
                        raise ValidationError(
                            'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
                elif department_dep:
                    if department_dep.remaining_amount < total_tour_amount:
                        raise ValidationError(
                            'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
                else:
                    raise ValidationError('No Budget Data Found. Please Contact Your PM/RA For Further Information.')

        #     -----------------------------------------------------------------------------------------
        company_accomodation = self.tour_detail_ids.filtered(lambda r:r.accomodation_arrangement != "Not Required")
        if company_accomodation and not self.accomodation_ids:
            raise ValidationError("Please fill accomodation details.")
        if settlement_pending:
            if self.advance:
                raise ValidationError("Can't add Advance(In INR) due to settlement is pending for tour" + settlement_pending[0].code)

            if self.advance_usd:
                raise ValidationError("Can't add Advance(In USD) due to settlement is pending for tour" + settlement_pending[0].code)

            if self.exchange_rate:
                raise ValidationError("Can't add Exchange Rate due to settlement is pending for tour" + settlement_pending[0].code)

        if not self.employee_id.parent_id:
            self.write({'state':'Approved','applied_datetime':datetime.now(),'action_datetime':datetime.now()})
            tour_dates = self.generate_days_with_from_and_to_date(self.date_travel,self.date_return)
            try:
                attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('employee_id','=',self.employee_id.id),
                                                                                            ('attendance_recorded_date', 'in', tour_dates)])
                for record in attendance_records:
                    if record.is_on_tour != True:
                        try:
                            record.write({'is_on_tour':True})
                        except Exception as e:
                            continue
            except Exception:
                pass
            template = self.env.ref('kw_tour.kw_tour_apply_without_ra_email_template')
            travel_desk_group = self.env.ref('kw_tour.group_kw_tour_travel_desk')
            emails = ','.join(travel_desk_group.mapped('users.employee_ids.work_email'))
            template.with_context(email_users=emails).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            self.write({'state':'Applied','action_datetime':datetime.now(),'applied_datetime':datetime.now()})
            template = self.env.ref('kw_tour.kw_tour_apply_email_template')
            ra = self._get_tour_approver()
            email_cc_list = []
            if self.employee_id.coach_id:
                email_cc_list.append(self.employee_id.coach_id.work_email)
            if self.tour_type_id.code == 'project' and self.actual_project_id:
                email_cc_list.append(self.actual_project_id.emp_id.work_email)
            if self.actual_project_id and self.actual_project_id.reviewer_id:
                email_cc_list.append(self.actual_project_id.reviewer_id.work_email)
            if self.csg_group_tour_boolean == True:
                email_cc_list.append(self.employee_id.work_email)
            # print('-------------7--------next-', self.access_token, self._cr.dbname, ra.work_email, ra.name, ','.join(email_cc_list))
            template.with_context(token=self.access_token,dbname=self._cr.dbname,manager_email=ra.work_email,
                        manager_name=ra.name, email_cc=','.join(email_cc_list)).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env['kw_tour'].notify_users(ra.user_id,'Tour has been applied by '+self.env.user.name)
            self.env.user.notify_success("Tour applied successfully.")
        form_view_id = self.env.ref('kw_tour.view_kw_tour_form').id
        tree_view_id = self.env.ref('kw_tour.view_kw_tour_tree').id

        action = {
                'name'      : 'Apply Tour',
                'view_type' : 'form',
                'view_mode' : 'tree,form',
                'view_id'   : False,
                'res_model' : 'kw_tour',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'domain'    : [('create_uid','=',self.env.user.id)],
                'views'     : [(tree_view_id, 'tree'), (form_view_id, 'form')],
            }

    @api.depends('employee_id')
    def _compute_dept_id(self):
        if self.env.user.has_group('kw_tour.group_kw_tour_csg_user'):
            self.bool_obj = True
        else:
            self.bool_obj = False

    @api.multi
    def _compute_project_budget(self):
        for record in self:
            record.project_budget_id = False
            record.treasury_budget_id = False
            data = self.env['account.fiscalyear'].sudo().search([
                ('date_start', '<=', record.date_travel),
                ('date_stop', '>=', record.date_travel)
            ]).mapped('id')
            if record.tour_type_id.name == 'Project' and record.project_type == '70' and record.project_id and record.budget_head_id and record.state not in ['Draft', 'Cancelled', 'Rejected'] and not record.settlement_applied:
                project_budget = self.env['kw_tour_project_budget'].sudo().search([('budget_head_id', '=', record.budget_head_id.id),
                                                                                   ('project_id', '=', record.project_id.id),
                                                                                   ], limit=1)
                if project_budget:
                    record.project_budget_id = project_budget.id
                else:
                    pass
            else:
                if record.blocked_department_id and record.state not in ['Draft', 'Cancelled', 'Rejected'] and not record.settlement_applied:
                    record.treasury_budget_id = record.blocked_department_id
                else:
                    data = self.env['account.fiscalyear'].sudo().search([
                        ('date_start', '<=', record.date_travel),
                        ('date_stop', '>=', record.date_travel)
                    ]).mapped('id')

                    if record.state not in ['Draft', 'Cancelled', 'Rejected'] and not record.settlement_applied:
                        employee = record.create_uid.employee_ids
                        sec_data = self.env['kw_tour_treasury_budget'].sudo().search([
                                ('fiscal_year_id', 'in', data),
                                ('department_id', '=', employee.section.id),
                                ('currency_id', '=', record.currency_id.id)
                            ], limit=1)
                        div_data = self.env['kw_tour_treasury_budget'].sudo().search([
                                ('fiscal_year_id', 'in', data),
                                ('department_id', '=', employee.division.id),
                                ('currency_id', '=', record.currency_id.id)
                            ], limit=1)
                        dep_data = self.env['kw_tour_treasury_budget'].sudo().search([
                                ('fiscal_year_id', 'in', data),
                                ('department_id', '=', employee.department_id.id),
                                ('currency_id', '=', record.currency_id.id)
                            ], limit=1)
                        if employee.section and sec_data:
                            record.treasury_budget_id = sec_data.id
                        elif employee.division and div_data:
                            record.treasury_budget_id = div_data.id
                        elif employee.department_id and dep_data:
                            record.treasury_budget_id = dep_data.id

    # def _auto_init(self):
    #     super(Tour, self)._auto_init()
    #     self.env.cr.execute("delete from kw_tour_travel_ticket where tour_id is not null")
    #     self.env.cr.execute("update kw_tour set travel_arrangement = kw_tour_details.travel_arrangement from kw_tour_details where kw_tour_details.tour_id = kw_tour.id")
    #     self.env.cr.execute("insert into kw_tour_travel_ticket (tour_id, booking_date, travel_mode_id, currency_id, cost, document, document_name) select tour_id, from_date, travel_mode_id, currency_id, cost, document, document_name from kw_tour_details where travel_mode_id is not null and currency_id is not null")

    def _get_tour_approver(self):
        approver = self.employee_id and self.employee_id.parent_id or False
        if self.tour_type_id.code == 'project':
            if self.actual_project_id:
                # print(self.actual_project_id, 'self.actual_project_id.emp_id')
                if self.actual_project_id.emp_id.id == self.employee_id.id \
                        and self.actual_project_id.reviewer_id.id != self.employee_id.id:
                    approver = self.actual_project_id.reviewer_id or False
                elif self.actual_project_id.emp_id.id != self.employee_id.id\
                        and self.actual_project_id.reviewer_id.id != self.employee_id.id:
                    approver = self.actual_project_id.emp_id or False
        return approver

    @api.onchange('travel_arrangement')
    def onchange_travel_arrangement(self):
        if self.travel_arrangement:
            self.travel_ticket_ids = False

    @api.depends('city_id')
    @api.multi
    def _compute_tour_public_access(self):
        available_job_ids = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_public_access_job_ids') or '[]')
        for tour in self:
            if tour.employee_id.job_id and tour.employee_id.job_id.id in available_job_ids:
                tour.have_public_access = True
    
    @api.constrains('public_view')
    def validate_public_view(self):
        for tour in self:
            if not tour.have_public_access and not tour.public_view:
                raise ValidationError("You don't have access to disable public view.")

    def validate_tour_advance_process(self):
        """[checks the pending settlements for a tour by its employee_id.
            if tour state not in ['Draft','Rejected','Cancelled'] those are considered to be pending with additionally,
                1.don't have settlements or
                2.any settlement is not in ['Approved','Granted','Payment Done','Posted']
            ]

        Raises:
            None

        Returns:
            [kw_tour recordset]: [tours having settlement incomplete].

        Last Modified:
            On 17 March 2021 (Gouranga)
        """
        self.ensure_one()
        employee_tours = self.search(['&', ('employee_id', '=', self.employee_id.id),
                                      '|',
                                      '&', ('state', 'not in', ['Draft', 'Rejected', 'Cancelled']),
                                      '|', '|', '|', ('advance', '>', 0), ('advance_usd', '>', 0),
                                      ('disbursed_inr', '>', 0), ('disbursed_usd', '>', 0),

                                      '&', '&', ('state', '=', 'Draft'), ('status', '=', 'Rescheduled'),
                                      '|', ('disbursed_inr', '>', 0), ('disbursed_usd', '>', 0)

                                      ]) - self
        settlement_pending = employee_tours.filtered(lambda r: not r.settlement_ids or not set(r.settlement_ids.mapped('state')) & {'Approved','Granted','Payment Done','Posted'})
        return settlement_pending

    @api.constrains('advance', 'advance_usd', 'exchange_rate')
    def validate_if_user_has_pending_settlements(self):
        for tour in self:
            if not tour.state == 'Draft':
                settlement_pending = tour.validate_tour_advance_process()
                if settlement_pending:
                    if tour.advance:
                        raise ValidationError(f"Can't add Advance(In INR) due to settlement is pending for tour {settlement_pending[0].code}.")

                    if tour.advance_usd:
                        raise ValidationError(f"Can't add Advance(In USD) due to settlement is pending for tour {settlement_pending[0].code}.")

                    if tour.exchange_rate:
                        raise ValidationError(f"Can't add Exchange Rate due to settlement is pending for tour {settlement_pending[0].code}.")

    @api.onchange('project_type')
    def change_project(self):
        employee =  self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.project_id = False
        domain = {'project_id': [('id', '=', 0)]}

        if not employee:
            if 'params' in self._context and 'id' in self._context['params'] \
                    and 'model' in self._context['params'] \
                    and self._context['params'].get('model', '') == 'kw_tour':
                tour = self.browse(self._context['params']['id'])
                employee = tour.employee_id

        if self.project_type == "70":
            if employee.user_id.has_group('kw_tour.group_kw_tour_management') or employee.user_id.has_group('kw_tour.group_kw_tour_it'):
                domain['project_id'] = [('stage_id.sequence', '=', 70)]
            else:
                emp_kw_id = employee.kw_id or 0
                project_url = self.env.ref('kw_tour.kw_tour_project_url_system_parameter').sudo().value

                header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
                data = json.dumps({"userId": emp_kw_id})
                try:
                    resp_result = requests.post(project_url, headers=header, data=data)
                    resp = json.loads(resp_result.text)
                    if resp.get('retEOSDa', False):
                        id_list = [int(module_dict['ModuleID']) for module_dict in resp['retEOSDa']]
                        domain['project_id'] = [('kw_workorder_id', 'in', id_list)]
                except Exception as e:
                    # print(e)
                    pass

        elif self.project_type == "3":
            bss_department = self.env['hr.department'].search([('code', 'in', ['bss', 'Bss', 'BSS'])], limit=1)
            if employee.department_id and employee.department_id == bss_department:
                pass
            else:
                domain['project_id'] = [('stage_id.sequence', '=', 3)]

        return {'domain': domain}

    @api.depends("tour_detail_ids")
    @api.multi
    def _compute_advance_inr_usd(self):
        for tour in self:
            inr_expense = tour.travel_expense_details_ids.filtered(lambda r: r.amount_domestic > 0)
            usd_expense = tour.travel_expense_details_ids.filtered(lambda r: r.amount_international > 0)
            if inr_expense:
                tour.can_apply_inr = True
            if usd_expense:
                tour.can_apply_usd = True

    def can_take_action(self):
        tour = self
        tour.ensure_one()
        user = self.env.user
        status = False

        if tour.state == "Applied":
            if tour.employee_id.parent_id.user_id == user:
                status = True
        elif tour.state == "Forwarded":
            if user.employee_ids and tour.final_approver_id in user.employee_ids:
                status = True
        elif tour.state == "Approved":
            status = user.has_group('kw_tour.group_kw_tour_travel_desk')

        elif tour.state == "Traveldesk Approved":
            status = user.has_group('kw_tour.group_kw_tour_finance')

        return status
        
    @api.depends('tour_detail_ids')
    @api.multi
    def compute_tour_city_ids(self):
        for tour in self:
            from_cities = tour.tour_detail_ids.mapped('from_city_id')
            to_cities = tour.tour_detail_ids.mapped('to_city_id')
            all_cities = from_cities | to_cities
            tour.tour_city_list_ids = [(6, False, all_cities.ids)]

    @api.multi
    def get_tour_destinations_string(self):
        for tour in self:
            dest_str = ""
            for index, detail in enumerate(tour.tour_detail_ids):
                if index == 0:
                    dest_str += f"{detail.from_city_id.name} -> {detail.to_city_id.name}"
                else:
                    dest_str += f", {detail.from_city_id.name} -> {detail.to_city_id.name}"
            tour.destination_str = dest_str

    @api.constrains('date_travel', 'date_return')
    def validate_travel_return_date(self):
        # current_date = date.today()
        for tour in self:
            if tour.date_return < tour.date_travel:
                raise ValidationError("Return date can't be less than Date of travel.")

    @api.multi
    def compute_settlement_apply(self):
        for tour in self:
            settlement_applied = self.env['kw_tour_settlement'].search(
                [('tour_id', '=', tour.id), ('state', 'not in', ['Rejected', 'Draft'])])
            if settlement_applied:
                tour.settlement_applied = True

            cancellation_applied = self.env['kw_tour_cancellation'].search(
                [('tour_id', '=', tour.id), ('state', 'not in', ['Rejected'])])
            if cancellation_applied:
                tour.cancellation_status = True
                
    @api.multi
    def compute_pending_time(self):
        current_time = Datetime.now()
        for tour in self:
            time_format = ''
            time = current_time - tour.action_datetime
            days = time.days
            seconds = time.seconds
            hours = seconds//3600
            if days:
                time_format += f'{days} Day(s) '
            if hours:
                time_format += f'{hours} Hour(s) '
            tour.pending_time = time_format

    @api.depends('state','cancellation_id','cancellation_id.state')        
    @api.multi
    def compute_pending_at(self):
        for record in self:
            cancellation = record.cancellation_id
            record.actual_state = record.state
            approver = record._get_tour_approver()
            if cancellation and cancellation.state == 'Applied':
                # record.pending_at = record.employee_id.parent_id and record.employee_id.parent_id.name or ''
                record.pending_at = approver and approver.name or ''
                record.actual_state = 'Cancellation Applied'

            elif record.state == 'Applied':
                # record.pending_at = record.employee_id.parent_id and record.employee_id.parent_id.name or ''
                record.pending_at = approver and approver.name or ''

            elif record.state == 'Forwarded':
                record.pending_at = record.final_approver_id.name

            elif record.state == 'Approved':
                traveldesk_users = self.env.ref('kw_tour.group_kw_tour_travel_desk').users.mapped('name')
                record.pending_at = ', '.join(traveldesk_users)

            elif record.state == 'Traveldesk Approved':
                finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users.mapped('name')
                record.pending_at = ', '.join(finance_users)

    @api.multi
    def compute_tour_start_end_date(self):
        for tour in self:
            last_date = max(tour.tour_detail_ids.mapped('to_date'))
            # if Datetime.now() > last_date:
            if date.today() > last_date:
                tour.end_date_over = True
            if date.today() >= last_date:
                tour.tour_at_end_date_or_greater = True
    
    @api.multi
    def compute_own_access(self):
        for tour in self:
            tour.own_record = tour.create_uid == self.env.user
            tour.own_record = tour.employee_id.user_id == self.env.user
            tour.current_user = self.env.user
            approver = tour._get_tour_approver()
            if tour.state == 'Draft' and tour.employee_id.user_id == self.env.user:
                tour.is_valid_authority = True
            # elif tour.state == 'Applied' and tour.employee_id.parent_id and tour.employee_id.parent_id.user_id == self.env.user:
            elif tour.state == 'Applied' and approver and approver.user_id == self.env.user:
                tour.is_valid_authority = True
            elif tour.state == 'Approved' and self.env.user.has_group('kw_tour.group_kw_tour_travel_desk'):
                tour.is_valid_authority = True
            elif tour.state == 'Forwarded' and tour.final_approver_id and tour.final_approver_id.user_id == self.env.user:
                tour.is_valid_authority = True
            elif tour.state == 'Traveldesk Approved' and self.env.user.has_group('kw_tour.group_kw_tour_finance'):
                tour.is_valid_authority = True
            
    @api.depends('city_id', 'tour_detail_ids', 'date_travel')
    @api.multi
    def compute_last_city(self):
        # user_timezone = pytz.timezone(self.env.user.tz or 'UTC')
        for tour in self:
            if not tour.tour_detail_ids:
                tour.last_city_id = tour.city_id and tour.city_id.id or False
                # tour.last_travel_date = Datetime.to_datetime(tour.date_travel)
                tour.last_travel_date = tour.date_travel

                if not tour.date_return:
                    tour.date_return = tour.date_travel
            else:
                tour.last_city_id = tour.tour_detail_ids[-1].to_city_id.id
                tour.last_travel_date = tour.tour_detail_ids[-1].to_date
                tour.last_travel_time = tour.tour_detail_ids[-1].to_time
                # tour.date_return = max(tour.tour_detail_ids.mapped('to_date')).astimezone(user_timezone).date()
                tour.date_return = max(tour.tour_detail_ids.mapped('to_date'))
                tour.date_travel = min(tour.tour_detail_ids.mapped('from_date'))
                tour.city_id = tour.tour_detail_ids[0].from_city_id.id

    @api.multi
    def validate_accomodation_details(self):
        self.ensure_one()
        user_timezone = pytz.timezone(self.env.user.tz or 'UTC')

        invalid_accomodation_check_in_check_out = self.accomodation_ids.filtered(lambda r: not (self.date_travel <= r.check_in_time.astimezone(user_timezone).date() <= self.date_return)
                                                                                           or not (self.date_travel <= r.check_out_time.astimezone(user_timezone).date() <= self.date_return))
        if invalid_accomodation_check_in_check_out:
            raise ValidationError("Check In Date & Time and Check Out Date & Time must be between date of travel and return date in accommodation details.")

        for accomodation in self.accomodation_ids:
            '''validate for invalid check in check out date '''
            city = accomodation.city_id
            city_dict = self.get_city_halt_time()

            from_date_time = accomodation.check_in_time.astimezone(user_timezone).replace(tzinfo=None)  # .date()
            to_date_time = accomodation.check_out_time.astimezone(user_timezone).replace(tzinfo=None)  # .date()

            in_city_date = False
            city_data = city_dict.get(city.id, [])

            message = ''
            if not city_data:
                message += f"Reason : No accommodation found for {city.name}"
            else:
                message += f"Accommodation details for  {city.name} are : \n\n"
                for index, d in enumerate(city_data, start=1):
                    start, end = d
                    message += f"{index}. From : {start.strftime('%d-%b-%Y %I:%M %p')}  To : {end.strftime('%d-%b-%Y %I:%M %p')}\n"
                message += "\nPlease check in and check out within above details."

            for data in city_data:
                start, end = data
                if start <= from_date_time <= end and start <= to_date_time <= end:
                    in_city_date = True
                    break

            if not in_city_date:
                raise ValidationError(f'''Invalid Check In Date & Time  and Check Out Date & Time for  {city.name} .\n {message} ''')

    @api.constrains('tour_type_id', 'tour_detail_ids', 'accomodation_ids', 'travel_detail_ids', 'date_travel',
                    'date_return', 'city_id', 'travel_ticket_ids', 'travel_arrangement', 'travel_prerequisite_ids',
                    'project_type', 'project_id', 'budget_head_id', 'advance', 'advance_usd')
    def _validate_tour_details(self):
        '''
        1.At least one record in tour details.
        2.validate date of tour details must be same or greater than tour date of travel.
        3.validate to date of tour details must be same or greater than to_date of tour details.
        4.validate accommodation details checkin datetime and checkout datetime to be between tour travel and return date.
        5.validate travel details travel date to be between tour travel and return date.
        6.Al least one record in ticket details
        '''
        # user_timezone = pytz.timezone(self.env.user.tz or 'UTC')
        for tour in self:
            tour.currency_id = tour.employee_id.user_id.company_id.currency_id.id
            if tour.tour_type_id and not tour.tour_detail_ids:
                raise ValidationError('Please add tour details.')
            if tour.tour_type_id and tour.travel_arrangement == 'Self' and not tour.travel_ticket_ids:
                raise ValidationError('Please add ticket details.')

            overlappings = self.search([
                '&',
                '&', ('state', 'not in', ['Rejected', 'Cancelled']), ('employee_id', '=', tour.employee_id.id),
                '|',
                '|', '&', ('date_travel', '<=', tour.date_travel), ('date_return', '>=', tour.date_travel),
                '|', '&', ('date_travel', '<=', tour.date_return), ('date_return', '>=', tour.date_return), '&',
                    ('date_travel', '<=', tour.date_travel), ('date_return', '>=', tour.date_return),
                '|', '&', ('date_travel', '>=', tour.date_travel), ('date_travel', '<=', tour.date_return), '&',
                    ('date_return', '>=', tour.date_travel), ('date_return', '<=', tour.date_return)
            ]) - tour
                
            overlapping = overlappings - overlappings.filtered(lambda r:r.date_travel >= tour.date_return or r.date_return <= tour.date_travel)
            if overlapping:
                message = f'''There is already a tour having Date of Travel {overlapping[0].date_travel.strftime("%d-%b-%Y")} & Date of Return {overlapping[0].date_return.strftime("%d-%b-%Y")}.\n
                            Please try within a different date range.'''
                raise ValidationError(message)

            journey_date = min(tour.tour_detail_ids.mapped('from_date'))
            end_date = max(tour.tour_detail_ids.mapped('to_date'))
            start_city = tour.tour_detail_ids[0].from_city_id
            last_city = tour.tour_detail_ids[-1].to_city_id.name
            # company_accomodation = self.tour_detail_ids.filtered(lambda r:r.accomodation_arrangement=="Company")

            if start_city != tour.city_id:
                raise ValidationError("Originating place must be same with tour start city.")

            if journey_date != tour.date_travel:
                raise ValidationError("Date of travel must be same with tour start date.")

            if end_date != tour.date_return:
                raise ValidationError("Return date must be same with tour end date.")

            if tour.tour_detail_ids[-1].accomodation_arrangement != "Not Required":
                raise ValidationError(f'''Accommodation arrangement for the final destination ({last_city}) should be selected as 'Not Required' in Tour Details.''')

            # if company_accomodation and not self.accomodation_ids:
            #     raise ValidationError("Please fill accomodation details.")
            
            same_from_and_to_city = self.tour_detail_ids.filtered(lambda r: r.from_city_id == r.to_city_id)

            if same_from_and_to_city:
                raise ValidationError("From and To city must be different in tour details.")

            for index,tour_detail in enumerate(self.tour_detail_ids):

                if tour_detail.from_time and tour_detail.to_time:
                    from_date = datetime.strptime(tour_detail.from_date.strftime("%Y-%m-%d") + ' ' + tour_detail.from_time, "%Y-%m-%d %H:%M:%S")
                    to_date = datetime.strptime(tour_detail.to_date.strftime("%Y-%m-%d") + ' ' + tour_detail.to_time, "%Y-%m-%d %H:%M:%S")
                    if not to_date > from_date:
                        raise ValidationError("To date time must be greater than from date time.")

                if tour_detail.from_date < tour.date_travel:
                    raise ValidationError("From date in tour details should not less than date of travel.")

                if tour_detail.to_date < tour.date_travel:
                    raise ValidationError("To date in tour details should not less than date of travel.")

                if tour_detail.to_date < tour_detail.from_date:
                    raise ValidationError("To date in tour details should not less than from date of tour details.")

                if not index == 0:
                    prev_tour_details = self.tour_detail_ids[index-1]
                   
                    if not tour_detail.from_city_id == prev_tour_details.to_city_id:
                        raise ValidationError("From city in tour details should be equal of previous To city.")

                    if not tour_detail.from_date >= prev_tour_details.to_date:
                        raise ValidationError("From date must be greater than previous to date")

                # if tour_detail.travel_arrangement == 'Self' and tour_detail.cost <= 0:
                #     raise ValidationError(f"Cost should not be zero while Travel Arrangement is Self. In tour details at row {index + 1}.")
                #
                # if tour.state == 'Approved' and tour_detail.cost <= 0:
                #     raise ValidationError(f"Cost should not be zero. In tour details at row {index + 1}.")

            for index, ticket_detail in enumerate(tour.travel_ticket_ids):
                if tour.travel_arrangement == 'Self' and ticket_detail.cost <= 0:
                    raise ValidationError(f"Ticket cost should not be zero in ticket details at row {index + 1}.")

                if tour.state == 'Approved' and ticket_detail.cost <= 0:
                    raise ValidationError(f"Ticket cost should not be zero in ticket details at row {index + 1}.")

            for index, prerequisite in enumerate(tour.travel_prerequisite_ids):
                if prerequisite.amount <= 0:
                    raise ValidationError(f"Amount should not be zero in travel prerequisite at row {index + 1}.")

            if tour.state == 'Approved':
                tour.validate_accomodation_details()


            # if tour.state in ('Draft', 'Applied','Approved'):
            #     tour.validate_accomodation_details()

            invalid_travel_details_date = tour.travel_detail_ids.filtered(lambda r: not (tour.date_travel <= r.travel_date<= tour.date_return))
            if invalid_travel_details_date:
                raise ValidationError("Travel date in travel details should be between date of travel and return date.")

            # if international tour check and get exchange rate
            if tour.can_apply_usd is True:
                dict_excange = {'INR':'rate',
                                'KES':'kenya_rate',
                                'AED':'dubai_rate',
                                'CAD':'canada_rate',
                                'RWF':'rawanda_rate'}
                if tour.employee_id.user_id.company_id.currency_id.name in dict_excange:
                    # print('==================', self.env.user.company_id.currency_id.name)

                    today_exchange_rate = self.env['kw_tour_exchange_rate'].search([('date', '=', tour.date_travel)],
                                                                                   limit=1)
                    val = today_exchange_rate.mapped(dict_excange[tour.employee_id.user_id.company_id.currency_id.name])
                    try:
                        if today_exchange_rate:
                            tour.api_exchange_rate = val[0]
                        else:
                            previous_exchange_rate = self.env['kw_tour_exchange_rate'].search(
                                [('date', '<', tour.date_travel)], limit=1)
                            vall = today_exchange_rate.mapped(dict_excange[tour.employee_id.user_id.company_id.currency_id.name])
                            if previous_exchange_rate:
                                tour.api_exchange_rate = vall[0]
                            else:
                                raise ValidationError("No Exchange rate set for the date of travel.\n"
                                                  "Contact Finance to set exchange rate.")
                    except:
                        today_exchange_ratee = self.env['kw_tour_exchange_rate'].search([('date', '=', date.today())],
                                                                                       limit=1)
                        value = today_exchange_ratee.mapped(dict_excange[tour.employee_id.user_id.company_id.currency_id.name])
                        tour.api_exchange_rate = value[0]


            # Validation Budget
            # data = self.env['account.fiscalyear'].sudo().search([
            #     ('date_start', '<=', self.date_travel),
            #     ('date_stop', '>=', self.date_travel)
            # ]).mapped('id')
            # project_budget = self.env['kw_tour_project_budget'].sudo()
            # if self.tour_type_id.name == 'Project' and self.project_type == '70':
            #     # project budget
            #     budget_amount = project_budget.search(
            #         [('budget_head_id', '=', self.budget_head_id.id),
            #          ('project_id', '=', self.project_id.id),
            #          ])
            #     total_tour_amount = 0
            #     if self.cancellation_status is False and self.settlement_applied is False:
            #         total_tour_amount += self.total_budget_expense
            #     if budget_amount:
            #         threshold_amount = float(budget_amount.remaining_amount) * budget_amount.threshold_limit / 100
            #         if threshold_amount < 0:
            #             raise ValidationError(
            #                 'Insufficient Balance Found in your Project budget. Please Contact Your PM for Further Information.')
            #         elif threshold_amount > 0 and threshold_amount < total_tour_amount:
            #             raise ValidationError(
            #                 'Insufficient Balance Found in your Project budget. Please Contact Your PM for Further Information.')
            #         elif threshold_amount == 0:
            #             raise ValidationError(
            #                 'No Budget Data Found in your Project. Please Contact your PM for Further Information.')
            #         else:
            #             pass
            #     else:
            #         raise ValidationError(
            #             'No Budget Data Found in your Project. Please Contact Finance Dept. for Further Information.')

            # else:
            #     # treasury budget
            #     data = self.env['account.fiscalyear'].sudo().search(
            #         [('date_start', '<=', self.date_travel), ('date_stop', '>=', self.date_travel)]).mapped('id')
            #     total_tour_amount = 0
            #     if self.cancellation_status is False and self.settlement_applied is False:
            #         total_tour_amount += self.total_budget_expense

            #     department_sec = self.env['kw_tour_treasury_budget'].sudo().search(
            #         [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.section.id),
            #          ('company_id', '=', self.employee_id.user_id.company_id.id)],
            #         limit=1)
            #     department_div = self.env['kw_tour_treasury_budget'].sudo().search(
            #         [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.division.id),
            #          ('company_id', '=', self.employee_id.user_id.company_id.id)],
            #         limit=1)
            #     department_dep = self.env['kw_tour_treasury_budget'].sudo().search(
            #         [('fiscal_year_id', 'in', data),
            #          ('department_id', '=', self.create_uid.employee_ids.department_id.id),
            #          ('company_id', '=', self.employee_id.user_id.company_id.id)],
            #         limit=1)
            #     if department_sec:
            #         if department_sec.remaining_amount < total_tour_amount:
            #             raise ValidationError(
            #                 'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
            #     elif department_div:
            #         if department_div.remaining_amount < total_tour_amount:
            #             raise ValidationError(
            #                 'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
            #     elif department_dep:
            #         if department_dep.remaining_amount < total_tour_amount:
            #             raise ValidationError(
            #                 'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
            #     else:
            #         raise ValidationError('No Budget Data Found. Please Contact Your PM/RA For Further Information.')

            # if self.budget_head_id and self.state == 'Draft':
            #     empl_id =  self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            #     emp_kw_id = empl_id.kw_id or 0
            #     project_url = self.env.ref('kw_tour.kw_tour_budget_url_system_parameter').sudo().value
            #     header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
            #     data = json.dumps({"userId": emp_kw_id, "BudgetHeadID": self.budget_head_id.kw_id})
            #     # print('response data>>>>>',data)
            #     resp_result = requests.post(project_url, headers=header, data=data)
            #     resp = json.loads(resp_result.text)
            #     budget_amount = 0
            #     if resp.get('retBudgetDa', False):
            #         if self.tour_type_id.code == 'project' and self.project_type == '70':
            #             if all(int(module_dict.get('ModuleID')) != self.project_id.kw_workorder_id for module_dict in
            #                    resp['retBudgetDa']):
            #                 raise ValidationError("No budget data found")
            #         else:
            #             if all(int(module_dict.get('Budget_Head_ID')) != self.budget_head_id.kw_id for module_dict in
            #                    resp['retBudgetDa']):
            #                 raise ValidationError("No budget data found")
            #         for module_dict in resp['retBudgetDa']:
            #             if self.tour_type_id.code == 'project' and self.project_type == '70':
            #                 if int(module_dict.get('ModuleID')) == self.project_id.kw_workorder_id:
            #                     budget_amount = module_dict.get('Total_BudgetAmt')
            #             elif self.tour_type_id.code == 'project' and self.project_type != '70':
            #                 budget_amount = module_dict.get('Total_BudgetAmt')
            #                 # print('budget_amount',budget_amount)
            #             elif self.tour_type_id.code != 'project':
            #                 budget_amount = module_dict.get('Total_BudgetAmt')
            #     elif self.tour_type_id.code in ['events', 'training','relocation', 'interviews']:
            #         pass
            #     else:
            #         raise ValidationError("No budget data found")
            #     if float(budget_amount) < 1 and tour.state in ('Draft', 'Applied') and self.tour_type_id.code not in ['events', 'training','relocation', 'interviews']:
            #         raise ValidationError("Insufficient Balance in budget")



                # if tour.state in ('Draft', 'Applied'):

                #     # settlement amount to deduct from budget amount
                #     total_settlement_amount = sum(self.env['kw_tour_settlement'].sudo().search(
                #         [('budget_head_id', '=', tour.budget_head_id.id),
                #          ('project_id', '=', tour.project_id.id), ('state', '!=', 'Rejected')]).mapped(
                #         'total_budget_expense'))

                #     # tours filtered of which settlement not applied except current record
                #     unsettled_tours = self.env['kw_tour'].sudo().search([('budget_head_id', '=', tour.budget_head_id.id),
                #                                                          ('project_id', '=', tour.project_id.id),
                #                                                          ('state', 'not in', ('Rejected', 'Cancelled'))]) - self
                #     unsettled_tour_amount = sum(unsettled_tours.filtered(
                #         lambda r: r.cancellation_status == False and r.settlement_applied == False).mapped(
                #         'total_budget_expense'))

                #     total_tour_amount = 0
                #     # current record amount
                #     if self.cancellation_status is False and self.settlement_applied is False:
                #         total_tour_amount += sum(
                #             self.travel_ticket_ids.filtered(lambda r: r.currency_id.name == 'INR').mapped('cost'))
                #         total_tour_amount += sum(
                #             self.travel_ticket_ids.filtered(lambda r: r.currency_id.name == 'USD').mapped(
                #                 'cost')) * self.api_exchange_rate
                #         total_tour_amount += sum(self.travel_expense_details_ids.mapped('amount_domestic'))
                #         total_tour_amount += sum(
                #             self.travel_expense_details_ids.mapped('amount_international')) * self.api_exchange_rate
                #         total_tour_amount += sum(
                #             self.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == 'INR').mapped(
                #                 'amount'))
                #         total_tour_amount += sum(
                #             self.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == 'USD').mapped(
                #                 'amount')) * self.api_exchange_rate
                #         total_tour_amount += sum(
                #             self.ancillary_expense_ids.filtered(lambda r: r.currency_id.name == 'INR').mapped('amount'))
                #         total_tour_amount += sum(
                #             self.ancillary_expense_ids.filtered(lambda r: r.currency_id.name == 'USD').mapped(
                #                 'amount')) * self.api_exchange_rate
                #         total_tour_amount += self.advance
                #         total_tour_amount += self.advance_usd * self.api_exchange_rate

                #     print('amount...', budget_amount, total_settlement_amount, unsettled_tour_amount, total_tour_amount)
                #     if tour.actual_project_id:
                #         total_amount_spent = float(total_settlement_amount) + float(unsettled_tour_amount)
                #         print('total_amount_spent',total_amount_spent)
                #         project_budget = self.env['kw_tour_project_budget'].sudo().search(
                #             [('project_id', '=', tour.project_id.id), ('budget_head_id', '=', tour.budget_head_id.id)],
                #             limit=1)
                #         threshold_amount = float(budget_amount) * project_budget.threshold_limit / 100
                #         print('threshold_amount--------------', total_amount_spent, threshold_amount)
                #         if total_amount_spent >= threshold_amount:
                #             raise ValidationError("Cannot apply tour\n"
                #                                   "Selected budget head has crossed threshold limit.\n"
                #                                   "Contact your project manager to increase budget")
                #     available_balance = float(budget_amount) - float(total_settlement_amount) - float(
                #         unsettled_tour_amount) - float(total_tour_amount)
                #     if available_balance < 1 and self.tour_type_id.code == 'project':
                #         raise ValidationError("Insufficient Balance in Budget")

                    # # USD
                    # settlement_amount_usd = 0
                    # if self.tour_type_id.code == 'project' and self.project_type == '70':
                    #     query_settlement = f'''select sum(total_international * api_exchange_rate)
                    #                            from kw_tour_settlement
                    #                            where state != 'Rejected' and total_international > 0
                    #                            and budget_head_id = ''' + str(self.budget_head_id.id) \
                    #                        + ''' and actual_project_id = ''' + str(self.actual_project_id.id)
                    #     self._cr.execute(query_settlement)
                    #     query_settlement_result = self._cr.dictfetchall()
                    #     if query_settlement_result[0].get('sum'):
                    #         settlement_amount_usd += query_settlement_result[0].get('sum')
                    # else:
                    #     query_settlement = f'''select sum(total_international * api_exchange_rate)
                    #                            from kw_tour_settlement
                    #                            where state != 'Rejected' and total_international > 0
                    #                            and budget_head_id = ''' + str(self.budget_head_id.id)
                    #     self._cr.execute(query_settlement)
                    #     query_settlement_result = self._cr.dictfetchall()
                    #     if query_settlement_result[0].get('sum'):
                    #         settlement_amount_usd += query_settlement_result[0].get('sum')
                    # if pending_settlement_tours:
                    #     # travel ticket
                    #     #     INR
                    #     self_tour = pending_settlement_tours.filtered(lambda r: r.travel_arrangement == 'Self')
                    #     p_amount_inr += sum(self.env['kw_tour_travel_ticket'].sudo().search(
                    #         [('tour_id', 'in', self_tour.ids), ('currency_id.name', '=', 'INR')]).mapped('cost'))
                    #     # USD
                    #     if self_tour:
                    #         ticket_query_condition = ' in ' + str(tuple(self_tour.ids))
                    #         if len(self_tour.ids) == 1:
                    #             ticket_query_condition = ' = ' + str(self_tour.id)
                    #         query_ticket = f'''select sum(kttt.cost * kt.api_exchange_rate)
                    #                            from kw_tour_travel_ticket kttt
                    #                            join kw_tour kt on kt.id = kttt.tour_id
                    #                            join res_currency rc on rc.id = kttt.currency_id
                    #                            where rc.name = 'USD' and kt.id ''' + ticket_query_condition
                    #         self._cr.execute(query_ticket)
                    #         query_ticket_result = self._cr.dictfetchall()
                    #         if query_ticket_result[0].get('sum'):
                    #             p_amount_usd += query_ticket_result[0].get('sum')
                    #
                    #     # travel expense
                    #     #         INR
                    #     p_amount_inr += sum(self.env['kw_tour_travel_expense_details'].sudo().search(
                    #         [('tour_id', 'in', pending_settlement_tours.ids)]).mapped('amount_domestic'))
                    #     # USD
                    #     travel_query_condition = ' in ' + str(tuple(pending_settlement_tours.ids))
                    #     if len(pending_settlement_tours.ids) == 1:
                    #         travel_query_condition = ' = ' + str(pending_settlement_tours.id)
                    #     query_travel = f'''select sum(ked.amount_international * kt.api_exchange_rate)
                    #                        from kw_tour_travel_expense_details ked
                    #                        join kw_tour kt on kt.id = ked.tour_id
                    #                        where kt.id ''' + travel_query_condition
                    #     self._cr.execute(query_travel)
                    #     query_travel_result = self._cr.dictfetchall()
                    #     if query_travel_result[0].get('sum'):
                    #         p_amount_usd += query_travel_result[0].get('sum')
                    #
                    #     # prerequisite
                    #     #             INR
                    #     p_amount_inr += sum(self.env['kw_tour_travel_prerequisite_details'].sudo().search(
                    #         [('tour_id', 'in', pending_settlement_tours.ids), ('currency_id.name', '=', 'INR')]).mapped(
                    #         'amount'))
                    #     # USD
                    #     prere_query_condition = ' in ' + str(tuple(pending_settlement_tours.ids))
                    #     if len(pending_settlement_tours.ids) == 1:
                    #         prere_query_condition = ' = ' + str(pending_settlement_tours.id)
                    #     query_prerequisite = f'''select sum(kpd.amount * kt.api_exchange_rate)
                    #                                from kw_tour_travel_prerequisite_details kpd
                    #                                join kw_tour kt on kt.id = kpd.tour_id
                    #                                join res_currency rc on rc.id = kpd.currency_id
                    #                                where rc.name = 'USD' and kt.id ''' + prere_query_condition
                    #     self._cr.execute(query_prerequisite)
                    #     query_prerequisite_result = self._cr.dictfetchall()
                    #     if query_prerequisite_result[0].get('sum'):
                    #         p_amount_usd += query_prerequisite_result[0].get('sum')
                    #     # ancillary expense
                    #     # INR
                    #     p_amount_inr += sum(self.env['kw_tour_ancillary_expense_details'].sudo().search(
                    #         [('tour_id', 'in', pending_settlement_tours.ids), ('currency_id.name', '=', 'INR')]).mapped(
                    #         'amount'))
                    #     # USD
                    #     ancillary_query_condition = ' in ' + str(tuple(pending_settlement_tours.ids))
                    #     if len(pending_settlement_tours.ids) == 1:
                    #         ancillary_query_condition = ' = ' + str(pending_settlement_tours.id)
                    #     query_ancillary = f'''select sum(kae.amount * kt.api_exchange_rate)
                    #                            from kw_tour_ancillary_expense_details kae
                    #                            join kw_tour kt on kt.id = kae.tour_id
                    #                            join res_currency rc on rc.id = kae.currency_id
                    #                            where rc.name = 'USD' and kt.id ''' + ancillary_query_condition
                    #     self._cr.execute(query_ancillary)
                    #     query_ancillary_result = self._cr.dictfetchall()
                    #     if query_ancillary_result[0].get('sum'):
                    #         p_amount_usd += query_ancillary_result[0].get('sum')
                    #     # advance
                    #     # INR
                    #     p_amount_inr += sum(
                    #         self.env['kw_tour'].sudo().search([('id', 'in', pending_settlement_tours.ids)]).mapped(
                    #             'advance'))
                    #     # USD
                    #     advance_query_condition = ' in ' + str(tuple(pending_settlement_tours.ids))
                    #     if len(pending_settlement_tours.ids) == 1:
                    #         advance_query_condition = ' = ' + str(pending_settlement_tours.id)
                    #     query_advance = f'''select sum(advance_usd * api_exchange_rate)
                    #                        from kw_tour where id ''' + advance_query_condition
                    #     self._cr.execute(query_advance)
                    #     query_advance_result = self._cr.dictfetchall()
                    #     if query_advance_result[0].get('sum'):
                    #         p_amount_usd += query_advance_result[0].get('sum')

    @api.multi
    def _compute_budget_limit_crossed(self):
        for record in self:
            record.budget_limit_crossed = False
            data = self.env['account.fiscalyear'].sudo().search([
                ('date_start', '<=', record.date_travel),
                ('date_stop', '>=', record.date_travel)
            ]).mapped('id')
            if record.project_id and record.budget_head_id:
                budget = self.env['kw_tour_project_budget'].sudo().search(
                    [('project_id', '=', record.project_id.id),
                     ('budget_head_id', '=', record.budget_head_id.id)],
                    limit=1)
                if budget.budget_perc > budget.threshold_limit:
                    record.budget_limit_crossed = True

    @api.depends('travel_arrangement', 'travel_ticket_ids', 'travel_expense_details_ids','tour_detail_ids','emp_budget_amount',
                 'travel_prerequisite_ids', 'ancillary_expense_ids', 'advance', 'advance_usd', 'api_exchange_rate')
    def _get_total_budget_expense(self):
        ticket_cost=sum(self.env['group_tour_ticket_config'].search([('company_id', '=', self.employee_id.user_id.company_id.id)]).mapped('ticket_price'))
        for record in self:
            p_amount_inr, p_amount_usd = 0, 0
            if record.travel_arrangement == 'Self':
                p_amount_inr += sum(
                    record.travel_ticket_ids.filtered(lambda r: r.currency_id.name == record.employee_id.user_id.company_id.currency_id.name).mapped('cost'))
                p_amount_usd += sum(
                    record.travel_ticket_ids.filtered(lambda r: r.currency_id.name == 'USD').mapped(
                        'cost')) * record.api_exchange_rate
            else:
                p_amount_inr += ticket_cost*len(record.tour_detail_ids)
            p_amount_inr += sum(record.travel_expense_details_ids.mapped('amount_domestic'))
            p_amount_usd += sum(
                record.travel_expense_details_ids.mapped('amount_international')) * record.api_exchange_rate
            p_amount_inr += sum(
                record.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == record.employee_id.user_id.company_id.currency_id.name).mapped('amount'))
            p_amount_usd += sum(
                record.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == 'USD').mapped(
                    'amount')) * record.api_exchange_rate
            p_amount_inr += sum(
                record.ancillary_expense_ids.filtered(lambda r: r.currency_id.name == record.employee_id.user_id.company_id.currency_id.name).mapped('amount'))
            p_amount_usd += sum(
                record.ancillary_expense_ids.filtered(lambda r: r.currency_id.name == 'USD').mapped(
                    'amount')) * record.api_exchange_rate
                    
            # p_amount_inr += sum(record.travel_expense_details_ids.mapped('user_input_amount_domestic'))
            # p_amount_usd += sum(record.travel_expense_details_ids.mapped('user_input_amount_international')) * record.api_exchange_rate

            p_amount_inr += record.advance
            p_amount_usd += record.advance_usd * record.api_exchange_rate
            # print(record.total_budget_expense, record.emp_budget_amount, p_amount_inr, p_amount_usd, '===========>>>>', record.user_budget_boolean)
            # print('===========1====>>>', record.currency_id, record.employee_id.user_id.company_id.currency_id.id)
            record.currency_id = record.employee_id.user_id.company_id.currency_id.id
            #
            # print('==========2=====>>>', record.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == 'USD').mapped(
            #         'amount'), record.api_exchange_rate)
            if record.user_budget_boolean == True:
                # print('if   ')
                record.total_budget_expense = float(record.emp_budget_amount)
            else:
                # print('else---')
                record.total_budget_expense = p_amount_inr + p_amount_usd

    @api.onchange('tour_type_id', 'project_type')
    def _onchange_project(self):
        domain = {'budget_head_id': [('tour_type', '=', 'Other')]}
        if self.tour_type_id and self.tour_type_id.code == 'project':
            self.project = True
            self.budget_head_id = False
            if self.project_type == '70':
                domain['budget_head_id'] = [('tour_type', '=', 'Project')]
        else:
            self.project = False
            self.project_type = False
            self.project_id = False
            self.budget_head_id = False
        return {'domain': domain}

    @api.multi
    def action_cancel_tour(self):
        ''' if state is not approved then change to cancelled,
            if state is approved then it will follow the approval process '''
        if self.state in ('Draft', 'Applied'):
            self._compute_project_budget()
            # t_value = self.env['kw_tour_treasury_budget'].sudo().search([('department_id', '=', self.department_id.id)])
            # t_value.write({
            #     'spent_amount': t_value.spent_amount - self.total_budget_expense,
            # })
            self.write({'state':'Cancelled'})
            self.env.user.notify_success("Tour Cancelled Successfully.")

        else:
            # open tour cancellation form view
            form_view_id = self.env.ref('kw_tour.view_kw_tour_cancellation_form').id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_tour_cancellation',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'self',
                'flags': {"toolbar": False},
                'context': {'default_tour_id': self.id}
            }

    def get_tour_data(self, start_date, end_date):
        data = {}
        tours = self.search(['&', ('state', 'in', ['Approved', 'Traveldesk Approved', 'Finance Approved']),
                             '|',
                             '|', '&', ('date_travel', '<=', start_date), ('date_return', '>=', start_date),
                             '|', '&', ('date_travel', '<=', end_date), ('date_return', '>=', end_date), '&',
                                ('date_travel', '<=', start_date), ('date_return', '>=', end_date),
                             '|', '&', ('date_travel', '>=', start_date), ('date_travel', '<=', end_date), '&',
                                ('date_return', '>=', start_date), ('date_return', '<=', end_date)
                             ])
        employees = tours.mapped('employee_id')
        for emp in employees:
            data[emp.id] = {tour_date: False for tour_date in self.generate_days_with_from_and_to_date(start_date, end_date)}
            emp_tours = tours.filtered(lambda r: r.employee_id == emp).sorted(key=lambda r: r.date_travel)
            for tour in emp_tours:
                for emp_date in self.generate_days_with_from_and_to_date(tour.date_travel, tour.date_return):
                    if emp_date in data[emp.id]:
                        data[emp.id][emp_date] = True
        return data

    @api.multi
    def action_advance_request_tour(self):
        settlement_pending = self.validate_tour_advance_process()
        if settlement_pending:
            raise ValidationError(f"Settlement is pending for tour {settlement_pending[0].code}. Hence you can't apply advance.")

        form_view_id = self.env.ref('kw_tour.view_kw_tour_advance_request_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_advance_request',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'self',
            'flags': {"toolbar": False, 'mode': 'edit'},
            'context': {'default_tour_id': self.id}
        }
    
    @api.multi
    def action_reschedule_tour(self):
        ''' Open current tour in draft mode to apply a new tour.
            write date_travel , date_return to old_date_travel and old_date_return to maintain history.
            update attendance related records to is_on_tour': False 
            maintain travel details in chatter.
        '''
        tour_state = self.state
        travel_date = self.date_travel
        return_date = self.date_return
        reschedule_count = self.reschedule_count and self.reschedule_count + 1 or 1
        self.write({'state': 'Draft',
                    'status': 'Rescheduled',
                    'old_date_travel': travel_date,
                    'old_date_return': return_date,
                    'reschedule_count': reschedule_count,
                    'reschedule_log_ids': [[0, 0, {
                                            'date_travel': travel_date,
                                            'date_return': return_date,
                                            'reschedule_count': reschedule_count,
                                            'detail_ids': [[0, 0, {
                                                        "from_date": detail.from_date,
                                                        "from_time": detail.from_time,
                                                        "from_city_id": detail.from_city_id and detail.from_city_id.id or False,

                                                        "to_date": detail.to_date,
                                                        "to_time": detail.to_time,
                                                        "to_city_id": detail.to_city_id and detail.to_city_id.id or False,

                                                        "travel_arrangement": detail.travel_arrangement,
                                                        "accomodation_arrangement": detail.accomodation_arrangement,

                                                        "travel_mode_id": detail.travel_mode_id and detail.travel_mode_id.id or False,
                                                        "currency_id": detail.currency_id and detail.currency_id.id or False,
                                                        "cost": detail.cost,
                                                        "document": detail.document
                                                    }] for detail in self.tour_detail_ids]
                                            }]],
                    'action_log_ids': [[0, 0, {'remark': 'Tour Rescheduled', 'state': 'Draft'}]]
                })
        # user_timezone = pytz.timezone(self.env.user.tz or 'UTC')

        # Start : update attendance related records to false
        # if tour_state in ['Finance Approved','Posted']:
        tour_dates = self.generate_days_with_from_and_to_date(travel_date, return_date)
        attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                                    ('attendance_recorded_date', 'in', tour_dates)])
        for record in attendance_records:
            if record.is_on_tour != False:
                try:
                    record.write({'is_on_tour': False})
                except Exception as e:
                    # print(e)
                    continue
        # End : update attendance related records to false'''

        message = '''<p>Old Tour Details.</p>
                    <table border="1" style="width:100%;">
                    <tr align="center">
                    <th>From Date</th>
                    <th>From Time</th>
                    <th>From Country</th>
                    <th>From City</th>
                    <th>To Date</th>
                    <th>To Time</th>
                    <th>To Country</th>
                    <th>To City</th>
                    </tr>'''
        for data in self.tour_detail_ids:
            # from_date = data.from_date.astimezone(user_timezone) ${datetime.datetime.strptime(object.to_time,"%H:%M:%S").strftime("%I:%M %p")}
            # to_date = data.to_date.astimezone(user_timezone)
            from_date = data.from_date.strftime('%d-%b-%Y')
            to_date = data.to_date.strftime('%d-%b-%Y')
            from_time = data.from_time and datetime.strptime(data.from_time,"%H:%M:%S").strftime("%I:%M %p") or ''
            to_time = data.to_time and datetime.strptime(data.to_time,"%H:%M:%S").strftime("%I:%M %p") or ''

            # message += f"<tr align='center'><td>{from_date.strftime('%d-%b-%Y %I:%M %p')}</td> <td>{data.from_country_id.name} </td> <td>{data.from_city_id.name}</td> <td>{to_date.strftime('%d-%b-%Y %I:%M %p')} </td> <td>{data.to_country_id.name} </td> <td>{data.to_city_id.name}</td></tr>"

            message += f"<tr align='center'><td>{from_date}</td><td>{from_time}</td> <td>{data.from_country_id.name} </td> <td>{data.from_city_id.name}</td> <td>{to_date} </td><td>{to_time} </td> <td>{data.to_country_id.name} </td> <td>{data.to_city_id.name}</td></tr>"
        message += '</table>'
        self.message_post(body=message)
        form_view_id = self.env.ref('kw_tour.view_kw_tour_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.ids[0],
            'target': 'self',
            'flags': {"toolbar": False, 'mode': 'edit'},
        }

    @api.multi
    def action_confirm_reschedule(self):
        form_view_id = self.env.ref('kw_tour.kw_tour_reschedule_confirmation_view').id
        return  {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'view_id':form_view_id,
            'res_id': self.id,
            'domain': [('id', '=', self.id)]
        }

    @api.onchange('acc_arrange')
    def change_accomodation_details(self):
        if self.acc_arrange:
            if self.acc_arrange == 'Company' and self.state in ['Draft', 'Applied']:
                self.accomodation_ids = False
        else:
            self.accomodation_ids = False

    @api.onchange('tour_detail_ids')
    def set_expenses(self):
        from_cities = self.tour_detail_ids.mapped('from_city_id')
        to_cities = self.tour_detail_ids.mapped('to_city_id')

        all_cities = from_cities | to_cities

        expenses = self.env['kw_tour_expense_type'].search([])

        city_dict = {city.id: 0 for city in all_cities}
        city_halt_dict = {city.id: 0 for city in all_cities}

        days_expense_dict = {expen.id: {"inr": 0, "usd": 0} for expen in expenses}

        # user_timezone = pytz.timezone(self.env.user.tz or 'UTC')

        for index,detail in enumerate(self.tour_detail_ids,start=1):
            
            from_date = detail.from_date #.astimezone(user_timezone).date()
            to_date = detail.to_date #.astimezone(user_timezone).date()

            if index ==1:
                city_dict[detail.to_city_id.id] += (to_date - from_date).days + 1
            else:
                date_gape_with_prev_date = (from_date - prev_date).days
                date_gape_with_next_date = (to_date - from_date).days

                city_dict[prev_city] += date_gape_with_prev_date
                city_dict[detail.to_city_id.id] += date_gape_with_next_date

                # if prev_rec.accomodation_arrangement == "Self":
                city_halt_dict[prev_city] += date_gape_with_prev_date

            prev_date = to_date
            prev_city = detail.to_city_id.id
            prev_rec = detail
            
        self.city_days_spend_ids = False
        self.city_days_spend_ids = [[0, 0, {'city_id': key, 'no_of_nights': value,'actual_no': value}] for key, value in city_dict.items() if value >0]

        expense_data = {expense.id: {'amount_domestic': 0, 'amount_international':0, 'currency_domestic': 0, 'currency_international':0} for expense in expenses}
        hardship_expense = self.env.ref('kw_tour.kw_tour_expense_type_ha')
        hra_expense = self.env.ref('kw_tour.kw_tour_expense_type_hra')
        employee = self.employee_id

        # added for RA and Travel desk and other approvals
        if self._context.get('default_tour_id'):
            tour = self.env['kw_tour'].browse(self._context.get('default_tour_id'))
            if tour and tour.employee_id:
                employee = tour.employee_id
                # print(employee.user_id.company_id.currency_id.name, '============>>')
        # added for RA and Travel desk and other approvals
        effective_from = date(2022, 12, 26)
        i_class_effective_from = date(2023, 7, 1)
        for city in all_cities.filtered(lambda r: city_dict[r.id] > 0):
            if city.classification_type_id.name.upper().startswith('I'):
                if i_class_effective_from <= self.date_travel:
                    # print('if satisfied-----1--------------->>>')
                    emp_level = self.env['kwemp_grade_master'].search([('id', 'in', employee.grade.ids)], limit=1)
                    # print('employee_grade_master', emp_level)
                    '''check if city is under domestic or international '''
                    # print(city.classification_type_id.name, '========2========>>>>>')
                    for exp in expenses:
                        domestic_rec = city.expense_ids.filtered(
                            lambda r: r.expense_type_id == exp and emp_level.id in r.employee_grade_id.ids)

                        if exp == hra_expense:
                            if city_halt_dict[city.id] > 0:
                                ''' calculate HRA '''
                                if domestic_rec and domestic_rec.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                    expense_data[exp.id]['amount_domestic'] += city_halt_dict[
                                                                                   city.id] * domestic_rec.amount or 0
                                    expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                                    days_expense_dict[exp.id]['inr'] += city_halt_dict[city.id]

                                elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                    expense_data[exp.id]['amount_international'] += city_halt_dict[
                                                                                        city.id] * domestic_rec.amount or 0
                                    expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                    days_expense_dict[exp.id]['usd'] += city_halt_dict[city.id]

                        elif exp == hardship_expense:
                            if city.ha_eligible:
                                '''calculate hardship'''
                                corresponding_exp = city.expense_type_id
                                # print('corressponding_exp>>>', corresponding_exp)
                                exp_record = city.expense_ids.filtered(
                                    lambda
                                        r: r.expense_type_id == corresponding_exp and emp_level.id in r.employee_grade_id.ids)
                                # print('exp_record>>>>>>>>>', exp_record)

                                if exp_record and exp_record.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                    amount = (exp_record.amount) * city.eligibility_percent / 100
                                    expense_data[hardship_expense.id]['amount_domestic'] += city_dict[city.id] * amount or 0
                                    expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                                    days_expense_dict[hardship_expense.id]['inr'] += city_dict[city.id]

                                elif exp_record and exp_record.currency_type_id.name == "USD":
                                    amount = (exp_record.amount) * city.eligibility_percent / 100
                                    expense_data[hardship_expense.id]['amount_international'] += city_dict[
                                                                                                     city.id] * amount or 0
                                    expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                    days_expense_dict[hardship_expense.id]['usd'] += city_dict[city.id]

                        else:
                            '''regular calculation '''
                            # print(domestic_rec, '==============>>', domestic_rec.currency_type_id.name,
                            #       self.env.user.company_id.currency_id.name)
                            if domestic_rec and domestic_rec.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                expense_data[exp.id]['amount_domestic'] += city_dict[city.id] * domestic_rec.amount or 0
                                expense_data[exp.id]['currency_domestic'] = domestic_rec.currency_type_id.id
                                days_expense_dict[exp.id]['inr'] += city_dict[city.id]
                            elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                expense_data[exp.id]['amount_international'] += city_dict[
                                                                                    city.id] * domestic_rec.amount or 0
                                expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                days_expense_dict[exp.id]['usd'] += city_dict[city.id]
                else:
                    # print('else satisfied-------3----------------->>>')
                    emp_level = self.env['kw_grade_level'].search([('grade_ids', 'in', employee.grade.ids)], limit=1)
                    # print('emp_level_master', emp_level)
                    # for city in all_cities.filtered(lambda r: city_dict[r.id] > 0):
                    '''check if city is under domestic or international '''
                    for exp in expenses:
                        domestic_rec = city.expense_ids.filtered(
                            lambda r: r.expense_type_id == exp and not r.employee_grade_id)
                        if exp == hra_expense:
                            if city_halt_dict[city.id] > 0:
                                ''' calculate HRA '''
                                if domestic_rec and domestic_rec.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                    expense_data[exp.id]['amount_domestic'] += city_halt_dict[
                                                                                   city.id] * domestic_rec.amount or 0
                                    expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                                    days_expense_dict[exp.id]['inr'] += city_halt_dict[city.id]

                                elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                    expense_data[exp.id]['amount_international'] += city_halt_dict[
                                                                                        city.id] * domestic_rec.amount or 0
                                    expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                    days_expense_dict[exp.id]['usd'] += city_halt_dict[city.id]

                        elif exp == hardship_expense:
                            if city.ha_eligible:
                                '''calculate hardship'''
                                corresponding_exp = city.expense_type_id
                                exp_record = city.expense_ids.filtered(
                                    lambda r: r.expense_type_id == corresponding_exp and not r.employee_grade_id)

                                if exp_record and exp_record.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                    amount = (exp_record.amount) * city.eligibility_percent / 100
                                    expense_data[hardship_expense.id]['amount_domestic'] += city_dict[
                                                                                                city.id] * amount or 0
                                    expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                                    days_expense_dict[hardship_expense.id]['inr'] += city_dict[city.id]

                                elif exp_record and exp_record.currency_type_id.name == "USD":
                                    amount = (exp_record.amount) * city.eligibility_percent / 100
                                    expense_data[hardship_expense.id]['amount_international'] += city_dict[
                                                                                                     city.id] * amount or 0
                                    expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                    days_expense_dict[hardship_expense.id]['usd'] += city_dict[city.id]
                        else:
                            '''regular calculation '''
                            # print(domestic_rec, '==============>>', domestic_rec.currency_type_id.name,
                            #       self.env.user.company_id.currency_id.name)
                            if domestic_rec and domestic_rec.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                expense_data[exp.id]['amount_domestic'] += city_dict[city.id] * domestic_rec.amount or 0
                                expense_data[exp.id]['currency_domestic'] = domestic_rec.currency_type_id.id
                                days_expense_dict[exp.id]['inr'] += city_dict[city.id]
                            elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                expense_data[exp.id]['amount_international'] += city_dict[
                                                                                    city.id] * domestic_rec.amount or 0
                                expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                days_expense_dict[exp.id]['usd'] += city_dict[city.id]

            elif self.date_travel and effective_from <= self.date_travel:
                # print('if satisfied-----4--------------->>>')
                emp_level = self.env['kwemp_grade_master'].search([('id', 'in', employee.grade.ids)], limit=1)
                # print('employee_grade_master',emp_level)
                # for city in all_cities.filtered(lambda r: city_dict[r.id] > 0):
                '''check if city is under domestic or international '''
                # print(city, '=====5===========>>>>>')
                for exp in expenses:
                    domestic_rec = city.expense_ids.filtered(
                        lambda r: r.expense_type_id == exp and emp_level.id in r.employee_grade_id.ids)

                    if exp == hra_expense:
                        if city_halt_dict[city.id] >0:
                            ''' calculate HRA '''
                            if domestic_rec and domestic_rec.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                expense_data[exp.id]['amount_domestic'] += city_halt_dict[city.id] * domestic_rec.amount or 0
                                expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                                days_expense_dict[exp.id]['inr'] += city_halt_dict[city.id]

                            elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                expense_data[exp.id]['amount_international'] += city_halt_dict[city.id] * domestic_rec.amount or 0
                                expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                days_expense_dict[exp.id]['usd'] += city_halt_dict[city.id]

                    elif exp == hardship_expense:
                        if city.ha_eligible:
                            '''calculate hardship'''
                            corresponding_exp = city.expense_type_id
                            # print('corressponding_exp>>>',corresponding_exp)
                            exp_record = city.expense_ids.filtered(
                                lambda r: r.expense_type_id == corresponding_exp and emp_level.id in r.employee_grade_id.ids)
                            # print('exp_record>>>>>>>>>',exp_record)

                            if exp_record and exp_record.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                amount = (exp_record.amount) * city.eligibility_percent/100
                                expense_data[hardship_expense.id]['amount_domestic'] += city_dict[city.id] * amount or 0
                                expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                                days_expense_dict[hardship_expense.id]['inr'] += city_dict[city.id]

                            elif exp_record and exp_record.currency_type_id.name == "USD":
                                amount = (exp_record.amount) * city.eligibility_percent/100
                                expense_data[hardship_expense.id]['amount_international'] += city_dict[city.id] * amount or 0
                                expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                days_expense_dict[hardship_expense.id]['usd'] += city_dict[city.id]

                    else:
                        '''regular calculation '''
                        # print(domestic_rec, '======domasticcc========>>', domestic_rec.currency_type_id.name, self.env.user.company_id.currency_id.name)
                        if domestic_rec and domestic_rec.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                            expense_data[exp.id]['amount_domestic'] += city_dict[city.id] * domestic_rec.amount or 0
                            expense_data[exp.id]['currency_domestic'] = domestic_rec.currency_type_id.id
                            days_expense_dict[exp.id]['inr'] += city_dict[city.id]

                        elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                            expense_data[exp.id]['amount_international'] += city_dict[city.id] * domestic_rec.amount or 0
                            expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                            days_expense_dict[exp.id]['usd'] += city_dict[city.id]

            else :
                # print('else satisfied-----6--------------->>>')
                emp_level = self.env['kw_grade_level'].search([('grade_ids', 'in', employee.grade.ids)], limit=1)
                # print('emp_level_master',emp_level)
                # for city in all_cities.filtered(lambda r: city_dict[r.id] > 0):
                '''check if city is under domestic or international '''

                for exp in expenses:
                    domestic_rec = city.expense_ids.filtered(
                        lambda r: r.expense_type_id == exp and not r.employee_grade_id)
                    if exp == hra_expense:
                        if city_halt_dict[city.id] >0:
                            ''' calculate HRA '''
                            if domestic_rec and domestic_rec.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                expense_data[exp.id]['amount_domestic'] += city_halt_dict[city.id] * domestic_rec.amount or 0
                                expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                                days_expense_dict[exp.id]['inr'] += city_halt_dict[city.id]

                            elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                expense_data[exp.id]['amount_international'] += city_halt_dict[city.id] * domestic_rec.amount or 0
                                expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                days_expense_dict[exp.id]['usd'] += city_halt_dict[city.id]

                    elif exp == hardship_expense:
                        if city.ha_eligible:
                            '''calculate hardship'''
                            corresponding_exp = city.expense_type_id
                            exp_record = city.expense_ids.filtered(
                                lambda r: r.expense_type_id == corresponding_exp and not r.employee_grade_id)

                            if exp_record and exp_record.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                                amount = (exp_record.amount) * city.eligibility_percent/100
                                expense_data[hardship_expense.id]['amount_domestic'] += city_dict[city.id] * amount or 0
                                expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                                days_expense_dict[hardship_expense.id]['inr'] += city_dict[city.id]

                            elif exp_record and exp_record.currency_type_id.name == "USD":
                                amount = (exp_record.amount) * city.eligibility_percent/100
                                expense_data[hardship_expense.id]['amount_international'] += city_dict[city.id] * amount or 0
                                expense_data[exp.id]['currency_international'] = domestic_rec.currency_type_id.id
                                days_expense_dict[hardship_expense.id]['usd'] += city_dict[city.id]

                    else:
                        '''regular calculation '''
                        # print(domestic_rec, '==============>>', domestic_rec.currency_type_id.name,
                        #       self.env.user.company_id.currency_id.name)
                        if domestic_rec and domestic_rec.currency_type_id.name == employee.user_id.company_id.currency_id.name:
                            expense_data[exp.id]['amount_domestic'] += city_dict[city.id] * domestic_rec.amount or 0
                            expense_data[exp.id]['currency_domestic'] += domestic_rec.currency_type_id.id
                            days_expense_dict[exp.id]['inr'] += city_dict[city.id]
                        elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                            expense_data[exp.id]['amount_international'] += city_dict[
                                                                                city.id] * domestic_rec.amount or 0
                            expense_data[exp.id]['currency_international'] += domestic_rec.currency_type_id.id
                            days_expense_dict[exp.id]['usd'] += city_dict[city.id]

        self.travel_expense_details_ids = False
        self.travel_expense_details_ids = [[0, 0,{
                'expense_id': expense,
                'amount_domestic': expense_data[expense]['amount_domestic'],
                'amount_international': expense_data[expense]['amount_international'],
                'no_of_night_inr':days_expense_dict[expense]['inr'],
                'no_of_night_usd':days_expense_dict[expense]['usd'],
                'currency_domestic':expense_data[expense]['currency_domestic'],
                'currency_international':expense_data[expense]['currency_international'],
                }] for expense in expense_data if any([expense_data[expense]['amount_domestic'], expense_data[expense]['amount_international']])]

    @api.multi
    def _compute_project(self):
        for rec in self:
            if rec.tour_type_id.code == 'project':
                rec.project = True

    @api.depends('project_id')
    def _compute_get_project(self):
        for rec in self:
            rec.actual_project_id = False
            if rec.tour_type_id.code == 'project' and rec.project_id:
                project_record = self.env['project.project'].sudo().search(
                    [('crm_id', '=', rec.project_id.id), ('active', '=', True)])
                if project_record:
                    rec.actual_project_id = project_record.id

    @api.model
    def create(self, values):
        values['code'] = self.env['ir.sequence'].sudo().next_by_code('self.tour_seq') or 'New'
        tour = super(Tour, self).create(values)
        # removed on 22 March 2021
        # status          = self.env['kw_tour'].sudo().search([('create_uid', '=' ,self._uid),('state', 'in', ['Draft','Applied', 'Approved'])]) - tour
        # if status:
        #     raise ValidationError(f'''There is already a tour in {status[0].state} state.
        #                                 Hence you can't apply a new tour.
        #                                 Make sure any tour is not in following state before applying a new tour.\n
        #                                 1.Draft
        #                                 2.Applied
        #                                 3.Approved''')
        self.env.user.notify_success("Tour created successfully.")
        return tour
    
    @api.multi
    def compute_ra_access(self):
        for tour in self:
            approver = tour._get_tour_approver()
            # if tour.employee_id and tour.employee_id.parent_id and tour.employee_id.parent_id.user_id == self.env.user:
            if tour.employee_id and approver and approver.user_id == self.env.user:
                tour.ra_access = True

    @api.multi
    def _compute_approve(self):
        for record in self:
            if self.env.user.has_group('kw_tour.group_kw_tour_admin'):
                record.admin_access = True
            if self.env.user.has_group('kw_tour.group_kw_tour_travel_desk'):
                record.travel_desk_access = True
            if self.env.user.has_group('kw_tour.group_kw_tour_finance'):
                record.finance_access = True

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None, is_integrated=False):
        # print("_search called")
        if not is_integrated:
            # print('is_integrated',is_integrated)
            # current_employee_id = self.env.user.employee_ids
            current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
            query = f'''select kt.id from kw_tour kt
                        join project_project pj on pj.id = kt.actual_project_id
                        where pj.emp_id = kt.employee_id 
                        and pj.reviewer_id = {current_employee.id}::integer '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            tour_reviewer_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select kt.id from kw_tour kt
                        join project_project pj on pj.id = kt.actual_project_id
                        where pj.reviewer_id = kt.employee_id '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            tour_ra_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select kt.id from kw_tour kt
                        join project_project pj on pj.id = kt.actual_project_id
                        where pj.reviewer_id != kt.employee_id and pj.emp_id != kt.employee_id 
                        and pj.emp_id = {current_employee.id}::integer '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            tour_pm_ids = [id_tuple[0] for id_tuple in query_result]
            if self._context.get('access_label_check'):
                if self.env.user.has_group('kw_tour.group_kw_tour_travel_desk'):
                    args += ['&',
                             '|', ('cancellation_id', '=', False), ('cancellation_id.state', 'not in', ['Applied', 'Approved']),
                             '|', ('state', '=', 'Approved'),
                             '|', '|', '|',
                                 '&', ('state', '=', 'Forwarded'), ('final_approver_id.user_id', '=', self.env.user.id),

                                 '&', '&', ('state', '=', 'Applied'), ('employee_id.parent_id.user_id', '=', self.env.user.id),
                                           '|',
                                           ('tour_type_id.code', '!=', 'project'),
                                           '&',
                                           ('tour_type_id.code', '=', 'project'),
                                           '|',
                                           ('id', 'in', tour_ra_ids),
                                           ('project_type', '=', '3'),

                                 '&', '&', '&', ('state', '=', 'Applied'),
                                           ('tour_type_id.code', '=', 'project'),
                                           ('create_uid', '!=', self.env.user.id),
                                           ('id', 'in', tour_pm_ids),

                                 '&', '&', ('state', '=', 'Applied'),
                                           ('tour_type_id.code', '=', 'project'),
                                           ('id', 'in', tour_reviewer_ids)
                             ]

                elif self.env.user.has_group('kw_tour.group_kw_tour_finance'):
                    args += ['&',
                             '|', ('cancellation_id', '=', False), ('cancellation_id.state', 'not in', ['Applied', 'Approved']),
                             '|', ('state', '=', 'Traveldesk Approved'),
                             '|', '|', '|',
                                 '&', ('state', '=', 'Forwarded'), ('final_approver_id.user_id', '=', self.env.user.id),

                                 '&', '&', ('state', '=', 'Applied'), ('employee_id.parent_id.user_id', '=', self.env.user.id),
                                           '|',
                                           ('tour_type_id.code', '!=', 'project'),
                                           '&',
                                           ('tour_type_id.code', '=', 'project'),
                                           '|',
                                           ('id', 'in', tour_ra_ids),
                                           ('project_type', '=', '3'),

                                 '&', '&', '&', ('state', '=', 'Applied'),
                                           ('tour_type_id.code', '=', 'project'),
                                           ('create_uid', '!=', self.env.user.id),
                                           ('id', 'in', tour_pm_ids),

                                 '&', '&', ('state', '=', 'Applied'),
                                           ('tour_type_id.code', '=', 'project'),
                                           ('id', 'in', tour_reviewer_ids)
                             ]
                else:
                    args += ['&',
                             '|', ('cancellation_id', '=', False), ('cancellation_id.state', 'not in', ['Applied', 'Approved']),
                             '|', '|', '|',
                                 '&', ('state', '=', 'Forwarded'), ('final_approver_id.user_id', '=', self.env.user.id),

                                 '&', '&', ('state', '=', 'Applied'), ('employee_id.parent_id.user_id', '=', self.env.user.id),
                                           '|',
                                           ('tour_type_id.code', '!=', 'project'),
                                           '&',
                                           ('tour_type_id.code', '=', 'project'),
                                           '|',
                                           ('id', 'in', tour_ra_ids),
                                           ('project_type', '=', '3'),

                                 '&', '&', ('state', '=', 'Applied'),
                                           ('tour_type_id.code', '=', 'project'),
                                           ('id', 'in', tour_pm_ids),

                                 '&', '&', ('state', '=', 'Applied'),
                                           ('tour_type_id.code', '=', 'project'),
                                           ('id', 'in', tour_reviewer_ids)
                             ]

            if self._context.get('filter_tour'):
                if self.env.user.has_group('kw_tour.group_kw_tour_travel_desk') \
                        or self.env.user.has_group('kw_tour.group_kw_tour_finance') \
                        or self.env.user.has_group('kw_tour.group_kw_tour_admin'):
                    args += [('state', '!=', 'Draft')]
                else:
                    args += ['&', ('state', '!=', 'Draft'),
                             '|', '|', '|', ('create_uid', '=', self.env.user.id),
                             '&',
                             ('employee_id.parent_id.user_id', '=', self.env.user.id),
                             '|',
                             ('tour_type_id.code', '!=', 'project'),
                             '&',
                             ('tour_type_id.code', '=', 'project'),
                             '|',
                             ('id', 'in', tour_ra_ids),
                             ('project_type', '=', '3'),

                             '&',
                             ('tour_type_id.code', '=', 'project'),
                             ('id', 'in', tour_pm_ids),

                             '&',
                             ('tour_type_id.code', '=', 'project'),
                             ('id', 'in', tour_reviewer_ids)]

        return super(Tour, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.multi
    def button_take_action(self):
        view_id = self.env.ref('kw_tour.view_kw_tour_take_action_form').id
        target_id = self.id
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
        }

    # Cron for settlement remind
    @api.model
    def remind_settlements(self):
        current_date = date.today()

        unsettled_tours = self.search([('state', '=', 'Finance Approved'), ('employee_id.active', '=', True)])
        pending_settlement_tours = unsettled_tours.filtered(lambda r: (current_date - r.date_return).days >= 5 and (
                    r.cancellation_status == False and r.settlement_applied == False))

        template = self.env.ref('kw_tour.kw_tour_settlement_reminder_mail')
        for tour in pending_settlement_tours:
            approver = tour._get_tour_approver()
            restrict_emp_ids = literal_eval(
                self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_approval_email_ids') or "[]")
            email_cc_users = ''
            if approver:
                approver -= approver.filtered(lambda r: r.id in restrict_emp_ids)
                if approver:
                    email_cc_users = approver.work_email
            template.with_context(email_cc_users=email_cc_users).send_mail(tour.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        # Remind to book return date before 2 and 5 days of return
        date_after_5_days = current_date + timedelta(days=5)
        date_after_2_days = current_date + timedelta(days=2)

        ticket_booking_tours = self.search([('state', 'in', ['Approved', 'Traveldesk Approved', 'Finance Approved']),
                                            ('date_return', 'in', [date_after_5_days, date_after_2_days]),
                                            ('employee_id.active', '=', True)])

        travel_desk_users = self.env.ref('kw_tour.group_kw_tour_travel_desk').users
        if travel_desk_users:

            mail_template = self.env.ref('kw_tour.kw_tour_return_date_notification_email_template')
            user_names = ','.join(travel_desk_users.mapped('name'))
            emails = ','.join(travel_desk_users.mapped('employee_ids.work_email'))

            for tour in ticket_booking_tours.filtered(lambda r: r.cancellation_status == False and not set(r.settlement_ids.mapped('state')) - {'Draft',
                                                                                                              'Rejected'}):
                mail_template.with_context(users=user_names, emails=emails).send_mail(
                    tour.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    # @api.model
    # def auto_forward_pending_actions(self):
    #     current_datetime            = datetime.now()

    #     #upper RA tour ra approve
    #     pending_at_ra_days = int(self.env['ir.config_parameter'].sudo().get_param('ra_pending_days'))
    #     pending_at_upper_ra_days = int(self.env['ir.config_parameter'].sudo().get_param('ra_pending_days'))

    #     ra_settlement           = self.env['kw_tour_settlement'].search([('pending_status_at', '=', 'RA'),('state','=','Applied')])
    #     upper_ra_settlement     = self.env['kw_tour_settlement'].search([('pending_status_at', '=', 'UA'),('state','=','Applied')])
        
    #     ra_pending_days_over        = ra_settlement.filtered(lambda r:(current_datetime - r.action_datetime).days >= pending_at_ra_days)
    #     ua_pending_days_over  = upper_ra_settlement.filtered(lambda r:(current_datetime - r.upper_ra_switched_datetime).days >= pending_at_upper_ra_days)

    #     for settlement in ra_pending_days_over:
    #         if settlement.employee_id.parent_id and settlement.employee_id.parent_id.parent_id:
    #             upper_ra_id = settlement.employee_id.parent_id.parent_id
    #             settlement.write(
    #                 {'pending_status_at':'UA',
    #                 'upper_ra_switched_datetime':current_datetime,
    #                 'upper_ra_id':upper_ra_id.id,
    #                 'action_datetime':Datetime.now(),
    #                 'approver_id': False,
    #                 'remark': False,
    #                 'final_approver_id': False,
    #                 'action_log_ids': [[0, 0, {'remark': f'Auto Forwarded to upper ra ({upper_ra_id.name}) By System','state': 'Applied'}]]
    #                 }
    #                 )
    #         else:
    #             settlement.write(
    #                 {'state': 'Approved',
    #                  'pending_status_at': False,
    #                 'approver_id': False,
    #                 'remark': False,
    #                 'final_approver_id': False,
    #                 'action_datetime':Datetime.now(),
    #                 'action_log_ids': [[0, 0, {'remark': 'Auto Approved By System','state': 'Applied'}]]
    #                 }
    #             )

    #     for settlement in ua_pending_days_over:
    #         ra = settlement.employee_id.parent_id and settlement.employee_id.parent_id.id or False
    #         ra_name = settlement.employee_id.parent_id and settlement.employee_id.parent_id.name or ''
    #         settlement.write({
    #             'pending_status_at':'RA',
    #             'upper_ra_switched_datetime':False,
    #             'upper_ra_id':False,
    #             'action_datetime':Datetime.now(),
    #             'approver_id': False,
    #             'remark': False,
    #             'final_approver_id': ra,
    #             'action_log_ids': [[0, 0, {'remark': f'Auto Backward to RA ({ra_name}) By System', 'state': 'Applied'}]]
    #                 })

    @api.model
    def remind_pending_actions(self):
        '''
        take action reminder for tour
        take action reminder for settlement 10 march 2021 (gouranga)
        '''
        # Start : Tour pending action code
        current_datetime = datetime.now()
        pending_tours = self.search([('state', 'in', ['Applied', 'Approved', 'Forwarded', 'Traveldesk Approved'])])
        maximum_pending_tarveldesk_days = int(self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_maximum_pending_days'))

        if pending_tours:
            mail_template = self.env.ref('kw_tour.kw_tour_pending_action_email_template')
        #     # RA_pending_tours = pending_tours.filtered(lambda r:r.state == 'Applied' and r.pending_status_at == 'RA')

        #     # Email for non-project and project tour pending at RA
        #     RA_pending_tours = pending_tours.filtered(lambda r: r.state == 'Applied'
        #                                                         and r.tour_type_id.code != 'project')

        #     RA_pending_tours += pending_tours.filtered(lambda r: r.state == 'Applied' and
        #                                                          r.actual_project_id.reviewer_id == r.employee_id and
        #                                                          r.tour_type_id.code == 'project')

        #     if RA_pending_tours:
        #         parent_ids = RA_pending_tours.mapped('employee_id.parent_id')
        #         for ra in parent_ids:
        #             corresponding_tours = RA_pending_tours.filtered(lambda r: r.employee_id.parent_id == ra)
        #             mail_template.with_context(users=ra.name, emails=ra.work_email,
        #                                        tours=corresponding_tours).send_mail(corresponding_tours[-1].id,
        #                                                                             notif_layout="kwantify_theme.csm_mail_notification_light")

        #     # Email for project tour pending at PM
        #     query = f'''select array_agg(kt.id), pj.emp_id from kw_tour kt
        #                 join project_project pj on pj.id = kt.actual_project_id
        #                 join kw_tour_type ktt on ktt.id = kt.tour_type_id
        #                 where kt.state = 'Applied' and  ktt.code = 'project' 
        #                 and kt.employee_id != pj.emp_id and kt.employee_id != pj.reviewer_id
        #                 group by pj.emp_id '''
        #     self._cr.execute(query)
        #     query_result = self._cr.fetchall()
        #     for record in query_result:
        #         ra = self.env['hr.employee'].browse(record[1])
        #         corresponding_tours = pending_tours.filtered(lambda r: r.id in record[0])
        #         if corresponding_tours:
        #             mail_template.with_context(users=ra.name, emails=ra.work_email,
        #                                        tours=corresponding_tours).send_mail(corresponding_tours[-1].id,
        #                                                                             notif_layout="kwantify_theme.csm_mail_notification_light")

        #     # Email for project tour pending at PR
        #     query = f'''select array_agg(kt.id), pj.reviewer_id from kw_tour kt
        #                 join project_project pj on pj.id = kt.actual_project_id
        #                 join kw_tour_type ktt on ktt.id = kt.tour_type_id
        #                 where kt.state = 'Applied' and  ktt.code = 'project' 
        #                 and kt.employee_id = pj.emp_id and kt.employee_id != pj.reviewer_id
        #                 group by pj.reviewer_id '''
        #     self._cr.execute(query)
        #     query_result = self._cr.fetchall()
        #     for record in query_result:
        #         ra = self.env['hr.employee'].browse(record[1])
        #         corresponding_tours = pending_tours.filtered(lambda r: r.id in record[0])
        #         if corresponding_tours:
        #             mail_template.with_context(users=ra.name, emails=ra.work_email,
        #                                        tours=corresponding_tours).send_mail(corresponding_tours[-1].id,
        #                                                                             notif_layout="kwantify_theme.csm_mail_notification_light")

        #     forwarded_tours = pending_tours and pending_tours.filtered(lambda r: r.state == 'Forwarded')
        #     if forwarded_tours:
        #         forwarded_employees = forwarded_tours.mapped('final_approver_id')
        #         for employee in forwarded_employees:
        #             employee_pending_tours = forwarded_tours.filtered(lambda r: r.final_approver_id == employee)
        #             mail_template.with_context(users=employee.name, emails=employee.work_email,
        #                                        tours=employee_pending_tours).send_mail(employee_pending_tours[-1].id,
        #                   notif_layout="kwantify_theme.csm_mail_notification_light")

            approved_tours = pending_tours and pending_tours.filtered(lambda r: r.state == 'Approved' and (
                        r.cancellation_status == False and not set(r.settlement_ids.mapped('state')) - {'Draft',
                                                                                                        'Rejected'}) and (current_datetime - r.action_datetime).days < maximum_pending_tarveldesk_days)
            if approved_tours:
                travel_desk_users = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_users_l1_ids') or "[]")
                mail_to=[]
                # travel_desk_users = self.env.ref('kw_tour.group_kw_tour_travel_desk').users
                if travel_desk_users:
                    emp = self.env['hr.employee'].sudo().search([('id', 'in', travel_desk_users)])
                    mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                user_names = ','.join(emp.mapped('name'))
                emails = ",".join(mail_to) or ''
                mail_template.with_context(users=user_names, emails=emails, tours=approved_tours).send_mail(
                        approved_tours[-1].id, notif_layout="kwantify_theme.csm_mail_notification_light")

            approved_tours = pending_tours and pending_tours.filtered(lambda r: r.state == 'Approved' and (
                        r.cancellation_status == False and not set(r.settlement_ids.mapped('state')) - {'Draft',
                                                                                                        'Rejected'}) and (current_datetime - r.action_datetime).days > maximum_pending_tarveldesk_days)
            if approved_tours:
                travel_desk_users_1 = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_users_l1_ids') or "[]")
                travel_desk_users_2 = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_users_l2_ids') or "[]")
                traveldesk_emp_1 = self.env['hr.employee'].browse(travel_desk_users_1)
                traveldesk_emp_2 = self.env['hr.employee'].browse(travel_desk_users_2)
                user_names_1 = ','.join(traveldesk_emp_1.mapped('name'))
                emails_1 = ','.join(traveldesk_emp_1.mapped('work_email'))

                user_names_2 = ','.join(traveldesk_emp_2.mapped('name'))
                emails_2 = ','.join(traveldesk_emp_2.mapped('work_email'))
                traveldesk_emails = ','.join([emails_1, emails_2])
                traveldesk_user_names = ','.join([user_names_1, user_names_2])
                # travel_desk_users = self.env.ref('kw_tour.group_kw_tour_travel_desk').users
                if traveldesk_emails:
                    mail_template.with_context(users=traveldesk_user_names, emails=traveldesk_emails, tours=approved_tours).send_mail(
                            approved_tours[-1].id, notif_layout="kwantify_theme.csm_mail_notification_light")                        

            travel_desk_approved_tours = pending_tours.filtered(lambda r: r.state == 'Traveldesk Approved' and (
                        r.cancellation_status == False and not set(r.settlement_ids.mapped('state')) - {'Draft',
                                                                                                        'Rejected'}))
            if travel_desk_approved_tours:
                finance_users = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_finance_users_l1_ids') or "[]")
                # finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
                mail_to=[]
                if finance_users:
                    emp = self.env['hr.employee'].sudo().search([('id', 'in', finance_users)])
                    mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                emails = ",".join(mail_to) or ''
                user_names= ','.join(emp.mapped('name'))
                mail_template.with_context(users=user_names, emails=emails,
                                               tours=travel_desk_approved_tours).send_mail(
                        travel_desk_approved_tours[-1].id, notif_layout="kwantify_theme.csm_mail_notification_light")
        # End : Tour pending action code

        # Start : Settlement pending action code

        pending_settlements = self.env['kw_tour_settlement'].search(
            [('state', 'in', ['Applied', 'Forwarded', 'Approved'])])

        if pending_settlements:
            reminder_template = self.env.ref('kw_tour.kw_tour_settlement_pending_action_email_template')
            maximum_pending_days = int(self.env['ir.config_parameter'].sudo().get_param('tour_maximum_pending_days'))
        #     # RA_pending_settlements = pending_settlements.filtered(lambda r:r.state == 'Applied' and r.pending_status_at == 'RA')

        #     # Email to non-project and project tour settlement to RA
        #     RA_pending_settlements = pending_settlements.filtered(
        #         lambda r: r.state == 'Applied' and r.tour_type_id.code != 'project'
        #                   and (current_datetime - r.action_datetime).days > maximum_pending_days)

        #     RA_pending_settlements += pending_settlements.filtered(
        #         lambda r: r.state == 'Applied' and r.tour_type_id.code == 'project'
        #                   and r.actual_project_id.reviewer_id == r.employee_id
        #                   and (current_datetime - r.action_datetime).days > maximum_pending_days)
        #     if RA_pending_settlements:
        #         parent_ids = RA_pending_settlements.mapped('employee_id.parent_id')
        #         for ra in parent_ids:
        #             corresponding_settlements = RA_pending_settlements.filtered(lambda r: r.employee_id.parent_id == ra)
        #             try:
        #                 reminder_template.with_context(users=ra.name, emails=ra.work_email,
        #                                                settlements=corresponding_settlements).send_mail(
        #                     corresponding_settlements[-1].id, notif_layout="kwantify_theme.csm_mail_notification_light")
        #             except Exception:
        #                 pass

            # Email to project tour settlement to PM-----
            # query = f'''select array_agg(kts.id), pj.emp_id from kw_tour_settlement kts
            #             join project_project pj on pj.id = kts.actual_project_id
            #             join kw_tour_type ktt on ktt.id = kts.tour_type_id
            #             where kts.state = 'Applied' and ktt.code = 'project' 
            #             and kts.employee_id != pj.emp_id and kts.employee_id != pj.reviewer_id
            #             group by pj.emp_id '''
            # self._cr.execute(query)
            # settlement_pm_query_result = self._cr.fetchall()
            # for record in settlement_pm_query_result:
            #     ra = self.env['hr.employee'].browse(record[1])
            #     corresponding_tours = pending_settlements.filtered(lambda r: r.id in record[0]
            #                                                                  and (current_datetime - r.action_datetime).days > maximum_pending_days)
            #     if corresponding_tours:
            #         reminder_template.with_context(users=ra.name, emails=ra.work_email,
            #                                        settlements=corresponding_tours).send_mail(
            #             corresponding_tours[-1].id,
            #             notif_layout="kwantify_theme.csm_mail_notification_light")

            # # Email to project tour settlement to PR
            # query = f'''select array_agg(kts.id), pj.reviewer_id from kw_tour_settlement kts
            #             join project_project pj on pj.id = kts.actual_project_id
            #             join kw_tour_type ktt on ktt.id = kts.tour_type_id
            #             where kts.state = 'Applied' and  ktt.code = 'project' 
            #             and kts.employee_id = pj.emp_id and kts.employee_id != pj.reviewer_id
            #             group by pj.reviewer_id '''
            # self._cr.execute(query)
            # settlement_pr_query_result = self._cr.fetchall()
            # for record in settlement_pr_query_result:
            #     ra = self.env['hr.employee'].browse(record[1])
            #     corresponding_tours = pending_settlements.filtered(lambda r: r.id in record[0]
            #                                                                  and (current_datetime - r.action_datetime).days > maximum_pending_days)
            #     if corresponding_tours:
            #         reminder_template.with_context(users=ra.name, emails=ra.work_email,
            #                                        settlements=corresponding_tours).send_mail(
            #             corresponding_tours[-1].id,
            #             notif_layout="kwantify_theme.csm_mail_notification_light")

            # UA_pending_settlements = pending_settlements.filtered(lambda r:r.state == 'Applied' and r.pending_status_at == 'UA')
            # if UA_pending_settlements:
            #     ua_ids = UA_pending_settlements.mapped('employee_id.parent_id.parent_id')
            #     for ua in ua_ids:
            #         corresponding_settlements = UA_pending_settlements.filtered(lambda r:r.employee_id.parent_id.parent_id == ua)
            #         reminder_template.with_context(users=ua.name,emails=ua.work_email,settlements=corresponding_settlements).send_mail(corresponding_settlements[-1].id,notif_layout="kwantify_theme.csm_mail_notification_light")

            # forwarded_settlements = pending_settlements.filtered(
            #     lambda r: r.state == 'Forwarded' and (current_datetime - r.action_datetime).days > maximum_pending_days)
            # if forwarded_settlements:
            #     forwarded_employees = forwarded_settlements.mapped('final_approver_id')
            #     for employee in forwarded_employees:
            #         employee_pending_settlements = forwarded_settlements.filtered(
            #             lambda r: r.final_approver_id == employee)
            #         try:
            #             reminder_template.with_context(users=employee.name, emails=employee.work_email,
            #                                            settlements=employee_pending_settlements).send_mail(
            #                 employee_pending_settlements[-1].id,
            #                 notif_layout="kwantify_theme.csm_mail_notification_light")
            #         except Exception:
            #             pass
            # approved_settlements = pending_settlements.filtered(
            #     lambda r: r.state == 'Approved' and (current_datetime - r.action_datetime).days < maximum_pending_days)
            # if approved_settlements:
            #     finance_emp_ids = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_finance_users_l1_ids') or "[]")
            #     # finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
            #     mail_to = []
            #     if finance_emp_ids:
            #         emp = self.env['hr.employee'].sudo().search([('id', 'in', finance_emp_ids)])
            #         mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
            #     emails = ",".join(mail_to) or ''
            #     user_name= ','.join(emp.mapped('name'))

            #     # if finance_users:
            #     #     user_names = ','.join(finance_users.mapped('name'))
            #     #     emails = ','.join(finance_users.mapped('employee_ids.work_email'))
            #     try:
            #         reminder_template.with_context(users=user_name, emails=emails,
            #                                         settlements=approved_settlements).send_mail(
            #             approved_settlements[-1].id, notif_layout="kwantify_theme.csm_mail_notification_light")
            #     except Exception:
            #         pass

            approved_settlements = pending_settlements.filtered(
                lambda r: r.state == 'Approved' and (current_datetime - r.action_datetime).days > maximum_pending_days)        
            if approved_settlements:
                finance_emp_ids_1 = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_finance_users_l1_ids') or "[]")
                finance_emp_ids_2 = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_finance_users_l2_ids') or "[]")
                finance_users_1 = self.env['hr.employee'].browse(finance_emp_ids_1)
                finance_users_2 = self.env['hr.employee'].browse(finance_emp_ids_2)

                user_names_1 = ','.join(finance_users_1.mapped('name'))
                emails_1 = ','.join(finance_users_1.mapped('work_email'))

                user_names_2 = ','.join(finance_users_2.mapped('name'))
                emails_2 = ','.join(finance_users_2.mapped('work_email'))
                finance_emails = ','.join([emails_1, emails_2])
                finance_user_names = ','.join([user_names_1, user_names_2])
                # finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
                if finance_emails:
                    try:
                        reminder_template.with_context(users=finance_user_names, emails=finance_emails,
                                                       settlements=approved_settlements).send_mail(
                            approved_settlements[-1].id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    except Exception:
                        pass
        # End : Settlement pending action code

    def notify_users(self, user_ids, body):
        ch_obj = self.env['mail.channel']
        for user in user_ids:

            channel1, channel2 = f'{user.name}, {self.env.user.name}', f'{self.env.user.name}, {user.name}'
            channel = ch_obj.sudo().search(["|", ('name', 'ilike', channel1), ('name', 'ilike', channel2)])
            if not channel:
                channel_id = ch_obj.channel_get(user.partner_id.ids)
                channel = ch_obj.browse([channel_id['id']])
            channel[-1].message_post(body=body, message_type='comment',
                                     subtype='mail.mt_comment',
                                     author_id=self.env.user.partner_id.id,
                                     notif_layout='mail.mail_notification_light')

    # ---------------Start : Approval Flow---------------------------#

    @api.multi
    def action_approve_tour(self,context=False,by_email=False,remark=False):
        remark = remark or self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")

        self.write({'state': 'Approved',
                    'approver_id': False,
                    'remark': False,
                    'final_approver_id': False,
                    'upper_ra_id': False,
                    # 'pending_status_at' : False,
                    'action_datetime': Datetime.now(),
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Approved'}]]
                    })

        self.message_post(body=f"Remark : {remark}")
        # Start : update attendance related records to False
        tour_dates = self.generate_days_with_from_and_to_date(self.date_travel, self.date_return)
        attendance_records = self.env['kw_daily_employee_attendance'].sudo().search(
            [('employee_id', '=', self.employee_id.id),
             ('attendance_recorded_date', 'in', tour_dates)])
        for record in attendance_records:
            if record.is_on_tour != True:
                try:
                    record.write({'is_on_tour': True})
                except Exception as e:
                    # print(e)
                    continue
        # End : update attendance related records to False

        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name

        notify_template = self.env.ref('kw_tour.kw_tour_approve_mail_template')
        traveldesk_users = self.env.ref('kw_tour.group_kw_tour_travel_desk').users
        traveldesk_users_emails = ','.join(traveldesk_users.mapped("employee_ids.work_email"))
        
        # travel_desk_cc_users = self.env.ref('kw_tour.group_kw_tour_travel_desk_notify').users or []
        travel_desk_cc_users_emails = ','.join([self.employee_id.work_email]) + ',' + self.employee_id.parent_id.work_email
        
        notify_template.with_context(
            token=self.access_token,
            email_users=traveldesk_users_emails,
            email_cc_users=travel_desk_cc_users_emails,
            action_user=uname).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env['kw_tour'].notify_users(self.create_uid, 'Tour have been approved by '+user.name)
        if not by_email:
            # action_id = self.env.ref('kw_tour.action_kw_tour_take_action_act_window').id
            # return {
            #     'type'  : 'ir.actions.act_url',
            #     'url'   : f'/web#action={action_id}&model=kw_tour&view_type=list',
            #     'target': 'self',
            # }
            return self.return_to_tour_take_action()

    @api.multi
    def action_forward_tour(self):
        remark = self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")

        approver = self.approver_id
        self.write({'state': 'Forwarded',
                    'approver_id': False,
                    'final_approver_id': approver.id,
                    'action_datetime': Datetime.now(),
                    'remark': False,
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Forwarded'}]]
                    })

        self.message_post(body=f"Remark : {remark}")

        template = self.env.ref('kw_tour.kw_tour_forward_mail_template')
        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name

        approver = self._get_tour_approver()
        template.with_context(
            token=self.access_token, user_name=uname, email_cc=approver.work_email).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        if approver.user_id:
            self.env['kw_tour'].notify_users(approver.user_id, 'Tour have been forwarded by '+user.name)

        # action_id = self.env.ref('kw_tour.action_kw_tour_take_action_act_window').id
        # return {
        #     'type'      : 'ir.actions.act_url',
        #     'url'       : f'/web#action={action_id}&model=kw_tour&view_type=list',
        #     'target'    : 'self'
        # }
        return self.return_to_tour_take_action()

    @api.multi
    def action_traveldesk_revert_tour(self, context=False, by_email=False, remark=False):
        # print('travel_revert called>>>>>>>>>>>>>>>>')
        remark = remark or self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")
        self.message_post(body=f"Remark : {remark}")

        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name
        # approver = self._get_tour_approver()
        # cc_employees = approver
        notify_template = self.env.ref('kw_tour.kw_tour_revert_traveldesk_email_template')
        traveldesk_users = self.env.ref('kw_tour.group_kw_tour_travel_desk').users
        traveldesk_users_emails = ','.join(traveldesk_users.mapped("employee_ids.work_email"))
        
        travel_desk_cc_users = self.env.ref('kw_tour.group_kw_tour_travel_desk_notify').users or []
        travel_desk_cc_users_emails = ','.join(travel_desk_cc_users.mapped("employee_ids.work_email") + [self.employee_id.work_email])
        
        notify_template.with_context(
            token=self.access_token,
            email_users=traveldesk_users_emails,
            # email_cc_users=travel_desk_cc_users_emails,
            action_user=uname).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        if not by_email:
            self.sudo().write({'state': 'Draft',
                    'remark': False,
                    'action_datetime': Datetime.now(),
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Draft'}]]})
        action_id = self.env.ref('kw_tour.action_kw_tour_take_action_act_window').id
        return {
            'type'      : 'ir.actions.act_url',
            'url'       : f'/web#action={action_id}&model=kw_tour&view_type=list',
            'target'    : 'self'
        }
          
       
    @api.multi
    def action_traveldesk_approve_tour(self, context=False, by_email=False, remark=False):
        remark = remark or self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")
        self.write({'state': 'Traveldesk Approved',
                    'remark': False,
                    'action_datetime': Datetime.now(),
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Traveldesk Approved'}]]})

        self.message_post(body=f"Remark : {remark}")

        # Start : update attendance related records to False
        tour_dates = self.generate_days_with_from_and_to_date(self.date_travel, self.date_return)
        attendance_records = self.env['kw_daily_employee_attendance'].sudo().search(
            [('employee_id', '=', self.employee_id.id),
             ('attendance_recorded_date', 'in', tour_dates)])
        for record in attendance_records:
            if record.is_on_tour != True:
                try:
                    record.write({'is_on_tour': True})
                except Exception as e:
                    # print(e)
                    continue
        # End : update attendance related records to False

        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name

        notify_template = self.env.ref('kw_tour.kw_tour_approve_mail_template')

        approver = self._get_tour_approver()
        # cc_employees = self.employee_id | self.employee_id.parent_id
        cc_employees = approver
        email_cc_users = ''
        restrict_emp_ids = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_approval_email_ids') or "[]")
        if cc_employees:
            cc_employees -= cc_employees.filtered(lambda r: r.id in restrict_emp_ids)
            if cc_employees:
                email_cc_users = ','.join(cc_employees.mapped('work_email'))
        finance_users = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_finance_users_l1_ids') or "[]")
        # finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
        mail_to = []
        if finance_users:
            emp = self.env['hr.employee'].sudo().search([('id', 'in', finance_users)])
            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
        emails = ",".join(mail_to) or ''
        # finance_users_emails = ','.join(finance_users.mapped("employee_ids.work_email"))

        notify_template.with_context(
            token=self.access_token,
            email_users=emails,
            email_cc_users=email_cc_users,
            action_user=uname).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        guest_house_bookings = self.accomodation_ids.filtered(lambda r: r.arrangement == 'Guest House')
        if guest_house_bookings:
            notif_template = self.env.ref('kw_tour.kw_tour_guesthouse_notification_email_template')
            guest_houses = guest_house_bookings.mapped('guest_house_id')
            for guest_house in guest_houses:
                all_related_bookings = guest_house_bookings.filtered(lambda r: r.guest_house_id == guest_house)
                contact_person_emails = ','.join(
                    guest_house.mapped('contact_person_id').filtered(lambda r: r.email).mapped('email'))

                spoc_person_email = ','.join(
                    guest_house.mapped('spoc_person_id').filtered(lambda r: r.email).mapped('email'))
                notif_template.with_context(email_users=contact_person_emails, spoc_users=spoc_person_email,booking_ids=all_related_bookings).send_mail(
                    self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            user_notif_template = self.env.ref('kw_tour.kw_tour_guesthouse_notification_traveller_email_template')
            for booking in guest_house_bookings:
                contact_person_emails = ','.join(booking.guest_house_id.mapped('contact_person_id').filtered(lambda r: r.email).mapped('email'))

                user_notif_template.with_context(email_users=contact_person_emails,booking_id=booking).send_mail(
                    self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env['kw_tour'].notify_users(
            self.create_uid, 'Tour traveldesk settings have been completed by ' + user.name)
        if not by_email:
            # action_id = self.env.ref('kw_tour.action_kw_tour_take_action_act_window').id
            # return {
            #     'type'      : 'ir.actions.act_url',
            #     'url'       : f'/web#action={action_id}&model=kw_tour&view_type=list',
            #     'target'    : 'self',
            # }
            return self.return_to_tour_take_action()

    @api.multi
    def confirm_approve_with_extra_baggage(self):
        '''launch remark form'''
        form_view_id = self.env.ref("kw_tour.view_kw_tour_approve_remark_form").id
        return {
            'name': 'Remarks',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'nodestroy': True,
        }
    
    @api.multi
    def action_finace_approve_tour(self, context=False, by_email=False, remark=False):
        remark = remark or self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")

        disburse_inr = disburse_usd = 0

        if self.to_disbursed_inr:
            disburse_inr = self.disbursed_inr + self.to_disbursed_inr

        if self.to_disbursed_usd:
            disburse_usd = self.disbursed_usd + self.to_disbursed_usd

        if self.to_disbursed_inr > 0 or self.to_disbursed_usd > 0:
            advance_log = self.env['kw_tour_advance_given_log']
            log_data = {'tour_id':self.id}

            if self.to_disbursed_inr > 0:
                log_data['requested_inr'] = self.advance
                log_data['old_amount_inr'] = self.disbursed_inr
                log_data['disbursed_amount_inr'] = disburse_inr
                log_data['new_amount_inr'] = self.disbursed_inr + self.to_disbursed_inr

            if self.to_disbursed_usd > 0:
                log_data['requested_usd'] = self.advance_usd
                log_data['old_amount_usd'] = self.disbursed_usd
                log_data['disbursed_amount_usd'] = disburse_usd
                log_data['new_amount_usd'] = self.disbursed_usd + self.to_disbursed_usd

                log_data['exchange_rate'] = self.exchange_rate

            advance_log.create(log_data)

        data = {'state': 'Finance Approved', 'remark': False,
                'disbursed_inr': disburse_inr, 'disbursed_usd': disburse_usd,
                'to_disbursed_usd': False, 'to_disbursed_inr': False,
                'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Finance Approved'}]]
                }
        self.write(data)
        # Start : update attendance related records
        tour_dates = self.env['kw_tour'].generate_days_with_from_and_to_date(self.date_travel, self.date_return)
        attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                                    ('attendance_recorded_date', 'in', tour_dates)])
        for record in attendance_records:
            if record.is_on_tour != True:
                try:
                    record.write({ 'is_on_tour': True})
                except Exception as e:
                    # print(e)
                    continue
        # End : update attendance related records

        self.message_post(body=f"Remark : {remark}")

        template = self.env.ref('kw_tour.kw_tour_finance_approve_reject_email_template')
        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name

        approver = self._get_tour_approver()
        restrict_emp_ids = literal_eval(
            self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_approval_email_ids') or "[]")
        email_cc_users = ''
        if approver:
            approver -= approver.filtered(lambda r: r.id in restrict_emp_ids)
            if approver:
                email_cc_users = approver.work_email
        template.with_context(user_name=uname, email_cc_users=email_cc_users).send_mail(self.id,
                                                                                             notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env['kw_tour'].notify_users(self.create_uid, 'Tour finance settings have been completed by '+user.name)

        if not by_email:
            # action_id = self.env.ref('kw_tour.action_kw_tour_take_action_act_window').id
            # return {
            #     'type'      : 'ir.actions.act_url',
            #     'url'       : f'/web#action={action_id}&model=kw_tour&view_type=list',
            #     'target'    : 'self',
            # }
            return self.return_to_tour_take_action()
    # added on 12 march 2021 (gouranga) to solve the issue of disable button after redirect to tree view from form view

    def return_to_tour_take_action(self):
        tree_view_id = self.env.ref('kw_tour.view_kw_tour_take_action_tree').id
        form_view_id = self.env.ref('kw_tour.view_kw_tour_take_action_form').id

        return {
            'name': 'Take Action',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'kw_tour',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'context': {"access_label_check": 1},
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        }
                
    @api.multi
    def action_reject_tour(self, context=False, by_email=False, remark=False):
        # if by_email:
        #     remark = remark
        # else:
        #     remark = self.remark.strip()

        remark = remark if by_email else self.remark.strip()

        prev_state = self.state
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")

        self.write({'state': 'Rejected', 'remark': False,
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Rejected'}]]})
        template = self.env.ref('kw_tour.kw_tour_finance_approve_reject_email_template')
        user = self.env.user
        email_cc_users=self.employee_id.coach_id.work_email if self.employee_id.coach_id else ''
        uname = user.employee_ids and user.employee_ids[-1].name or user.name
        if prev_state in ['Forwarded', 'Traveldesk Approved']:  # cc to ra
            approver = self._get_tour_approver()
            # ra_email = self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.work_email or ''
            restrict_emp_ids = literal_eval(
                self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_approval_email_ids') or "[]")
            email_cc_users = ''
            if approver:
                approver -= approver.filtered(lambda r: r.id in restrict_emp_ids)
                if approver:
                    email_cc_users = approver.work_email + ',' + self.employee_id.coach_id.work_email
                    print("email cc===============",email_cc_users)
            template.with_context(user_name=uname, email_cc_users=email_cc_users).send_mail(self.id,
                                                                                                 notif_layout="kwantify_theme.csm_mail_notification_light")

        template.with_context(user_name=uname,email_cc_users=email_cc_users).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env['kw_tour'].notify_users(
            self.create_uid, 'Tour has been rejected by '+user.name)

        if not by_email:
            # action_id = self.env.ref('kw_tour.action_kw_tour_take_action_act_window').id
            # return {
            #     'type': 'ir.actions.act_url',
            #     'url': f'/web#action={action_id}&model=kw_tour&view_type=list',
            #     'target': 'self',
            # }
            return self.return_to_tour_take_action()

    # ---------------End : Approval Flow---------------------------#
    
    @api.multi
    def name_get(self):
        if self._context.get('by_code'):
            result = [(tour.id,tour.code) for tour in self]
        else:
            result = [(tour.id,tour.employee_id.name_get()[0][1]) for tour in self]
        return result
    
    def generate_days_with_from_and_to_date(self, from_date, to_date):
        date_list = []
        delta = to_date - from_date
        for i in range(delta.days+1):
            day = from_date + timedelta(days=i)
            date_list.append(day)
        return date_list

    def get_city_dates(self):
        self.ensure_one()

        from_cities = self.tour_detail_ids.mapped('from_city_id')
        to_cities = self.tour_detail_ids.mapped('to_city_id')

        all_cities = from_cities | to_cities
        tour_city_date_dicts = {city.id: [] for city in all_cities}

        # user_timezone = pytz.timezone(self.employee_id.user_id.tz or 'UTC')

        for index, detail in enumerate(self.tour_detail_ids, start=1):
            from_date = detail.from_date  # .astimezone(user_timezone).date()
            to_date = detail.to_date  # .astimezone(user_timezone).date()

            if index == 1:
                # from date of first record added to source city ## 3-March-2021 (Gouranga)
                tour_city_date_dicts[detail.from_city_id.id] += [from_date]
                temp_date_list = [date for date in self.generate_days_with_from_and_to_date(from_date,to_date) if date not in tour_city_date_dicts[detail.to_city_id.id]]
                tour_city_date_dicts[detail.to_city_id.id] += temp_date_list
            else:
                temp_from_dates = [date for date in self.generate_days_with_from_and_to_date(prev_date,from_date) if date not in tour_city_date_dicts[detail.from_city_id.id]]
                tour_city_date_dicts[detail.from_city_id.id] += temp_from_dates

                # from date also included for to city ## 3-March-2021 (Gouranga)
                temp_to_dates = [date for date in self.generate_days_with_from_and_to_date(from_date,to_date) if date not in tour_city_date_dicts[detail.to_city_id.id]]
                tour_city_date_dicts[detail.to_city_id.id] += temp_to_dates

            prev_date = to_date
        return tour_city_date_dicts
    
    def get_city_halt_time(self):
        self.ensure_one()
        city_dict = {}

        if len(self.tour_detail_ids) > 1:
            temp_data = {}
            for index, data in enumerate(self.tour_detail_ids):
                if index == 0:  # take second city of first record in details as accommodation start
                    start_time = data.to_time or "00:00:00"
                    start_datetime = datetime.strptime(data.to_date.strftime("%Y-%m-%d") + ' ' + start_time, "%Y-%m-%d %H:%M:%S")
                    temp_data[data.to_city_id.id] = [start_datetime]
                else:
                    # for previous city
                    end_time = data.from_time or "23:59:00"
                    end_date_time = datetime.strptime(data.from_date.strftime("%Y-%m-%d") + ' ' + end_time, "%Y-%m-%d %H:%M:%S")
                    temp_data[prev_record.to_city_id.id].append(end_date_time)

                    if index < len(self.tour_detail_ids):  # don't calculate for last reached city
                        start_time = data.to_time or "00:00:00"
                        start_datetime = datetime.strptime(data.to_date.strftime("%Y-%m-%d") + ' ' + start_time, "%Y-%m-%d %H:%M:%S")
                        temp_data[data.to_city_id.id] = [start_datetime]

                # shift data to main dictionary if list contains 2 elements i.e start datetime , end datetime
                for k,v in temp_data.copy().items():
                    if len(v) ==2:
                        if k not in city_dict:
                            city_dict[k] = [v]
                        else:
                            city_dict[k].append(v)
                        temp_data.pop(k)  # remove city from temp_date when shifting is completed

                prev_record = data
                
        return city_dict

    def get_city_time_range_status(self):
        self.ensure_one()
        city_time_range = {}
        started = False
        ended = False
        user_timezone = pytz.timezone(self.env.user.tz or 'UTC')

        tour_start_datetime = datetime.strptime(self.tour_detail_ids[0].from_date.strftime("%Y-%m-%d") + ' ' + self.tour_detail_ids[0].from_time, "%Y-%m-%d %H:%M:%S")
        tour_end_datetime = datetime.strptime(self.tour_detail_ids[-1].from_date.strftime("%Y-%m-%d") + ' ' + self.tour_detail_ids[-1].from_time, "%Y-%m-%d %H:%M:%S")

        if tour_start_datetime.astimezone(user_timezone).replace(tzinfo=None) < datetime.now():
            started = True
        if tour_end_datetime.astimezone(user_timezone).replace(tzinfo=None) < datetime.now():
            ended = True

        for index,data in enumerate(self.tour_detail_ids):
            if index == 0:  # start
                target_city = data.to_city_id.id
                start_datetime = datetime.strptime(data.from_date.strftime("%Y-%m-%d") + ' ' + data.from_time, "%Y-%m-%d %H:%M:%S")
                end_datetime = datetime.strptime(data.to_date.strftime("%Y-%m-%d") + ' ' + data.to_time, "%Y-%m-%d %H:%M:%S") - timedelta(seconds=1)
                time_range = [(start_datetime, end_datetime)]

                if target_city not in city_time_range:
                    city_time_range[target_city] = time_range
                else:
                    city_time_range[target_city] += time_range
                prev_date_time = end_datetime + timedelta(seconds=1)

            else:
                prev_city = data.from_city_id.id
                target_city = data.to_city_id.id

                start_datetime = datetime.strptime(data.from_date.strftime("%Y-%m-%d") + ' ' + data.from_time, "%Y-%m-%d %H:%M:%S")
                end_datetime = datetime.strptime(data.to_date.strftime("%Y-%m-%d") + ' ' + data.to_time, "%Y-%m-%d %H:%M:%S") - timedelta(seconds=1)

                prev_city_time_range = [(prev_date_time, start_datetime - timedelta(seconds=1))]
                target_city_time_range = [(start_datetime, end_datetime)]

                if target_city not in city_time_range:
                    city_time_range[target_city] = target_city_time_range
                else:
                    city_time_range[target_city] += target_city_time_range
                
                city_time_range[prev_city] += prev_city_time_range

        return started, ended, city_time_range
