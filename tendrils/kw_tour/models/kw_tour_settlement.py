import pytz
from datetime import date,timedelta,datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from ast import literal_eval
import json, requests


class TourSettlement(models.Model):
    _name = 'kw_tour_settlement'
    _description = "Tour Settlement"
    _rec_name = 'employee_id'
    _order = 'create_date desc'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.model
    def _get_domain(self):
        settlement_pending_tour_ids = self.env['kw_tour_settlement'].search(
            [('create_uid', '=', self._uid), ('state', '!=', 'Rejected')])
        tour_ids = settlement_pending_tour_ids.mapped('tour_id').ids
        return [('create_uid', '=', self._uid), ('id', 'not in', tour_ids),
                ('state', 'in', ['Finance Approved']),
                ('settlement_id', '=', False)]

    # @api.model
    # def _get_finance_employee(self):
    #     finance_group   = self.env.ref('kw_tour.group_kw_tour_finance')
    #     user_ids        = finance_group.users and finance_group.users.ids or []
    #     return [('user_id','in', user_ids)]
    c_suite_boolean = fields.Boolean('C-Suite')
    additional_exp_boolean = fields.Boolean('Additional Expenses')
    domestic_currency_id = fields.Many2one('res.currency', related='tour_id.currency_id',
                                           default=lambda self: self.env.user.company_id.currency_id.id,
                                           readonly=True, store=True)
    usd_currency_id = fields.Many2one('res.currency', string='USD Currency',
                                      default=lambda self: self.env.ref('base.USD').id,
                                      readonly=True)

    employee_id = fields.Many2one('hr.employee', string="Employee Name",
                                  default=_default_employee, required=True, ondelete='cascade', index=True)
    emp_id = fields.Many2one(related="tour_id.employee_id")

    applied_date = fields.Date(string='Applied_date', default=fields.Date.context_today)
    tour_id = fields.Many2one(string='Tour', comodel_name='kw_tour', ondelete='cascade', required=True,
                              domain=_get_domain)
    tour_type_id = fields.Many2one('kw_tour_type', related="tour_id.tour_type_id", string="Type Of Tour", store=True)
    purpose = fields.Text("Purpose", related='tour_id.purpose', required=True)
    date_travel = fields.Date("Date Of Travel", related="tour_id.date_travel", )
    date_return = fields.Date("Return Date", related="tour_id.date_return")
    city_id = fields.Many2one('kw_tour_city', string="Originating Place", related="tour_id.city_id")

    code = fields.Char(string="Reference No.", related="tour_id.code")

    tour_detail_ids = fields.One2many(related='tour_id.tour_detail_ids', string="Tour Details")
    city_days_spend_ids = fields.One2many(related='tour_id.city_days_spend_ids', string="Days Spend")
    travel_expense_details_ids = fields.One2many(related='tour_id.travel_expense_details_ids', string="Travel Expenses")
    acc_arrange = fields.Selection(related="tour_id.acc_arrange", string='Accommodation Arrangement',
                                   selection=[('Company', 'Company'), ('Self', 'Self')])
    accomodation_ids = fields.One2many(related='tour_id.accomodation_ids', string="Accommodation Details")
    travel_detail_ids = fields.One2many(related="tour_id.travel_detail_ids", string="Travel Details")
    budget_head = fields.Char(related="tour_id.budget_head", string="Budget Head")

    settlement_detail_ids = fields.One2many("kw_tour_settlement_details", "settlement_id", string="Settlement Details")
    comment = fields.Text("Comment")
    payment_date = fields.Date('Payment Date')

    state = fields.Selection(string="Status",
                             selection=[('Draft', 'Draft'),
                                        ('Applied', 'Applied'),
                                        ('Forwarded', 'Forwarded'),
                                        ('Approved', 'Approved'),
                                        ('Granted', 'Granted'),
                                        ('Payment Done', 'Payment Done'),
                                        ('Rejected', 'Rejected')
                                        ])

    approver_id = fields.Many2one('hr.employee', 'Approver')
    final_approver_id = fields.Many2one('hr.employee', 'Final Approver')

    action_log_ids = fields.One2many('kw_tour_settlement_action_log', 'settlement_id', string='Action Logs')
    remark = fields.Text("Remark")

    ra_access = fields.Boolean("RA Access ?", compute="compute_ra_access")
    finance_access = fields.Boolean("Finance Access ?", compute="compute_finance_access")
    own_record = fields.Boolean("Own Record ?", compute="compute_own_access")
    current_user = fields.Many2one("res.users", string="Current User", compute="compute_own_access")
    upload_doc = fields.Binary("Upload Document")

    advance_inr = fields.Float(related='tour_id.disbursed_inr', string="Disbursed(Domestic)")
    advance_usd = fields.Float(related='tour_id.disbursed_usd', string="Disbursed(USD)")

    total_domestic = fields.Float(string="Total(Domestic)", compute="compute_total", store=True)
    total_international = fields.Float(string="Total(USD)", compute="compute_total", store=True)

    paid_domestic = fields.Float(string="Amount Payable(Domestic)", compute="compute_total")
    paid_international = fields.Float(string="Amount Payable(USD)", compute="compute_total")

    receivable_inr = fields.Float(string="Amount Receivable(Domestic)", compute="compute_total")

    receivable_usd = fields.Float(string="Amount Receivable(USD)", compute="compute_total")

    pending_at = fields.Char("Pending At", compute="compute_pending_at", store=True)
    job_id = fields.Many2one('hr.job', string="Designation", related="employee_id.job_id")
    dept_id = fields.Many2one('hr.department', string="Department Name", related="employee_id.department_id")

    advance_ids = fields.One2many('kw_tour_advance_given_log', related='tour_id.advance_ids',
                                  string="Advance Disbursed Log")

    total_expense_ids = fields.One2many('kw_tour_settlement_total_expense', 'settlement_id', string="Total Expenses")

    applied_datetime = fields.Datetime(string="Applied Time")

    action_datetime = fields.Datetime("Action taken Time", default=fields.Datetime.now)

    # pending_status_at     = fields.Selection(string='Pending At (status)',selection=[('RA', 'Reporting Authority'),('UA', 'Upper RA')])
    # upper_ra_id           = fields.Many2one('hr.employee',string="Upper RA")
    # upper_ra_switched_datetime = fields.Datetime(string="Switched To Upper RA Time")

    grant_date = fields.Date("Grant Date")
    grant_datetime = fields.Datetime("Grant Datetime")

    can_apply_inr = fields.Boolean(string='Can Apply For Advance INR ?', compute="_compute_advance_inr_usd")
    can_apply_usd = fields.Boolean(string='Can Apply For Advance USD ?', compute="_compute_advance_inr_usd")

    destination_str = fields.Char('Desting String', compute="get_tour_destinations_string")
    settled_tour_ids = fields.Many2many('kw_tour', string="Settlement Completed Tours",
                                        compute="compute_settlement_completed_tours")
    project_id = fields.Many2one(related="tour_id.project_id", string='Project', store=True)
    actual_project_id = fields.Many2one('project.project', related="tour_id.actual_project_id", string='Project', store=True)
    travel_arrangement = fields.Selection(related='tour_id.travel_arrangement', string="Travel Arrangement", store=True)
    travel_ticket_ids = fields.One2many("kw_tour_travel_ticket", "settlement_id", string="Ticket Details")
    travel_prerequisite_ids = fields.One2many('kw_tour_travel_prerequisite_details', 'settlement_id',
                                              string="Travel Prerequisite")
    additional_expenses_ids = fields.One2many('kw_tour_travel_additional_expense_details', 'settlement_id',
                                              string="Additional Expenses")
    budget_head_id = fields.Many2one(related="tour_id.budget_head_id", string="Budget Head",
                                     track_visibility='onchange', store=True)
    api_exchange_rate = fields.Float(related='tour_id.api_exchange_rate', string="API Exchange Rate", store=True)
    total_budget_expense = fields.Float("Total budget expense", compute='_get_total_budget_expense', store=True)
    project_budget_id = fields.Many2one('kw_tour_project_budget', string='Project Budget',
                                        compute='_compute_project_budget')
    budget_limit_crossed = fields.Boolean('Budget Limit Crossed', compute='_compute_budget_limit_crossed')
    emp_grade=fields.Many2one(related='tour_id.employee_id.grade', string="Employee Grade")
    emp_level=fields.Many2one(related='tour_id.employee_id.level', string="Employee Level")
    project_type = fields.Selection(related="tour_id.project_type", string="Project Type", store=True)
    apply_for = fields.Selection(string='Apply for',related="tour_id.apply_for")
    create_id =fields.Char(related='tour_id.create_uid.name')
    treasury_budget_id  = fields.Many2one('kw_tour_treasury_budget', compute='_compute_project_budget')
    additional_tour_expense = fields.Float('Additional Tour Expenses(Domestic)', compute='_compute_additional_expense', store=False)
    additional_tour_expense_usd = fields.Float('Additional Tour Expenses(USD)', compute='_compute_additional_expense',
                                           store=False)

    def _compute_additional_expense(self):
        for rec in self:
            additional_amount = 0
            additional_amount_usd = 0
            expenses = 0
            expense_usd = 0
            if rec.additional_expenses_ids:
                additional_amount += sum(rec.additional_expenses_ids.filtered(
                    lambda r: r.currency_id.name == rec.tour_id.sudo().create_uid.employee_ids.company_id.currency_id.name).mapped(
                    'amount'))
                additional_amount_usd += sum(
                    rec.additional_expenses_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('amount'))
            ta_act_amount = 0
            ta_claim = 0
            ta_act_amount_usd = 0
            ta_claim_usd = 0
            misc_expenses = 0
            misc_expense_usd = 0
            if rec.settlement_detail_ids:
                # ta_claiming_by_date = {}
                for recc in rec.settlement_detail_ids:
                    if recc.expense_id.code in ['ta'] and recc.amount_claiming > recc.amount_actual:
                        if recc.currency_id.name == rec.tour_id.sudo().employee_id.user_id.company_id.currency_id.name:
                            ta_act_amount += recc.amount_actual
                            ta_claim += recc.amount_claiming
                        elif recc.currency_id.name == 'USD':
                            ta_act_amount_usd += recc.amount_actual
                            ta_claim_usd += recc.amount_claiming

                    if recc.expense_id.code in ['hra'] and recc.amount_claiming > recc.amount_actual:
                        if recc.currency_id.name == rec.tour_id.sudo().employee_id.user_id.company_id.currency_id.name:
                            expenses += recc.amount_claiming - recc.amount_actual
                        elif recc.currency_id.name == 'USD':
                            expense_usd += (recc.amount_claiming - recc.amount_actual)

                    if recc.expense_id.code in ['misc'] and recc.amount_claiming > recc.amount_actual:
                        if recc.currency_id.name == rec.tour_id.sudo().employee_id.user_id.company_id.currency_id.name:
                            misc_expenses += recc.amount_claiming - recc.amount_actual
                        elif recc.currency_id.name == 'USD':
                            misc_expense_usd += (recc.amount_claiming - recc.amount_actual)
            ta_amount = 0
            if ta_act_amount < ta_claim:
                ta_amount += ta_claim - ta_act_amount

            ta_amount_usd = 0
            if ta_act_amount_usd < ta_claim_usd:
                ta_amount_usd += ta_claim_usd - ta_act_amount_usd

            rec.additional_tour_expense = additional_amount + expenses + ta_amount + misc_expenses
            rec.additional_tour_expense_usd = additional_amount_usd + expense_usd + misc_expense_usd + ta_amount_usd



    def check_parent_sort_(self, employee_id):
        csuite_emp = self.env['kw_tour_c_suite'].sudo().search(
            [('company_id', '=', self.tour_id.employee_id.company_id.id),
             ('department_id', '=', self.tour_id.employee_id.department_id.id)], limit=1).employee_ids.ids
        if csuite_emp:
            if employee_id.parent_id and employee_id.parent_id.id in csuite_emp:
                return employee_id.parent_id
            elif employee_id.parent_id:
                return self.check_parent_sort_(employee_id.parent_id)
            else:
                return employee_id
        else:
            return employee_id.parent_id

    def settlement_approval_flow(self):
        current_date = date.today()
        if not current_date >= self.date_return:
            raise ValidationError("Settlement can be applied after the return date")
        domestic_curr = self.tour_id.employee_id.user_id.company_id.currency_id.name
        approver_id = self.check_parent_sort_(self.tour_id.create_uid.employee_ids)
        expense_data = {}
        expense_data_usd = {}
        send_mail = False
        if self.settlement_detail_ids:
            ta_act_amount = 0
            ta_claim = 0
            ta_act_amount_usd = 0
            ta_claim_usd = 0
            other_amount = 0
            other_amount_usd = 0
            hra_amount = 0
            hra_amount_usd = 0
            for rec in self.settlement_detail_ids:
                if rec.expense_id.code in ['ta']and rec.amount_claiming > rec.amount_actual:
                    if rec.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name:
                        ta_act_amount += rec.amount_actual
                        ta_claim += rec.amount_claiming
                    elif rec.currency_id.name == 'USD':
                        ta_act_amount_usd += rec.amount_actual
                        ta_claim_usd += rec.amount_claiming
                if rec.expense_id.code in ['hra'] and rec.amount_claiming > rec.amount_actual:
                    if rec.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name:
                        hra_extra_amount = round(rec.amount_claiming - rec.amount_actual)
                        rounded_exchange_valuee = round(float(hra_extra_amount), 2)
                        hra_amount += rounded_exchange_valuee
                        send_mail = True
                    elif rec.currency_id.name == 'USD':
                        hra_extra_amountt = rec.amount_claiming - rec.amount_actual
                        exchange_value = hra_extra_amountt
                        rounded_exchange_value = round(float(exchange_value), 2)
                        hra_amount_usd += rounded_exchange_value
                        send_mail = True
                if rec.expense_id.code in ['misc'] and rec.amount_claiming > rec.amount_actual:
                    if rec.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name:
                        misc_extra_amount = round(rec.amount_claiming - rec.amount_actual)
                        rounded_exchange_valuee = round(float(misc_extra_amount), 2)
                        other_amount += rounded_exchange_valuee
                        send_mail = True
                    elif rec.currency_id.name == 'USD':
                        misc_extra_amountt = rec.amount_claiming - rec.amount_actual
                        exchange_value = misc_extra_amountt
                        rounded_exchange_value = round(float(exchange_value), 2)
                        other_amount_usd += rounded_exchange_value
                        send_mail = True
            if hra_amount > 0:
                expense_data['HRA'] = round(float(hra_amount), 2)
                send_mail = True
            if other_amount > 0:
                expense_data['Others'] = round(float(other_amount), 2)
                send_mail = True
            if ta_act_amount < ta_claim:
                send_mail = True
                ta_extra_amount = ta_claim - ta_act_amount
                rounded_exchange_ta_value = round(float(ta_extra_amount), 2)
                expense_data['TA'] = rounded_exchange_ta_value

            if hra_amount_usd > 0:
                expense_data_usd['HRA'] = round(float(hra_amount_usd), 2)
                send_mail = True
            if other_amount_usd > 0:
                expense_data_usd['Others'] = round(float(other_amount_usd), 2)
                send_mail = True
            if ta_act_amount_usd < ta_claim_usd:
                send_mail = True
                ta_extra_amountt = ta_claim_usd - ta_act_amount_usd
                rounded_exchange_ta_valuee = round(float(ta_extra_amountt), 2)
                expense_data_usd['TA'] = rounded_exchange_ta_valuee

        if self.additional_expenses_ids:
            additional_amount = 0
            additional_amount_usd = 0
            additional_amount += sum(self.additional_expenses_ids.filtered(
                lambda r: r.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name).mapped(
                'amount'))
            if additional_amount > 0:
                additional = round(float(additional_amount), 2)
                expense_data['Additional Expenses'] = additional

            additional_amount_usd += sum(
                self.additional_expenses_ids.filtered(lambda r: r.currency_id.name == "USD").mapped(
                    'amount'))
            if additional_amount_usd > 0:
                additionall = round(float(additional_amount_usd), 2)
                expense_data_usd['Additional Expenses'] = additionall
                send_mail = True


        ex_ke = ''
        key_data = []
        for kee in expense_data:
            key_data.append(kee)
        for key_usd in expense_data_usd:
            if key_usd not in key_data:
                key_data.append(key_usd)
        for k in key_data:
            ex_ke = ex_ke + k + ' | '

        ex_amount = ''
        for ke in expense_data:
            ex_amount = ex_amount + str(expense_data[ke]) + ' | '

        ex_amount_usd = ''
        for ke_usd in expense_data_usd:
            ex_amount_usd = ex_amount_usd + str(expense_data_usd[ke_usd]) + ' | '


        formatted_expenses = ", ".join([f"{key}: {value}" for key, value in expense_data.items()])
        # print(formatted_expenses, '========>>')
        formatted_expenses_usd = ", ".join([f"{key}: {value}" for key, value in expense_data_usd.items()])
        csuite_employee = self.env['kw_tour_c_suite'].sudo().search(
            [('company_id', '=', self.tour_id.create_uid.employee_ids.company_id.id),
             ('department_id', '=', self.tour_id.create_uid.employee_ids.department_id.id)], limit=1).employee_ids.ids
        above_m8_grade = ['M8', 'M9', 'M10', 'E1', 'E2', 'E3', 'E4', 'E5']
        if self.tour_id.employee_id.grade.name in above_m8_grade:
            # print('above=============m8888888888888888888')
            if send_mail == True and approver_id and approver_id.id in csuite_employee:
                self.write(
                    {'state': 'Applied', 'final_approver_id': approver_id.id, 'applied_datetime': datetime.now(), 'c_suite_boolean':True, 'additional_exp_boolean':True,
                     'action_datetime': datetime.now()}, no_notify=True)
                template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail_c_suite')
                template.with_context(domestic_curr = domestic_curr, expense_data = expense_data, email_cc=self.employee_id.parent_id.work_email if approver_id.work_email != self.employee_id.parent_id.work_email else False, ex_key = ex_ke[:-3],
                                      ex_amount=formatted_expenses, ex_amount_usd=formatted_expenses_usd, email=approver_id.work_email, name=approver_id.name).send_mail(self.id,
                                                                                                                                                                                                                                     notif_layout="kwantify_theme.csm_mail_notification_light")
            elif send_mail == True and approver_id and approver_id.id not in csuite_employee:
                if self.tour_type_id.name == 'Project' and self.project_type == '70':
                    approverr = self._get_tour_approver()
                    self.write(
                        {'state': 'Applied', 'final_approver_id': approverr.id, 'applied_datetime': datetime.now(),
                         'c_suite_boolean': False, 'additional_exp_boolean':True,
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail_c_suite')
                    template.with_context(domestic_curr = domestic_curr,expense_data=expense_data, email_cc=self.employee_id.parent_id.work_email if approver_id.work_email != self.employee_id.parent_id.work_email else False,
                                          ex_key=ex_ke[:-3], ex_amount=formatted_expenses, ex_amount_usd=formatted_expenses_usd, email=approverr.work_email,
                                          name=approverr.name).send_mail(self.id,
                                                                         notif_layout="kwantify_theme.csm_mail_notification_light")

                else:
                    parent_ra_id = self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id or False
                    self.write(
                        {'state': 'Applied', 'final_approver_id': parent_ra_id.id, 'applied_datetime': datetime.now(),
                         'c_suite_boolean': False, 'additional_exp_boolean':True,
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail_c_suite')
                    template.with_context(domestic_curr = domestic_curr,expense_data=expense_data, email_cc=self.employee_id.parent_id.work_email if approver_id.work_email != self.employee_id.parent_id.work_email else False,
                                          ex_key=ex_ke[:-3], ex_amount=formatted_expenses, ex_amount_usd=formatted_expenses_usd, email=parent_ra_id.work_email,
                                          name=parent_ra_id.name).send_mail(self.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
            elif send_mail == True and not approver_id:
                parent_idd = self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.id or False
                self.write(
                    {'state': 'Approved', 'final_approver_id': parent_idd, 'applied_datetime': datetime.now(), 'additional_exp_boolean':True,
                     'action_datetime': datetime.now()}, no_notify=True)
                template = self.env.ref('kw_tour.kw_tour_settlement_applied_without_ra_mail')
                finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
                finance_users_emails = ','.join(finance_users.mapped("employee_ids.work_email"))
                template.with_context(email_users=finance_users_emails).send_mail(self.id,
                                                                                  notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                parent_id = self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.id or False
                if not parent_id:
                    self.write(
                        {'state': 'Approved', 'final_approver_id': parent_id, 'applied_datetime': datetime.now(),
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_without_ra_mail')
                    finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
                    finance_users_emails = ','.join(finance_users.mapped("employee_ids.work_email"))
                    template.with_context(email_users=finance_users_emails).send_mail(self.id,
                                                                                      notif_layout="kwantify_theme.csm_mail_notification_light")

                elif self.tour_type_id.name == 'Project' and self.project_type == '70':
                    approver = self._get_tour_approver()
                    self.write(
                        {'state': 'Applied', 'final_approver_id': approver.id, 'applied_datetime': datetime.now(),
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail')
                    template.with_context(email=approver.work_email, name=approver.name).send_mail(self.id,
                                                                                                   notif_layout="kwantify_theme.csm_mail_notification_light")

                else:
                    self.write(
                        {'state': 'Applied', 'final_approver_id': self.employee_id.parent_id.id, 'applied_datetime': datetime.now(),
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail')
                    template.with_context(email=self.employee_id.parent_id.work_email, name=self.employee_id.parent_id.name).send_mail(self.id,
                                                                                                                                       notif_layout="kwantify_theme.csm_mail_notification_light")

        else:
            # print('below m8888888888888888-------------------->>>>>>')
            if send_mail == True and approver_id and approver_id.id in csuite_employee and approver_id.parent_id:
                self.write(
                    {'state': 'Applied', 'final_approver_id': approver_id.id, 'applied_datetime': datetime.now(), 'c_suite_boolean':True, 'additional_exp_boolean':True,
                     'action_datetime': datetime.now()}, no_notify=True)
                template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail_c_suite')
                template.with_context(domestic_curr = domestic_curr,expense_data = expense_data, email_cc=self.employee_id.parent_id.work_email if approver_id.work_email != self.employee_id.parent_id.work_email else False, ex_key = ex_ke[:-3],
                                      ex_amount=formatted_expenses, ex_amount_usd=formatted_expenses_usd, email=approver_id.work_email, name=approver_id.name).send_mail(self.id,
                                                                                                                                                                                                                                     notif_layout="kwantify_theme.csm_mail_notification_light")
            elif send_mail == True and approver_id and approver_id.id in csuite_employee and not approver_id.parent_id:
                if self.tour_type_id.name == 'Project' and self.project_type == '70':
                    approverr = self._get_tour_approver()
                    self.write(
                        {'state': 'Applied', 'final_approver_id': approverr.id, 'applied_datetime': datetime.now(),
                         'c_suite_boolean': False, 'additional_exp_boolean':True,
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail_c_suite')
                    template.with_context(domestic_curr = domestic_curr,expense_data=expense_data, email_cc=self.employee_id.parent_id.work_email if approver_id.work_email != self.employee_id.parent_id.work_email else False,
                                          ex_key=ex_ke[:-3], ex_amount=formatted_expenses, ex_amount_usd=formatted_expenses_usd, email=approverr.work_email,
                                          name=approverr.name).send_mail(self.id,
                                                                         notif_layout="kwantify_theme.csm_mail_notification_light")

                else:
                    parent_ra_id = self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id or False
                    self.write(
                        {'state': 'Applied', 'final_approver_id': parent_ra_id.id, 'applied_datetime': datetime.now(),
                         'c_suite_boolean': False, 'additional_exp_boolean':True,
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail_c_suite')
                    template.with_context(domestic_curr = domestic_curr, expense_data=expense_data, email_cc=self.employee_id.parent_id.work_email if approver_id.work_email != self.employee_id.parent_id.work_email else False,
                                          ex_key=ex_ke[:-3], ex_amount=formatted_expenses, ex_amount_usd=formatted_expenses_usd, email=parent_ra_id.work_email,
                                          name=parent_ra_id.name).send_mail(self.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
            elif send_mail == True and approver_id and approver_id.id not in csuite_employee:
                if self.tour_type_id.name == 'Project' and self.project_type == '70':
                    approverr = self._get_tour_approver()
                    self.write(
                        {'state': 'Applied', 'final_approver_id': approverr.id, 'applied_datetime': datetime.now(),
                         'c_suite_boolean': False, 'additional_exp_boolean':True,
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail_c_suite')
                    template.with_context(domestic_curr = domestic_curr, expense_data=expense_data, email_cc=self.employee_id.parent_id.work_email if approver_id.work_email != self.employee_id.parent_id.work_email else False,
                                          ex_key=ex_ke[:-3], ex_amount=formatted_expenses, ex_amount_usd=formatted_expenses_usd, email=approverr.work_email,
                                          name=approverr.name).send_mail(self.id,
                                                                         notif_layout="kwantify_theme.csm_mail_notification_light")

                else:
                    parent_ra_id = self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id or False
                    self.write(
                        {'state': 'Applied', 'final_approver_id': parent_ra_id.id, 'applied_datetime': datetime.now(),
                         'c_suite_boolean': False, 'additional_exp_boolean':True,
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail_c_suite')
                    template.with_context(domestic_curr = domestic_curr, expense_data=expense_data, email_cc=self.employee_id.parent_id.work_email if approver_id.work_email != self.employee_id.parent_id.work_email else False,
                                          ex_key=ex_ke[:-3], ex_amount=formatted_expenses, ex_amount_usd=formatted_expenses_usd, email=parent_ra_id.work_email,
                                          name=parent_ra_id.name).send_mail(self.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
            elif send_mail == True and not approver_id:
                parent_idd = self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.id or False
                self.write(
                    {'state': 'Approved', 'final_approver_id': parent_idd, 'applied_datetime': datetime.now(), 'additional_exp_boolean':True,
                     'action_datetime': datetime.now()}, no_notify=True)
                template = self.env.ref('kw_tour.kw_tour_settlement_applied_without_ra_mail')
                finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
                finance_users_emails = ','.join(finance_users.mapped("employee_ids.work_email"))
                template.with_context(email_users=finance_users_emails).send_mail(self.id,
                                                                                  notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                parent_id = self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.id or False
                if not parent_id:
                    self.write(
                        {'state': 'Approved', 'final_approver_id': parent_id, 'applied_datetime': datetime.now(),
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_without_ra_mail')
                    finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
                    finance_users_emails = ','.join(finance_users.mapped("employee_ids.work_email"))
                    template.with_context(email_users=finance_users_emails).send_mail(self.id,
                                                                                      notif_layout="kwantify_theme.csm_mail_notification_light")

                elif self.tour_type_id.name == 'Project' and self.project_type == '70':
                    approver = self._get_tour_approver()
                    self.write(
                        {'state': 'Applied', 'final_approver_id': approver.id, 'applied_datetime': datetime.now(),
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail')
                    template.with_context(email=approver.work_email, name=approver.name).send_mail(self.id,
                                                                                                   notif_layout="kwantify_theme.csm_mail_notification_light")

                else:
                    self.write(
                        {'state': 'Applied', 'final_approver_id': self.employee_id.parent_id.id, 'applied_datetime': datetime.now(),
                         'action_datetime': datetime.now()}, no_notify=True)
                    template = self.env.ref('kw_tour.kw_tour_settlement_applied_mail')
                    template.with_context(email=self.employee_id.parent_id.work_email, name=self.employee_id.parent_id.name).send_mail(self.id,
                                                                                                                                       notif_layout="kwantify_theme.csm_mail_notification_light")


        # above the all mail communication part ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        project_budget = self.env['kw_tour_project_budget'].sudo()
        if self.tour_type_id.name == 'Project' and self.project_type == '70':
            # project budget
            data = self.env['account.fiscalyear'].sudo().search([
                ('date_start', '<=', self.date_travel),
                ('date_stop', '>=', self.date_travel)
            ]).mapped('id')
            budget_amount = project_budget.search(
                [('budget_head_id', '=', self.budget_head_id.id),
                 ('project_id', '=', self.project_id.id),
                 ])
            total_tour_amount = 0
            if self.tour_id.cancellation_status is False and self.tour_id.settlement_applied is False:
                total_tour_amount += self.total_budget_expense
            if budget_amount:
                spent_amount = sum(budget_amount.tour_ids.mapped('total_budget_expense')) + sum(budget_amount.settlement_ids.mapped('total_budget_expense')) - self.tour_id.total_budget_expense
                remaining_amount = budget_amount.budget_amount - spent_amount
                # threshold_amount = float(remaining_amount) * budget_amount.threshold_limit / 100
                # print(budget_amount,total_tour_amount, remaining_amount)
                if remaining_amount < 0:
                    raise ValidationError(
                        'Insufficient Balance Found in your Project budget. Please Contact Your PM for Further Information.')
                elif remaining_amount > 0 and remaining_amount < total_tour_amount:
                    raise ValidationError(
                        'Insufficient Balance Found in your Project budget. Please Contact Your PM for Further Information.')
                elif remaining_amount == 0:
                    raise ValidationError(
                        'No Budget Data Found in your Project. Please Contact your PM for Further Information.')
                else:
                    pass
            else:
                raise ValidationError(
                    'No Budget Data Found in your Project. Please Contact your PM for Further Information.')

        else:
            total_tour_amount = 0
            if self.tour_id.cancellation_status is False and self.tour_id.settlement_applied is False:
                total_tour_amount += self.total_budget_expense

            if self.tour_id.sudo().blocked_department_id:
                if self.tour_id.sudo().blocked_department_id.remaining_amount < total_tour_amount:
                    raise ValidationError(
                        'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
            else:
                data = self.env['account.fiscalyear'].sudo().search(
                    [('date_start', '<=', self.tour_id.date_travel), ('date_stop', '>=', self.tour_id.date_travel)]).mapped('id')

                department_sec = self.env['kw_tour_treasury_budget'].sudo().search(
                    [('fiscal_year_id', 'in', data), ('department_id', '=', self.tour_id.create_uid.employee_ids.section.id),
                     ('company_id', '=', self.tour_id.employee_id.user_id.company_id.id)],
                    limit=1)
                department_div = self.env['kw_tour_treasury_budget'].sudo().search(
                    [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.division.id),
                     ('company_id', '=', self.employee_id.user_id.company_id.id)],
                    limit=1)
                department_dep = self.env['kw_tour_treasury_budget'].sudo().search(
                    [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.department_id.id),
                     ('company_id', '=', self.employee_id.user_id.company_id.id)],
                    limit=1)
                if department_sec:
                    spent_amount = sum(department_sec.tour_ids.mapped('total_budget_expense')) + sum(
                        department_sec.settlement_ids.mapped('total_budget_expense')) - self.tour_id.total_budget_expense
                    remaining_amount = department_sec.budget_amount - spent_amount
                    if remaining_amount < total_tour_amount:
                        raise ValidationError(
                            'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
                elif department_div:
                    spent_amount = sum(department_div.tour_ids.mapped('total_budget_expense')) + sum(
                        department_div.settlement_ids.mapped('total_budget_expense')) - self.tour_id.total_budget_expense
                    remaining_amount = department_div.budget_amount - spent_amount
                    if remaining_amount < total_tour_amount:
                        raise ValidationError(
                            'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
                elif department_dep:
                    spent_amount = sum(department_dep.tour_ids.mapped('total_budget_expense')) + sum(
                        department_dep.settlement_ids.mapped(
                            'total_budget_expense')) - self.tour_id.total_budget_expense
                    remaining_amount = department_dep.budget_amount - spent_amount
                    if remaining_amount < total_tour_amount:
                        raise ValidationError(
                            'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
                else:
                    raise ValidationError('No Budget Data Found. Please Contact Your PM/RA For Further Information.')
        self.env.user.notify_success("Settlement Applied Successfully.")

    @api.multi
    def confirm_approve_with_additional_expenses(self):
        '''launch remark form'''
        form_view_id = self.env.ref("kw_tour.view_kw_tour_settlement_approve_remark_form").id
        return {
            'name': 'Remarks',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_settlement',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'nodestroy': True,
        }

    @api.multi
    def _compute_budget_limit_crossed(self):
        for record in self:
            data = self.env['account.fiscalyear'].sudo().search([
                ('date_start', '<=', record.date_travel),
                ('date_stop', '>=', record.date_travel)
            ]).mapped('id')
            record.budget_limit_crossed = False
            if record.project_id and record.budget_head_id:
                budget = self.env['kw_tour_project_budget'].sudo().search(
                    [('project_id', '=', record.project_id.id),
                     ('budget_head_id', '=', record.budget_head_id.id),

                     ],
                    limit=1)
                if budget.budget_perc > budget.threshold_limit:
                    record.budget_limit_crossed = True

    @api.multi
    def _compute_project_budget(self):
        for record in self:
            record.project_budget_id = False
            record.treasury_budget_id =False
            data = self.env['account.fiscalyear'].sudo().search([
                ('date_start', '<=', record.date_travel),
                ('date_stop', '>=', record.date_travel)
            ]).mapped('id')
            if record.tour_type_id.name == 'Project' and record.project_type == '70' and record.project_id and record.budget_head_id and record.state != 'Draft' and record.tour_id.cancellation_status is False and record.tour_id.settlement_applied:
                project_budget = self.env['kw_tour_project_budget'].sudo().search(
                    [('budget_head_id', '=', record.budget_head_id.id),
                     ('project_id', '=', record.project_id.id),
                     ], limit=1)
                if project_budget:
                    record.project_budget_id = project_budget.id
            else:
                if record.tour_id.blocked_department_id and record.state not in ['Draft', 'Rejected', 'Cancelled']:
                    record.treasury_budget_id = record.tour_id.blocked_department_id
                else:
                    data = self.env['account.fiscalyear'].sudo().search([
                        ('date_start', '<=', record.tour_id.date_travel),
                        ('date_stop', '>=', record.tour_id.date_travel)
                    ]).mapped('id')
                    if record.state not in ['Draft', 'Rejected', 'Cancelled']:
                        employee = record.tour_id.create_uid.employee_ids
                        sec_data = self.env['kw_tour_treasury_budget'].sudo().search([
                            ('fiscal_year_id', 'in', data),
                            ('department_id', '=', employee.section.id),
                            ('currency_id', '=', record.tour_id.currency_id.id)
                        ])
                        div_data = self.env['kw_tour_treasury_budget'].sudo().search([
                            ('fiscal_year_id', 'in', data),
                            ('department_id', '=', employee.division.id),

                            ('currency_id', '=', record.tour_id.currency_id.id)
                        ])
                        dep_data = self.env['kw_tour_treasury_budget'].sudo().search([
                            ('fiscal_year_id', 'in', data),
                            ('department_id', '=', employee.department_id.id),
                            ('currency_id', '=', record.tour_id.currency_id.id)
                        ])
                        if employee.section and sec_data:
                            record.treasury_budget_id = sec_data.id
                        elif employee.division and div_data:
                            record.treasury_budget_id = div_data.id
                        elif employee.department_id and dep_data:
                            record.treasury_budget_id = dep_data.id

    @api.depends('total_domestic', 'total_international',)
    def _get_total_budget_expense(self):
        for record in self:
            record.total_budget_expense = record.total_domestic + (record.total_international * record.api_exchange_rate)

    # def _auto_init(self):
    #     super(TourSettlement, self)._auto_init()
    #     self.env.cr.execute("delete from kw_tour_travel_ticket where settlement_id is not null")
    #     self.env.cr.execute("update kw_tour_settlement set travel_arrangement = kw_tour_details.travel_arrangement from kw_tour_details join kw_tour on kw_tour.id = kw_tour_details.tour_id where kw_tour.id = kw_tour_settlement.tour_id")
    #     self.env.cr.execute("insert into kw_tour_travel_ticket (settlement_id, booking_date, travel_mode_id, currency_id, cost, document, document_name) select kts.id, ktd.from_date, ktd.travel_mode_id, ktd.currency_id, ktd.cost, ktd.document, ktd.document_name from kw_tour_details ktd, kw_tour_settlement kts where kts.tour_id = ktd.tour_id and ktd.travel_mode_id is not null and ktd.currency_id is not null")

    def _get_tour_approver(self):
        approver = self.employee_id and self.employee_id.parent_id or False
        # approver_id = self.check_parent_sort_(self.tour_id.employee_id)
        # # above_m8_grade = ['M8', 'M9', 'M10', 'E1', 'E2', 'E3', 'E4', 'E5']
        # send_mail = False
        # if self.settlement_detail_ids:
        #     for rec in self.settlement_detail_ids:
        #         if rec.expense_id.code in ['ta', 'hra'] and rec.amount_claiming > rec.amount_actual:
        #             send_mail = True
        # if self.additional_expenses_ids:
        #     send_mail = True
        # if send_mail == True:
        #     approver = approver_id
        if self.tour_type_id.code == 'project':
            if self.actual_project_id:
                if self.actual_project_id.emp_id.id == self.employee_id.id \
                        and self.actual_project_id.reviewer_id.id != self.employee_id.id:
                    approver = self.actual_project_id.reviewer_id or False
                elif self.actual_project_id.emp_id.id != self.employee_id.id \
                        and self.actual_project_id.reviewer_id.id != self.employee_id.id:
                    approver = self.actual_project_id.emp_id or False
        return approver

    @api.onchange('tour_id')
    def onchange_tour_id(self):
        if self.tour_id and self.tour_id.travel_ticket_ids:
            self.travel_ticket_ids = False
            self.travel_ticket_ids = [[0, 0, {'booking_date': ticket_booking.booking_date,
                                              'travel_mode_id': ticket_booking.travel_mode_id.id,
                                              'currency_id': ticket_booking.currency_id.id,
                                              'cost': ticket_booking.cost,
                                              'document': ticket_booking.document,
                                              'document_name': ticket_booking.document_name}] for ticket_booking in
                                      self.tour_id.travel_ticket_ids]
        if self.tour_id and self.tour_id.travel_prerequisite_ids:
            self.travel_prerequisite_ids = False
            self.travel_prerequisite_ids = [[0, 0, {'travel_prerequisite_id': prerequisite.travel_prerequisite_id.id,
                                                    'amount': prerequisite.amount,
                                                    'currency_id': prerequisite.currency_id.id,
                                                    'document': prerequisite.document,
                                                    'document_name': prerequisite.document_name}] for prerequisite in
                                            self.tour_id.travel_prerequisite_ids]

    @api.depends('tour_id')
    @api.multi
    def compute_settlement_completed_tours(self):
        for settlement in self:
            employee = settlement.employee_id or settlement._default_employee()
            settled_tours = self.search([('employee_id', '=', employee.id), ('state', '!=', 'Rejected')])
            tour_ids = settled_tours.mapped('tour_id').ids
            settlement.update({'settled_tour_ids': [[6, 0, tour_ids]]})

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

    @api.depends('state')
    @api.multi
    def compute_pending_at(self):
        for record in self:
            if record.state == 'Applied':
                approver = record._get_tour_approver()
                # record.pending_at = record.employee_id.parent_id and record.employee_id.parent_id.name or False
                record.pending_at = approver and approver.name or False
            elif record.state in ['Approved','Granted']:
                finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users.mapped('name')
                record.pending_at = ','.join(finance_users)
            elif record.state == 'Forwarded':
                record.pending_at = record.final_approver_id.name

    @api.multi
    def action_view_travel_details(self):
        ''' RETURN TRAVEL DETAILS BY TOUR ID'''
        return {
            'name': 'Travel Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_travel_details',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': self.env.ref('kw_tour.view_kw_tour_travel_details_tree').id,
            'context': {'create':False,'edit':False,'import':False},
            'target': 'new',
            'domain': [('id', 'in', self.tour_id.travel_detail_ids.ids)]
        }

    @api.multi
    def action_view_accomodation_details(self):
        return {
            'name': 'Accommodation Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_accomodation',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': self.env.ref('kw_tour.view_kw_tour_accomodation_details_tree').id,
            'context': {'create': False, 'edit': False, 'import': False},
            'target': 'new',
            'domain': [('id', 'in', self.tour_id.accomodation_ids.ids)]
        }

    @api.constrains('tour_id', 'tour_detail_ids', 'settlement_detail_ids', 'travel_ticket_ids',
                    'travel_prerequisite_ids', 'additional_expenses_ids')
    def validate_settlement_detail(self):
        # user_timezone = pytz.timezone(self.env.user.tz or 'UTC')
        for settlement in self:
            settlement.calculate_expense_with_head()
            if settlement.tour_id:

                existing_settlement = self.search([('tour_id','=',settlement.tour_id.id),('state','!=','Rejected')]) - settlement
                if existing_settlement:
                    raise ValidationError(f"There is already a settlement for tour {existing_settlement[0].tour_id.code} in '{existing_settlement[0].state}' state.\n Please try with another tour.")

                if not settlement.settlement_detail_ids:
                    raise ValidationError("Please add settlement details.")

            if settlement.tour_detail_ids:
                start_date = min(settlement.tour_detail_ids.mapped('from_date')) #.astimezone(user_timezone).date()
                end_date = max(settlement.tour_detail_ids.mapped('to_date')) #.astimezone(user_timezone).date()

                for detail in settlement.settlement_detail_ids:
                    if detail.to_date < detail.from_date:
                        raise ValidationError("Settlement to date can't be less than from date.")

                    if not (start_date <= detail.from_date <= end_date) or not (start_date <= detail.to_date <= end_date):
                        raise ValidationError("Settlement from date and to date must be between journey date(s).")

            if settlement.tour_id and settlement.settlement_detail_ids:
                '''validate for DA to be mandatory'''
                da_expense = settlement.settlement_detail_ids.filtered(lambda r: r.expense_id.code == 'da')
                if not da_expense:
                    raise ValidationError("Please apply DA in settlement details.")

                '''validate for invalid journey date '''
                city_dict = settlement.tour_id.get_city_dates()
                '''validate against inr and usd'''
                for detail in settlement.settlement_detail_ids:
                    if detail.amount_claiming < 1.00:
                        raise ValidationError("Claimed amount should be greater than 0.")
                    all_dates = settlement.tour_id.generate_days_with_from_and_to_date(detail.from_date, detail.to_date)
                    not_in_city_dates = set(all_dates) - set(city_dict[detail.city_id.id])

                    if not_in_city_dates:
                        raise ValidationError(f"{list(not_in_city_dates)[0].strftime('%d-%b-%Y')} is not in {detail.city_id.name} visited dates.")

                    # HRA validation is removed as requested (17 March 2021) [Gouranga]
                    # '''validate for hra category with corresponding percentage'''
                    # if detail.expense_id.code == 'hra':
                    #     if detail.amount_claiming > detail.amount_actual:
                    #         raise ValidationError(
                    #             f"More than eligible amount can't be applied in case of HRA.")

                    if detail.expense_id.code == 'da':
                        approver = settlement._get_tour_approver()
                        if detail.amount_claiming > detail.amount_actual and approver:
                            raise ValidationError("More than available percentage amount can't be applied in case of DA.")

                        ''' validate da can't be applied within same date range more than once '''

                        tour_obj                = self.env['kw_tour']
                        da_date_set             = set(tour_obj.generate_days_with_from_and_to_date(detail.from_date,detail.to_date))
                        # print(da_date_set, '======22222222222=====>>>>')
                        da_except_current_da    = settlement.settlement_detail_ids.filtered(lambda r: r.expense_id == detail.expense_id) - detail
                        # print(da_except_current_da,'==========11111111111')
                        da_within_same_date_range = da_except_current_da.filtered(lambda r: len(set(tour_obj.generate_days_with_from_and_to_date(r.from_date,r.to_date)) & da_date_set) > 0)
                        # print(da_within_same_date_range, '====>>>>')
                        if da_within_same_date_range:
                            raise ValidationError("DA within same date range can't be applied.")

                    if settlement.state in ['Draft', 'Applied'] and detail.expense_id.code == 'misc':
                        approver = settlement._get_tour_approver()
                        if detail.amount_claiming > detail.amount_actual and approver and detail.currency_id.id == detail.settlement_id.tour_id.create_uid.employee_ids.company_id.currency_id.id:
                            raise ValidationError(
                                "You are not allowed to apply more than the entitlement.")

                    # if detail.expense_id.code == 'ta':
                    #     # approver = settlement._get_tour_approver()
                    #     # if detail.amount_claiming > detail.amount_actual and approver:
                    #     #     raise ValidationError("More than available percentage amount can't be applied in case of DA.")
                    #     ''' validate ta can't be applied within same date range more than once '''
                    #     tour_obj                = self.env['kw_tour']
                    #     ta_date_set             = set(tour_obj.generate_days_with_from_and_to_date(detail.from_date,detail.to_date))
                    #     ta_except_current_da    = settlement.settlement_detail_ids.filtered(lambda r: r.expense_id == detail.expense_id) - detail
                    #     ta_within_same_date_range = ta_except_current_da.filtered(lambda r: len(set(tour_obj.generate_days_with_from_and_to_date(r.from_date,r.to_date)) & ta_date_set) > 0)
                    #     if ta_within_same_date_range:
                    #         raise ValidationError("TA within same date range can't be applied.")

                    # if detail.expense_id.code == 'hra':
                    #     # approver = settlement._get_tour_approver()
                    #     # if detail.amount_claiming > detail.amount_actual and approver:
                    #     #     raise ValidationError("More than available percentage amount can't be applied in case of DA.")
                    #     ''' validate ta can't be applied within same date range more than once '''
                    #     tour_obj                = self.env['kw_tour']
                    #     hra_date_set             = set(tour_obj.generate_days_with_from_and_to_date(detail.from_date,detail.to_date))
                    #     hra_except_current_da    = settlement.settlement_detail_ids.filtered(lambda r: r.expense_id == detail.expense_id) - detail
                    #     hra_within_same_date_range = hra_except_current_da.filtered(lambda r: len(set(tour_obj.generate_days_with_from_and_to_date(r.from_date,r.to_date)) & hra_date_set) > 0)
                    #     if hra_within_same_date_range:
                    #         raise ValidationError("HRA within same date range can't be applied.")
                total_add_exp = 0
                if settlement.additional_expenses_ids:
                    for exp in settlement.additional_expenses_ids:
                        if exp.currency_id.name == settlement.tour_id.employee_id.user_id.company_id.currency_id.name:
                            total_add_exp += exp.amount
                        # elif exp.currency_id.name == 'USD':
                        #     total_add_exp += exp.amount * settlement.tour_id.api_exchange_rate
                above_m8_grade = ['M8', 'M9', 'M10', 'E1', 'E2', 'E3', 'E4', 'E5']
                if settlement.state in ['Draft', 'Applied'] and settlement.tour_id.employee_id.grade.name in above_m8_grade and total_add_exp > 10000:
                    raise ValidationError(
                        "You are not allowed to apply more than the entitlement.")
                if settlement.state in ['Draft', 'Applied'] and settlement.tour_id.employee_id.grade.name not in above_m8_grade and total_add_exp > 5000:
                    raise ValidationError(
                        "You are not allowed to apply more than the entitlement.")
            for index, ticket_detail in enumerate(settlement.travel_ticket_ids):
                if ticket_detail.cost <= 0:   #settlement.travel_arrangement == 'Self'
                    raise ValidationError(f"Ticket cost should not be zero in ticket details at row {index + 1}.")

            for index, prerequisite in enumerate(settlement.travel_prerequisite_ids):
                if prerequisite.amount <= 0:
                    raise ValidationError(f"Amount should not be zero in travel prerequisite at row {index + 1}.")

            # if settlement.budget_head_id and settlement.state in ('Draft', 'Applied'):
            #     emp_create_id = settlement.tour_id.create_uid.id
            #     empls_id =  self.env['hr.employee'].search([('user_id', '=', emp_create_id)], limit=1)
            #     emp_kw_id = empls_id.kw_id or 0
            #     project_url = self.env.ref('kw_tour.kw_tour_budget_url_system_parameter').sudo().value
            #     header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
            #     data = json.dumps({"userId": emp_kw_id, "BudgetHeadID": settlement.tour_id.budget_head_id.kw_id})
            #     resp_result = requests.post(project_url, headers=header, data=data)
            #     resp = json.loads(resp_result.text)
            #     budget_amount = 0
            #     if resp.get('retBudgetDa', False):
            #         if settlement.tour_id.tour_type_id.code == 'project' and settlement.tour_id.project_type == '70':
            #             if all(int(module_dict.get('ModuleID')) != settlement.tour_id.project_id.kw_workorder_id for module_dict in
            #                    resp['retBudgetDa']):
            #                 raise ValidationError("No budget data found")
            #         else:
            #             if all(int(module_dict.get('Budget_Head_ID')) != settlement.tour_id.budget_head_id.kw_id for module_dict in
            #                    resp['retBudgetDa']):
            #                 raise ValidationError("No budget data found")
            #         for module_dict in resp['retBudgetDa']:
            #             if settlement.tour_id.tour_type_id.code == 'project' and settlement.tour_id.project_type == '70':
            #                 if int(module_dict.get('ModuleID')) == settlement.tour_id.project_id.kw_workorder_id:
            #                     budget_amount = module_dict.get('Total_BudgetAmt')
            #             elif settlement.tour_id.tour_type_id.code == 'project' and settlement.tour_id.project_type != '70':
            #                 budget_amount = module_dict.get('Total_BudgetAmt')
            #             elif settlement.tour_id.tour_type_id.code != 'project':
            #                 budget_amount = module_dict.get('Total_BudgetAmt')
            #     elif self.tour_type_id.code in ['events', 'training','relocation', 'interviews']:
            #         pass
            #     else:
            #         raise ValidationError("No budget data found")
            #     if float(budget_amount) < 1 and self.tour_type_id.code not in ['events', 'training','relocation', 'interviews']:
            #         raise ValidationError("Zero Balance in budget")
            #
            #     # tour settled
            #     tour_settlements = self.env['kw_tour_settlement'].sudo().search(
            #         [('budget_head_id', '=', settlement.budget_head_id.id),
            #          ('project_id', '=', settlement.project_id.id), ('state', '!=', 'Rejected')]) - settlement
            #     total_settlement_amount = sum(tour_settlements.mapped('total_budget_expense'))
            #
            #     # unsettled tours
            #     unsettled_tours = self.env['kw_tour'].sudo().search([('budget_head_id', '=', settlement.budget_head_id.id),
            #                                                          ('project_id', '=', settlement.project_id.id),
            #                                                          ('state', 'not in', ('Rejected', 'Cancelled')),
            #                                                          ('id', '!=', settlement.tour_id.id)])
            #     unsettled_tour_amount = sum(unsettled_tours.filtered(
            #         lambda r: r.cancellation_status == False and r.settlement_applied == False).mapped(
            #         'total_budget_expense'))
            #
            #     if settlement.actual_project_id:
            #         total_amount_spent = float(total_settlement_amount) + float(unsettled_tour_amount)
            #         project_budget = self.env['kw_tour_project_budget'].sudo().search(
            #             [('project_id', '=', settlement.project_id.id), ('budget_head_id', '=', settlement.budget_head_id.id)],
            #             limit=1)
            #         perc_80 = float(budget_amount) * project_budget.threshold_limit / 100
            #         if total_amount_spent >= perc_80:
            #             raise ValidationError("Cannot apply settlement.\n"
            #                                   "Selected budget has crossed threshold limit.\n"
            #                                   "Contact your project manager to increase budget")
            #     available_balance = float(budget_amount) - float(total_settlement_amount) - float(
            #         unsettled_tour_amount) - float(settlement.total_budget_expense)
            #
            #     if available_balance < 1 and self.tour_type_id.code == 'project':
            #         raise ValidationError("Insufficient Balance in Budget")
            city_li = []
            for rec in settlement.tour_detail_ids:
                if rec.accomodation_arrangement == 'Company':
                    city_li.append(rec.to_city_id.id)
            for recc in settlement.settlement_detail_ids:
                if recc.city_id.id in city_li and recc.expense_id.code == 'hra':
                    raise ValidationError(f'Due to accomodation arrangement of company. you can\'t apply HRA for {recc.city_id.name}.')

    @api.constrains("payment_date")
    def validate_payment_date(self):
        for settlement in self:
            if settlement.grant_date and not settlement.payment_date >= settlement.grant_date:
                raise ValidationError("Payment date must be after settlement grant date.")

    @api.multi
    @api.depends('tour_id', 'settlement_detail_ids', 'settlement_detail_ids.currency_id',
                 'settlement_detail_ids.amount_claiming', 'additional_expenses_ids')
    def compute_total(self):
        for claim in self:
            # print(claim.tour_id.sudo().employee_id.user_id.company_id.currency_id.name, '==============>>>>check.')
            domestic_amount, international_amount = 0, 0
            domestic_amount += sum(claim.settlement_detail_ids.filtered(lambda r: r.currency_id.name == claim.tour_id.sudo().employee_id.user_id.company_id.currency_id.name).mapped('amount_claiming'))
            international_amount += sum(claim.settlement_detail_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('amount_claiming'))

            if claim.travel_arrangement == 'Self' and claim.travel_ticket_ids:   #claim.travel_arrangement == 'Self' and
                domestic_amount += sum(claim.travel_ticket_ids.filtered(lambda r: r.currency_id.name == claim.tour_id.sudo().employee_id.user_id.company_id.currency_id.name).mapped('cost'))
                international_amount += sum(claim.travel_ticket_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('cost'))

            domestic_amount += sum(claim.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == claim.tour_id.sudo().employee_id.user_id.company_id.currency_id.name).mapped('amount'))
            international_amount += sum(claim.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('amount'))

            domestic_amount += sum(claim.additional_expenses_ids.filtered(
                lambda r: r.currency_id.name == claim.tour_id.sudo().employee_id.user_id.company_id.currency_id.name).mapped(
                'amount'))
            international_amount += sum(
                claim.additional_expenses_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('amount'))

            claim.total_domestic = domestic_amount
            claim.total_international = international_amount

            total_inr = claim.total_domestic - claim.advance_inr
            total_usd = claim.total_international - claim.advance_usd

            claim.paid_domestic = total_inr < 0 and total_inr or 0
            claim.paid_international = total_usd < 0 and total_usd or 0

            claim.receivable_inr = total_inr > 0 and total_inr or 0
            claim.receivable_usd = total_usd > 0 and total_usd or 0

            # if claim.travel_arrangement != 'Self':
            #     claim.receivable_inr =  claim.receivable_inr - sum(claim.travel_ticket_ids.filtered(lambda r: r.currency_id.name == claim.tour_id.employee_id.user_id.company_id.currency_id.name).mapped('cost'))
            #     claim.receivable_usd = claim.receivable_usd - sum(claim.travel_ticket_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('cost'))

    @api.multi
    def calculate_expense_with_head(self):
        domestic_amount, international_amount = 0, 0
        domestic_amount += sum(
            self.settlement_detail_ids.filtered(lambda r: r.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name).mapped('amount_claiming'))
        international_amount += sum(
            self.settlement_detail_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('amount_claiming'))

        if self.travel_arrangement == 'Self' and self.travel_ticket_ids:
            domestic_amount += sum(
                self.travel_ticket_ids.filtered(lambda r: r.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name).mapped('cost'))
            international_amount += sum(
                self.travel_ticket_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('cost'))

        domestic_amount += sum(
            self.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name).mapped('amount'))
        international_amount += sum(
            self.travel_prerequisite_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('amount'))

        domestic_amount += sum(
            self.additional_expenses_ids.filtered(
                lambda r: r.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name).mapped(
                'amount'))
        international_amount += sum(
            self.additional_expenses_ids.filtered(lambda r: r.currency_id.name == "USD").mapped('amount'))

        # self.total_domestic = domestic and sum(domestic.mapped('amount_claiming')) or 0
        # self.total_international = international and sum(international.mapped('amount_claiming')) or 0

        self.total_domestic = domestic_amount
        self.total_international = international_amount

        total_inr = self.total_domestic - self.advance_inr
        total_usd = self.total_international - self.advance_usd

        self.paid_domestic = total_inr < 0 and total_inr or 0
        self.paid_international = total_usd < 0 and total_usd or 0

        self.receivable_inr = total_inr > 0 and total_inr or 0
        self.receivable_usd = total_usd > 0 and total_usd or 0

        all_expenses = self.settlement_detail_ids.mapped('expense_id')
        expense_dict = {expense.id: {'inr': 0, 'usd': 0, 'domestic_cur':0, 'usd_cur':0} for expense in all_expenses}

        for exp in all_expenses:
            exp_records = self.settlement_detail_ids.filtered(lambda r: r.expense_id == exp)
            for rec in exp_records:
                if rec.currency_id and rec.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name:
                    expense_dict[exp.id]['inr'] += rec.amount_claiming
                    expense_dict[exp.id]['domestic_cur'] = rec.currency_id.id
                elif rec.currency_id and rec.currency_id.name == "USD":
                    expense_dict[exp.id]['usd'] += rec.amount_claiming
                    expense_dict[exp.id]['usd_cur'] = self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id

        # ticket cost
        ticket_inr, ticket_usd = 0, 0
        domestic_cur = 0
        international_cur = 0
        if self.travel_ticket_ids:    #self.tour_id.travel_arrangement == 'Self' and
            for anci_exp in self.travel_ticket_ids:
                if anci_exp.currency_id and anci_exp.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name:
                    ticket_inr += anci_exp.cost
                    domestic_cur = anci_exp.currency_id.id
                elif anci_exp.currency_id and anci_exp.currency_id.name == "USD":
                    ticket_usd += anci_exp.cost
                    international_cur += self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id

        # prerequisite
        travel_prerequisite_expenses = self.travel_prerequisite_ids.mapped('travel_prerequisite_id')
        travel_prerequisite_dict = {prerequisite.id: {'inr': 0, 'usd': 0} for prerequisite in
                                    travel_prerequisite_expenses}

        for travel_prerequisite_exp in travel_prerequisite_expenses:
            prerequisite_records = self.travel_prerequisite_ids.filtered(
                lambda r: r.travel_prerequisite_id == travel_prerequisite_exp)
            for pre_exp in prerequisite_records:
                if pre_exp.currency_id and pre_exp.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name:
                    travel_prerequisite_dict[travel_prerequisite_exp.id]['inr'] += pre_exp.amount
                elif pre_exp.currency_id and pre_exp.currency_id.name == "USD":
                    travel_prerequisite_dict[travel_prerequisite_exp.id]['usd'] += pre_exp.amount

        # additional expenses
        additional_expenses_inr, additional_expenses_usd = 0, 0
        add_domestic_cur = 0
        add_international_cur = 0
        if self.additional_expenses_ids:
            for addi_exp in self.additional_expenses_ids:
                if addi_exp.currency_id and addi_exp.currency_id.name == self.tour_id.employee_id.user_id.company_id.currency_id.name:
                    additional_expenses_inr += addi_exp.amount
                    domestic_cur = addi_exp.currency_id.id
                elif addi_exp.currency_id and addi_exp.currency_id.name == "USD":
                    additional_expenses_usd += addi_exp.amount
                    international_cur += self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id

        self.total_expense_ids = False
        self.total_expense_ids = [[0, 0, {'expense_id': key,
                                          'amount_inr': value['inr'],
                                          'domestic_currency_id': value['domestic_cur'],
                                          'amount_usd': value['usd'],
                                          'international_currency_id': value['usd_cur']}] for key, value in expense_dict.items()]

        if self.travel_ticket_ids:   #self.tour_id.travel_arrangement == 'Self' and
            self.total_expense_ids = [[0, 0, {'expense_id': self.env.ref('kw_tour.kw_tour_expense_type_ticket_cost').id,
                                              'domestic_currency_id': domestic_cur,
                                              'international_currency_id': international_cur,
                                              'amount_inr': ticket_inr,
                                              'amount_usd': ticket_usd}]]

        self.total_expense_ids = [[0, 0, {'travel_prerequisite_id': key,
                                          'amount_inr': value['inr'],
                                          'amount_usd': value['usd']}] for key, value in travel_prerequisite_dict.items()]
        if self.additional_expenses_ids:
            self.total_expense_ids = [[0, 0, {'expense_id': self.env.ref('kw_tour.kw_tour_expense_type_additional_expenses').id,
                                              'domestic_currency_id': domestic_cur,
                                              'international_currency_id': international_cur,
                                              'amount_inr': additional_expenses_inr,
                                              'amount_usd': additional_expenses_usd}]]

    def return_to_settlement_take_action(self):
        tree_view_id = self.env.ref('kw_tour.view_kw_tour_settlement_take_action_tree').id
        form_view_id = self.env.ref('kw_tour.view_kw_tour_settlement_take_action_form').id

        return {
            'name': 'Take Action',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'kw_tour_settlement',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'context': {"access_label_check": 1},
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        }

    @api.multi
    def action_settlement_approve(self):
        remark = self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")
        self.write({'state': 'Approved',
                    'approver_id': False,
                    'final_approver_id': False,
                    # 'pending_status_at':False,
                    'remark': False,
                    'action_datetime': Datetime.now(),
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Approved'}]]
                    }, no_notify=True)

        self.message_post(body=f"Remark : {remark}")
        approver = self._get_tour_approver()
        template = self.env.ref('kw_tour.kw_tour_settlement_approved_mail')
        template.with_context(action_user = self.env.user,remark=remark, email=approver.work_email).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        notify_template = self.env.ref('kw_tour.kw_tour_settlement_approval_notification_mail_template')
        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name
        finance_users = literal_eval(self.env['ir.config_parameter'].sudo().get_param('tour_finance_users_l1_ids') or "[]")
        # finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
        mail_to = []
        if finance_users:
            emp = self.env['hr.employee'].sudo().search([('id', 'in', finance_users)])
            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
        emails = ",".join(mail_to) or ''
        # finance_users_emails = ','.join(finance_users.mapped("employee_ids.work_email"))
        notify_template.with_context(
            remark=remark,
            email_users=emails,
            email_cc_users=self.employee_id.work_email,
            action_user=uname).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        user.notify_success("Tour Settlement Approved Successfully.")

        # action_id = self.env.ref('kw_tour.action_kw_tour_settlement_take_action_act_window').id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_settlement&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_settlement_take_action()

    @api.multi
    def action_settlement_forward(self):
        remark = self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")
        approver = self.approver_id and self.approver_id.id or False

        self.write({'state': 'Forwarded',
                    'approver_id': False,
                    'final_approver_id': approver,
                    # 'forward': False,
                    # 'pending_status_at':False,
                    'action_datetime':Datetime.now(),
                    'remark': False,
                    'action_log_ids': [[0, 0, {'remark': remark,'state': 'Forwarded'}]]
                    }, no_notify=True)

        self.message_post(body=f"Remark : {remark}")
        approver = self._get_tour_approver()
        template = self.env.ref('kw_tour.kw_tour_settlement_forwarded_user_mail')
        template.with_context(action_user=self.env.user, remark=remark, email=approver.work_email).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Tour Settlement Forwarded Successfully.")
        # action_id = self.env.ref('kw_tour.action_kw_tour_settlement_take_action_act_window').id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_settlement&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_settlement_take_action()

    @api.multi
    def action_settlement_finance_settle(self):
        remark = self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")

        self.write({'state': 'Granted',
                    'approver_id': False,
                    'final_approver_id': False,
                    'remark': False,
                    'action_datetime': Datetime.now(),
                    'grant_date': date.today(),
                    'grant_datetime': Datetime.now(),
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Granted'}]]
                    }, no_notify=True)
        self.tour_id.write({'settlement_id': self.id})

        self.message_post(body=f"Remark : {remark}")
        approver = self._get_tour_approver()
        restrict_emp_ids = literal_eval(
            self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_approval_email_ids') or "[]")
        cc_email = ''
        if approver:
            approver -= approver.filtered(lambda r: r.id in restrict_emp_ids)
            if approver:
                cc_email = approver.work_email
        template = self.env.ref('kw_tour.kw_tour_settlement_settled_mail')
        template.with_context(action_user=self.env.user, remark=remark, email=cc_email).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Tour Settlement Granted Successfully.")
        # action_id = self.env.ref(
        #     'kw_tour.action_kw_tour_settlement_take_action_act_window').id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_settlement&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_settlement_take_action()

    @api.multi
    def action_settlement_paid(self):
        remark = self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")

        self.write({'state': 'Payment Done',
                    'remark': False,
                    'action_datetime': Datetime.now(),
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Payment Done'}]]
                    }, no_notify=True)
        self.message_post(body=f"Remark : {remark}")

        self.env.user.notify_success("Tour Settlement Payment Completed Successfully.")
        # action_id = self.env.ref('kw_tour.action_kw_tour_settlement_payment_act_window').id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_settlement&view_type=list',
        #     'target': 'self',
        # }
        tree_view_id = self.env.ref('kw_tour.view_kw_tour_settlement_payment_tree').id
        form_view_id = self.env.ref('kw_tour.view_kw_tour_settlement_payment_form').id

        return {
            'name': 'Settlement Payment',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'kw_tour_settlement',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'domain': [('state', '=', 'Granted')],
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        }

    @api.multi
    def action_settlement_reject(self):
        remark = self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")
        self.write({'state': 'Rejected',
                    'approver_id': False,
                    # 'pending_status_at':False,
                    'final_approver_id': False,
                    'action_datetime': Datetime.now(),
                    'remark': False,
                    'action_log_ids': [[0, 0, {'remark': remark, 'state': 'Rejected'}]]
                    }, no_notify=True)

        self.message_post(body=f"Remark : {remark}")
        approver = self._get_tour_approver()
        restrict_emp_ids = literal_eval(
            self.env['ir.config_parameter'].sudo().get_param('tour_traveldesk_approval_email_ids') or "[]")
        cc_email = ''
        if approver:
            approver -= approver.filtered(lambda r: r.id in restrict_emp_ids)
            if approver:
                cc_email = approver.work_email
        template = self.env.ref('kw_tour.kw_tour_settlement_rejected_mail')
        template.with_context(action_user=self.env.user, remark=remark, email=cc_email).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Tour Settlement Rejected Successfully.")

        # action_id = self.env.ref(
        #     'kw_tour.action_kw_tour_settlement_take_action_act_window').id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_settlement&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_settlement_take_action()

    @api.multi
    def action_view_settle_claim(self):
        if self.settlement_claim_id:
            action_id = self.env.ref(
                'kw_tour.action_kw_tour_settlement_take_action_act_window').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_tour_settlement&view_type=list',
                'target': 'self',
            }
        else:
            raise ValidationError("No settlement claim found.")

    @api.multi
    def action_settlement_claim_view(self):
        view_id = self.env.ref('kw_tour.view_kw_tour_settlement_claim_wizard_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_settlement_claim_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_tour_id': self.tour_id.id,
                'default_settlement_id': self.id,
            }
        }

    @api.multi
    def button_take_action(self):
        view_id = self.env.ref('kw_tour.view_kw_tour_settlement_take_action_form').id

        if self.state in ['Granted', 'Payment Done']:
            view_id = self.env.ref('kw_tour.view_kw_tour_settlement_payment_form').id

        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_settlement',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
        }

    @api.multi
    def compute_own_access(self):
        for settlement in self:
            settlement.own_record = settlement.create_uid == self.env.user
            settlement.current_user = self.env.user
            if self._context.get('eos_ra_takeaction'):
                settlement.own_record = False

    @api.multi
    def compute_finance_access(self):
        for settlement in self:
            settlement.finance_access = self.env.user.has_group('kw_tour.group_kw_tour_finance')

    @api.multi
    def compute_ra_access(self):
        for tour in self:
            approver = tour._get_tour_approver()
            # if tour.employee_id and tour.employee_id.parent_id and tour.employee_id.parent_id.user_id == self.env.user:
            if tour.employee_id and approver and approver.user_id == self.env.user:
                tour.ra_access = True

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        query = f'''select kts.id from kw_tour_settlement kts
                    join kw_tour kt on kt.id = kts.tour_id
                    join project_project pj on pj.id = kt.actual_project_id
                    where pj.emp_id = kt.employee_id 
                    and pj.reviewer_id = {current_employee.id}::integer '''
        self._cr.execute(query)
        query_result = self._cr.fetchall()
        tour_reviewer_ids = [id_tuple[0] for id_tuple in query_result]

        query = f'''select kts.id from kw_tour_settlement kts
                    join kw_tour kt on kt.id = kts.tour_id
                    join project_project pj on pj.id = kt.actual_project_id
                    where pj.reviewer_id = kt.employee_id '''
        self._cr.execute(query)
        query_result = self._cr.fetchall()
        tour_ra_ids = [id_tuple[0] for id_tuple in query_result]

        query = f'''select kts.id from kw_tour_settlement kts
                    join kw_tour kt on kt.id = kts.tour_id
                    join project_project pj on pj.id = kt.actual_project_id
                    where pj.reviewer_id != kt.employee_id and pj.emp_id != kt.employee_id 
                    and pj.emp_id = {current_employee.id}::integer '''
        self._cr.execute(query)
        query_result = self._cr.fetchall()
        tour_pm_ids = [id_tuple[0] for id_tuple in query_result]
        if self._context.get('access_label_check'):
            c_suit_emp = self.env['kw_tour_c_suite'].sudo().search([]).filtered(lambda x: self.env.user.employee_ids.id in x.employee_ids.ids)
            if self.env.user.has_group('kw_tour.group_kw_tour_finance'):
                args += ['|', ('state', '=', 'Approved'),
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
            elif self.env.user.has_group('kw_tour.group_kw_tour_c_suite_user'):
                args += ['|', '|', '|',
                         '&', '&',('state', 'in', ['Forwarded', 'Applied']), ('final_approver_id.user_id', '=', self.env.user.id),('employee_id.department_id','in', c_suit_emp.mapped('department_id').ids),

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
                args += ['|', '|', '|',
                         '&','&', ('state', 'in', ['Forwarded']), ('final_approver_id.user_id', '=', self.env.user.id),('c_suite_boolean','=',False),

                         '&', '&','&', ('state', '=', 'Applied'), ('employee_id.parent_id.user_id', '=', self.env.user.id),('c_suite_boolean','=',False),
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
        if self._context.get('access_view_status'):
            if self.env.user.has_group('kw_tour.group_kw_tour_finance'):
                args += [('state', '!=', 'Draft')]
            else:
                args += ['&', ('state', '!=', 'Draft'),
                         '|', '|', '|', ('create_uid', '=', self.env.user.id),

                         '&',('employee_id.parent_id.user_id', '=', self.env.user.id),
                         '|',
                         ('tour_type_id.code', '!=', 'project'),
                         '&',
                         ('tour_type_id.code', '=', 'project'),
                         '|',
                         ('id', 'in', tour_ra_ids),
                         ('project_type', '=', '3'),

                         '&', ('tour_type_id.code', '=', 'project'),
                         ('id', 'in', tour_pm_ids),

                         '&', ('tour_type_id.code', '=', 'project'),
                         ('id', 'in', tour_reviewer_ids)
                         ]
        return super(TourSettlement, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def create(self, values):
        result = super(TourSettlement, self).create(values)
        self.env.user.notify_success("Settlement Created Successfully.")
        return result

    @api.multi
    def write(self, values,no_notify=False):
        result = super(TourSettlement, self).write(values)
        if len(values) == 1:
            if 'remark' in values or 'total_expense_ids' in values or 'total_domestic' in values:
                no_notify = True
            elif 'total_international' in values or 'paid_domestic' in values or 'paid_international' in values \
                    or 'receivable_inr' in values or 'receivable_usd' in values:
                no_notify = True
        elif len(values) == 2 and (('remark' and 'approver_id' in values) or ('remark' and 'payment_date' in values)):
            no_notify = True
        if not no_notify:
            self.env.user.notify_success("Tour Settlement Updated Successfully.")
        return result

    @api.multi
    def action_view_settlement_details(self):
        return {
            'name': 'Tour Settlement Details',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'kw_tour_settlement_details',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('settlement_id', '=', self.id)],
            'context': {'create': False, 'edit': False, 'delete': False, 'duplicate': False, 'show_employee': False}
        }
        
    @api.multi
    def print_settlement_feedback(self):
        return self.env.ref('kw_tour.kw_tour_settlement_claim_report').report_action(self)