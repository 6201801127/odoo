from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from ast import literal_eval

class TourOthers(models.Model):
    _name = 'kw_tour_others'
    _description = "Group Tour"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'tour_type_id'

    def get_city_id(self):
        country_data2 = self.env['kw_tour_city'].sudo().search(
            [('company_id', '=', self.env.user.company_id.id)]).mapped('id')
        return [('id', '=', country_data2)]

    tour_type_new = fields.Many2one('kw_tour_type_new', string="Tour Type")
    tour_type_id = fields.Many2one('kw_tour_type', required=True, string="Type Of Tour")
    group_tour_code =  fields.Char(string="Group Tour No.", default="New", readonly="1")
    purpose = fields.Text("Purpose", required=True)
    date_travel = fields.Date("Date Of Travel", required=True)
    city_id = fields.Many2one('kw_tour_city', "Originating Place")
    to_city_id = fields.Many2one('kw_tour_city', "Destination Place", required=True, domain=get_city_id)
    date_return = fields.Date("Return Date", required=True)
    budget_head_id = fields.Many2one('kw_tour_budget_head', string="Budget Head", track_visibility='onchange', required=True)
    travel_arrangement = fields.Selection(string="Travel Arrangement",
                                          selection=[('Self', 'Self'), ('Company', 'Company')], required=True,
                                          default="Company")
    # tour_detail_ids = fields.One2many('kw_tour_others_details', 'tour_others_id', string="Tour Details")
    assign_tour_others_emp_ids = fields.One2many('kw_tour_others_assign_employee', 'tour_others_id', string="Add Employee", required=True)
    state = fields.Selection(string='Status',
                             selection=[('Draft', 'Draft'),
                                        ('Applied', 'Applied'),
                                        ('Approved', 'Approved')
                                        ], default='Draft')
    approver_btn_boolean = fields.Boolean(compute='get_approver_btn', store=False)
    travel_expense_details_ids = fields.One2many('kw_tour_travel_expense_details', 'tour_others_id',
                                                 string="Travel Expenses", )
    department_id = fields.Many2one('hr.department')
    total_budget_expense = fields.Float("Total Blocked Budget Expense", compute='_get_total_budget', store=True)
    can_apply_inr = fields.Boolean(string='Can Apply For Advance INR ?', compute="_compute_advance_inr_usd")
    can_apply_usd = fields.Boolean(string='Can Apply For Advance USD ?', compute="_compute_advance_inr_usd")
    api_exchange_rate = fields.Float('API Exchange Rate')
    blocked_department_id = fields.Many2one('kw_tour_treasury_budget', 'Blocked Department')

    @api.model
    def create(self, values):
        values['group_tour_code'] = self.env['ir.sequence'].next_by_code('self.group_tour_seq') or 'New'
        tour = super(TourOthers, self).create(values)
        self.env.user.notify_success("Group Tour created successfully.")
        return tour

    @api.constrains('tour_type_id', 'assign_tour_others_emp_ids','date_travel',
                    'date_return', 'city_id', 'travel_ticket_ids', 'travel_arrangement', 'budget_head_id')
    def _validate_tour_details(self):
        for tour in self:
            if tour.can_apply_usd is True:
                today_exchange_rate = self.env['kw_tour_exchange_rate'].search([('date', '=', tour.date_travel)],
                                                                               limit=1)
                if today_exchange_rate:
                    tour.api_exchange_rate = today_exchange_rate.rate
                else:
                    previous_exchange_rate = self.env['kw_tour_exchange_rate'].search(
                        [('date', '<', tour.date_travel)], limit=1)
                    if previous_exchange_rate:
                        tour.api_exchange_rate = previous_exchange_rate.rate
                    else:
                        raise ValidationError("No Exchange rate set for the date of travel.\n"
                                              "Contact Finance to set exchange rate.")


    @api.depends("assign_tour_others_emp_ids")
    @api.multi
    def _compute_advance_inr_usd(self):
        for tour in self:
            inr_expense = tour.travel_expense_details_ids.filtered(lambda r: r.amount_domestic > 0)
            usd_expense = tour.travel_expense_details_ids.filtered(lambda r: r.amount_international > 0)
            if inr_expense:
                tour.can_apply_inr = True
            if usd_expense:
                tour.can_apply_usd = True

    @api.depends('assign_tour_others_emp_ids', 'date_travel', 'date_return', 'city_id', 'to_city_id')
    def _get_total_budget(self):
        for record in self:
            p_amount_inr, p_amount_usd = 0, 0
            # if record.travel_arrangement == 'Self':
            #     p_amount_inr += sum(
            #         record.travel_ticket_ids.filtered(lambda r: r.currency_id.name == 'INR').mapped('cost'))
            #     p_amount_usd += sum(
            #         record.travel_ticket_ids.filtered(lambda r: r.currency_id.name == 'USD').mapped(
            #             'cost')) * record.api_exchange_rate
            p_amount_inr += sum(record.travel_expense_details_ids.mapped('amount_domestic'))
            p_amount_usd += sum(
                record.travel_expense_details_ids.mapped('amount_international')) * record.api_exchange_rate
            record.total_budget_expense = p_amount_inr + p_amount_usd


    @api.constrains('date_travel', 'date_return')
    def get_date_value(self):
        if self.date_travel > self.date_return:
            raise ValidationError('Date of return always greater than Date of Travel.')

    @api.onchange('assign_tour_others_emp_ids', 'date_travel', 'date_return', 'to_city_id')
    def calculate_expenses(self):
        if self.date_travel and self.date_return and self.to_city_id:
            ta_amout_domestic = 0
            ta_amount_international = 0
            da_amout_domestic = 0
            da_amount_international = 0
            misc_amout_domestic = 0
            misc_amount_international = 0
            hra_amount_domestic = 0
            hra_amount_international = 0
            ticket_cost_domestic = 0
            ticket_cost_international = 0
            li = []
            self.travel_expense_details_ids = False
            for rec in self.assign_tour_others_emp_ids:
                if rec.status != 'Rejected':
                    li.append(rec.status)
                    from_cities = rec.city_id
                    to_cities = rec.tour_others_id.to_city_id

                    all_cities = from_cities | to_cities

                    expenses = self.env['kw_tour_expense_type'].search([])

                    city_dict = {city.id: 0 for city in all_cities}
                    city_halt_dict = {city.id: 0 for city in all_cities}

                    days_expense_dict = {expen.id: {"inr": 0, "usd": 0} for expen in expenses}

                    city_dict[rec.tour_others_id.to_city_id.id] += (rec.tour_others_id.date_return - rec.tour_others_id.date_travel).days + 1

                    expense_data = {expense.id: {'amount_domestic': 0, 'amount_international': 0} for expense in expenses}
                    hardship_expense = self.env.ref('kw_tour.kw_tour_expense_type_ha')
                    hra_expense = self.env.ref('kw_tour.kw_tour_expense_type_hra')
                    employee = rec.employee_id

                    # added for RA and Travel desk and other approvals
                    if self._context.get('default_tour_id'):
                        tour = self.env['kw_tour'].browse(self._context.get('default_tour_id'))
                        if tour and tour.employee_id:
                            employee = tour.employee_id
                    # added for RA and Travel desk and other approvals/
                    effective_from = date(2022, 12, 26)
                    if rec.tour_others_id.date_travel and effective_from <= rec.tour_others_id.date_travel:
                        emp_level = self.env['kwemp_grade_master'].search([('id', 'in', employee.grade.ids)], limit=1)
                        for city in all_cities.filtered(lambda r: city_dict[r.id] > 0):
                            '''check if city is under domestic or international '''
                            for exp in expenses:
                                domestic_rec = city.expense_ids.filtered(
                                    lambda r: r.expense_type_id == exp and emp_level.id in r.employee_grade_id.ids)

                                if exp == hra_expense:
                                    if city_halt_dict[city.id] > 0:
                                        ''' calculate HRA '''
                                        if domestic_rec and domestic_rec.currency_type_id.name == "INR":
                                            expense_data[exp.id]['amount_domestic'] += city_halt_dict[
                                                                                           city.id] * domestic_rec.amount or 0
                                            days_expense_dict[exp.id]['inr'] += city_halt_dict[city.id]

                                        elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                            expense_data[exp.id]['amount_international'] += city_halt_dict[
                                                                                                city.id] * domestic_rec.amount or 0
                                            days_expense_dict[exp.id]['usd'] += city_halt_dict[city.id]

                                elif exp == hardship_expense:
                                    if city.ha_eligible:
                                        '''calculate hardship'''
                                        corresponding_exp = city.expense_type_id
                                        exp_record = city.expense_ids.filtered(
                                            lambda
                                                r: r.expense_type_id == corresponding_exp and emp_level.id in r.employee_grade_id.ids)

                                        if exp_record and exp_record.currency_type_id.name == "INR":
                                            amount = (exp_record.amount) * city.eligibility_percent / 100
                                            expense_data[hardship_expense.id]['amount_domestic'] += city_dict[city.id] * amount or 0
                                            days_expense_dict[hardship_expense.id]['inr'] += city_dict[city.id]

                                        elif exp_record and exp_record.currency_type_id.name == "USD":
                                            amount = (exp_record.amount) * city.eligibility_percent / 100
                                            expense_data[hardship_expense.id]['amount_international'] += city_dict[
                                                                                                             city.id] * amount or 0
                                            days_expense_dict[hardship_expense.id]['usd'] += city_dict[city.id]

                                else:
                                    '''regular calculation '''
                                    if domestic_rec and domestic_rec.currency_type_id.name == "INR":
                                        expense_data[exp.id]['amount_domestic'] += city_dict[city.id] * domestic_rec.amount or 0
                                        days_expense_dict[exp.id]['inr'] += city_dict[city.id]

                                    elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                        expense_data[exp.id]['amount_international'] += city_dict[
                                                                                            city.id] * domestic_rec.amount or 0
                                        days_expense_dict[exp.id]['usd'] += city_dict[city.id]



                    else:
                        emp_level = self.env['kw_grade_level'].search([('grade_ids', 'in', employee.grade.ids)], limit=1)
                        # print('emp_level_master', emp_level)
                        for city in all_cities.filtered(lambda r: city_dict[r.id] > 0):
                            '''check if city is under domestic or international '''

                            for exp in expenses:
                                domestic_rec = city.expense_ids.filtered(
                                    lambda r: r.expense_type_id == exp and not r.employee_grade_id)
                                if exp == hra_expense:
                                    if city_halt_dict[city.id] > 0:
                                        ''' calculate HRA '''
                                        if domestic_rec and domestic_rec.currency_type_id.name == "INR":
                                            expense_data[exp.id]['amount_domestic'] += city_halt_dict[
                                                                                           city.id] * domestic_rec.amount or 0
                                            days_expense_dict[exp.id]['inr'] += city_halt_dict[city.id]

                                        elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                            expense_data[exp.id]['amount_international'] += city_halt_dict[
                                                                                                city.id] * domestic_rec.amount or 0
                                            days_expense_dict[exp.id]['usd'] += city_halt_dict[city.id]

                                elif exp == hardship_expense:
                                    if city.ha_eligible:
                                        '''calculate hardship'''
                                        corresponding_exp = city.expense_type_id
                                        exp_record = city.expense_ids.filtered(
                                            lambda r: r.expense_type_id == corresponding_exp and not r.employee_grade_id)

                                        if exp_record and exp_record.currency_type_id.name == "INR":
                                            amount = (exp_record.amount) * city.eligibility_percent / 100
                                            expense_data[hardship_expense.id]['amount_domestic'] += city_dict[city.id] * amount or 0
                                            days_expense_dict[hardship_expense.id]['inr'] += city_dict[city.id]

                                        elif exp_record and exp_record.currency_type_id.name == "USD":
                                            amount = (exp_record.amount) * city.eligibility_percent / 100
                                            expense_data[hardship_expense.id]['amount_international'] += city_dict[
                                                                                                             city.id] * amount or 0
                                            days_expense_dict[hardship_expense.id]['usd'] += city_dict[city.id]

                                else:
                                    '''regular calculation '''
                                    if domestic_rec and domestic_rec.currency_type_id.name == "INR":
                                        expense_data[exp.id]['amount_domestic'] += city_dict[city.id] * domestic_rec.amount or 0
                                        days_expense_dict[exp.id]['inr'] += city_dict[city.id]

                                    elif domestic_rec and domestic_rec.currency_type_id.name == "USD":
                                        expense_data[exp.id]['amount_international'] += city_dict[
                                                                                            city.id] * domestic_rec.amount or 0
                                        days_expense_dict[exp.id]['usd'] += city_dict[city.id]

                    ta_amout_domestic += expense_data[self.env['kw_tour_expense_type'].search([('code', '=', 'ta')]).id]['amount_domestic']
                    ta_amount_international += expense_data[self.env['kw_tour_expense_type'].search([('code', '=', 'ta')]).id]['amount_international']
                    da_amout_domestic += expense_data[self.env['kw_tour_expense_type'].search([('code', '=', 'da')]).id]['amount_domestic']
                    da_amount_international += expense_data[self.env['kw_tour_expense_type'].search([('code', '=', 'da')]).id]['amount_international']
                    misc_amout_domestic += expense_data[self.env['kw_tour_expense_type'].search([('code', '=', 'misc')]).id]['amount_domestic']
                    misc_amount_international += expense_data[self.env['kw_tour_expense_type'].search([('code', '=', 'misc')]).id]['amount_international']
                    hra_amount_domestic += expense_data[self.env['kw_tour_expense_type'].search([('code', '=', 'hra')]).id]['amount_domestic']
                    hra_amount_international += expense_data[self.env['kw_tour_expense_type'].search([('code', '=', 'hra')]).id]['amount_international']
                    # ticket_cost_domestic += self.env['group_tour_ticket_config'].search([('ticket_type', '=', 'Flight')]).ticket_price if self.env['group_tour_ticket_config'].search([('ticket_type', '=', 'Flight')]).ticket_price else 0
                    ticket_cost_domestic += rec.ticket_price * 2 #*2 for return ticket price 
                    ticket_cost_international += 0

                    self.travel_expense_details_ids = False
                    dictt = {self.env['kw_tour_expense_type'].search([('code', '=', 'ta')]).id: {'amount_domestic': ta_amout_domestic, 'amount_international': ta_amount_international},
                             self.env['kw_tour_expense_type'].search([('code', '=', 'da')]).id: {'amount_domestic': da_amout_domestic, 'amount_international': da_amount_international},
                             self.env['kw_tour_expense_type'].search([('code', '=', 'hra')]).id: {'amount_domestic': hra_amount_domestic, 'amount_international': hra_amount_international},
                             self.env['kw_tour_expense_type'].search([('code', '=', 'misc')]).id: {'amount_domestic': misc_amout_domestic, 'amount_international': misc_amount_international},
                             self.env['kw_tour_expense_type'].search([('code', '=', 'ticket cost')]).id: {'amount_domestic': ticket_cost_domestic, 'amount_international': ticket_cost_international},
                             }
                    for rec in dictt:
                        self.travel_expense_details_ids = [[0, 0, {
                            'expense_id': rec,
                            'no_of_employee': len(li),
                            'amount_domestic': dictt[rec]['amount_domestic'],
                            'amount_international': dictt[rec]['amount_international'],
                            'no_of_night_inr': days_expense_dict[rec]['inr'],
                            'no_of_night_usd': days_expense_dict[rec]['usd'],
                        }]]



    @api.onchange('tour_detail_ids')
    def get_end_date(self):
        for rec in self.tour_detail_ids:
            if rec.to_date:
                self.date_return = rec.to_date

    def get_approver_btn(self):
        for rec in self:
            if rec.state == 'Approved' and rec.create_uid.employee_ids.id == self.env.user.employee_ids.id:
                rec.approver_btn_boolean = True
            else:
                rec.approver_btn_boolean = False


    @api.constrains('tour_type_id', 'tour_detail_ids', 'assign_tour_others_emp_ids')
    def validate_tour_details(self):
        for tour in self:
            # if tour.tour_type_id and not tour.tour_detail_ids:
            #     raise ValidationError('Please add tour details.')
            if not tour.assign_tour_others_emp_ids:
                raise ValidationError('Please add Employee.')

    @api.constrains('date_travel', 'date_return')
    def validate_travel_return_date(self):
        # current_date = date.today()
        for tour in self:
            if tour.date_return < tour.date_travel:
                raise ValidationError("Return date can't be less than Date of travel.")

    def action_submit(self):
        self.calculate_expenses()
        data = self.env['account.fiscalyear'].sudo().search(
            [('date_start', '<=', self.date_travel), ('date_stop', '>=', self.date_travel)]).mapped('id')
        total_tour_amount = 0
        # if self.cancellation_status is False and self.settlement_applied is False:
        total_tour_amount += self.total_budget_expense
        data = self.env['account.fiscalyear'].sudo().search([
            ('date_start', '<=', self.date_travel),
            ('date_stop', '>=', self.date_travel)
        ]).mapped('id')

        sec_data = self.env['kw_tour_treasury_budget'].sudo().search([
            ('fiscal_year_id', 'in', data),
            ('department_id', '=', self.create_uid.employee_ids.section.id),
            ('currency_id', '=', self.create_uid.employee_ids.user_id.company_id.currency_id.id)
        ])
        div_data = self.env['kw_tour_treasury_budget'].sudo().search([
            ('fiscal_year_id', 'in', data),
            ('department_id', '=', self.create_uid.employee_ids.division.id),
            ('currency_id', '=', self.create_uid.employee_ids.user_id.company_id.currency_id.id)
        ])
        dep_data = self.env['kw_tour_treasury_budget'].sudo().search([
            ('fiscal_year_id', 'in', data),
            ('department_id', '=', self.create_uid.employee_ids.department_id.id),
            ('currency_id', '=', self.create_uid.employee_ids.user_id.company_id.currency_id.id)
        ])
        if self.create_uid.employee_ids.section and sec_data:
            self.blocked_department_id = sec_data.id
        elif self.create_uid.employee_ids.division and div_data:
            self.blocked_department_id = div_data.id
        elif self.create_uid.employee_ids.department_id and dep_data:
            self.blocked_department_id = dep_data.id
        else:
            raise ValidationError('No Budget Data Found. Please Contact Your PM/RA For Further Information.')
        spent_amount = sum(self.blocked_department_id.tour_ids.mapped('total_budget_expense')) + sum(self.blocked_department_id.settlement_ids.mapped('total_budget_expense'))
        remaining_amount = self.blocked_department_id.budget_amount - spent_amount
        if self.blocked_department_id:
            if remaining_amount < total_tour_amount:
                raise ValidationError(
                    'Insufficient Balance in Dept Budget. Please Contact Finance For Further Information.')
        else:
            raise ValidationError('No Budget Data Found. Please Contact Your Finance For Further Information.')


        """
        
        Here is the api code to be written.
        
        """
        status_data = []
        for data in self.assign_tour_others_emp_ids:
            status_data.append(data.status)
        if self.tour_type_id.code == 'events':
                self.state = 'Applied'
                template = self.env.ref("kw_tour.kw_tour_others_event_email_template")
                rec=[]
                if template:
                    for recc in self.assign_tour_others_emp_ids:
                        if recc.status == 'Pending':
                            rec.append({'name':recc.employee_id.name,
                            'designation':recc.deg_id.name,
                            'department':recc.dept_id.name,
                            'work_email':recc.work_email,
                            'status':recc.status})
                    take_action_emp_id = literal_eval(
                        self.env['ir.config_parameter'].sudo().get_param('tour_others_approver') or '[]')
                    emp = self.env['hr.employee'].sudo().search([('id', '=', take_action_emp_id)])
                    mail_to = emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                    email = ",".join(mail_to) or ''
                    template.with_context(email_to=email,mail_for="applied",records=rec, name=emp.name).send_mail(self.id,
                                                                                   notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success("Mail Sent Successfully.")

        else:
            for rec in self.assign_tour_others_emp_ids:
                rec.status = 'Approved'
                kw_tour_action=[]
                kw_tour_vals = []
                kw_tour_vals.append((0, 0, {
                    'from_date': rec.tour_others_id.date_travel,
                    'to_date': rec.tour_others_id.date_travel,
                    'from_city_id':rec.city_id.id,
                    'to_city_id': rec.tour_others_id.to_city_id.id,
                    'to_city_class': rec.to_city_class.id,
                    'accomodation_arrangement': 'Company',

                }))
                kw_tour_vals.append((0, 0, {
                    'from_date': rec.tour_others_id.date_return,
                    'to_date': rec.tour_others_id.date_return,
                    'from_city_id': rec.tour_others_id.to_city_id.id,
                    'to_city_id': rec.city_id.id,
                    'to_city_class': rec.to_city_class.id,
                    'accomodation_arrangement': 'Not Required',

                }))
                kw_tour_action.append((0, 0, {
                    'date': date.today(),
                    'employee_id': self.env.user.employee_ids.id,
                    'state': 'Approved',
                    'remark': 'Group Tour Approved',
                }))
                self.env['kw_tour'].create(
                    {
                        'employee_id':rec.employee_id.id,
                        'tour_type_id':rec.tour_others_id.tour_type_id.id,
                        'purpose':rec.tour_others_id.purpose,
                        'date_travel':rec.tour_others_id.date_travel,
                        'city_id':rec.city_id.id,
                        'date_return':rec.tour_others_id.date_return,
                        'budget_head_id':rec.tour_others_id.budget_head_id.id,
                        'travel_arrangement':rec.tour_others_id.travel_arrangement,
                        'tour_detail_ids':kw_tour_vals,
                        'action_log_ids':kw_tour_action,
                        'state': 'Draft',
                        'tour_others_applied_by':self.env.user.employee_ids.id,
                        'create_uid':self.env.user.create_uid.id,
                        'treasury_budget_id':self.blocked_department_id.id,
                    }
                )
                for record in self.env['kw_tour'].sudo().search([('state', '=', 'Approved'), ('employee_id', '=', rec.employee_id.id)]):
                    record.set_expenses()
            self.state = 'Approved'

class TourAssignEmployee(models.Model):
    _name = "kw_tour_others_assign_employee"
    _description = 'Assign Employee for tour others'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    deg_id = fields.Many2one('hr.job',string='Designation',related="employee_id.job_id")
    dept_id = fields.Many2one('hr.department',string='Department',related="employee_id.department_id")
    work_email= fields.Char(related="employee_id.work_email",string="Work Email")
    status= fields.Char(string="Status", default="Pending")
    tour_others_id = fields.Many2one('kw_tour_others')
    tour_type_boolean = fields.Boolean(compute='compute_tour_type_boolean', store=False)
    city_id = fields.Many2one('kw_tour_city', "Originating Place", required=True)
    to_city_class = fields.Many2one(string="City Class", related="tour_others_id.to_city_id.classification_type_id")
    from_city_currency_id = fields.Many2one("res.currency", "Currency of From City", compute='set_from_city_domain')
    to_city_currency_id = fields.Many2one("res.currency", "Currency of To City", compute='set_from_city_domain')
    currency_id = fields.Many2one("res.currency", "Currency", compute='set_from_city_domain')
    accomodation_arrangement = fields.Selection(string="Accommodation Arrangement",
                                                selection=[('Self', 'Self'),
                                                           ('Company', 'Company'),
                                                           ('Client Arrangement', 'Client Arrangement'),
                                                           ('Not Required', 'Not Required')
                                                           ])
    ticket_price = fields.Float('Ticket Cost', compute='get_ticket_price', store=True)


    @api.onchange('city_id', 'tour_others_id.to_city_id')
    @api.depends('city_id', 'tour_others_id.to_city_id')
    def get_ticket_price(self):
        for rec in self:
            if rec.city_id and rec.tour_others_id.to_city_id and rec.tour_others_id.state == 'Draft':
                rec.ticket_price = self.env['group_tour_ticket_config'].sudo().search([('ticket_type', '=', 'Flight'), ('company_id', '=', self.env.user.company_id.id)]).ticket_price
            else:
                rec.ticket_price = 0

    # @api.onchange('city_id')
    # def get_class(self):
    #     self.to_city_class = self.tour_others_id.to_city_id.classification_type_id.id
    @api.depends('to_city_class')
    @api.onchange('city_id', 'to_city_class')
    def set_from_city_domain(self):
        for rec in self:
            if rec.city_id:
                currency_ids = rec.city_id.mapped('expense_ids.currency_type_id')
                rec.from_city_currency_id = currency_ids and currency_ids[0].id
            else:
                rec.from_city_currency_id = False

            if rec.tour_others_id.to_city_id:
                currency_ids = rec.tour_others_id.to_city_id.mapped('expense_ids.currency_type_id')
                rec.to_city_currency_id = currency_ids and currency_ids[0].id
            else:
                rec.to_city_currency_id = False
            all_currencies = rec.from_city_currency_id | rec.to_city_currency_id

            if rec.currency_id and rec.currency_id not in all_currencies:
                rec.currency_id = False

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        selected_employees = self.tour_others_id.assign_tour_others_emp_ids.mapped('employee_id')
        return {
            'domain': {
                'employee_id': [('id', 'not in', selected_employees.ids)]
            }
        }


    def compute_tour_type_boolean(self):
        for rec in self:
            if rec.tour_others_id.tour_type_id.code == 'events' and self.env.user.has_group('kw_tour.group_kw_tour_others_manager_take_action') and rec.tour_others_id.state != 'Draft':
                rec.tour_type_boolean = True
            else:
                rec.tour_type_boolean = False


    @api.constrains('employee_id')
    def _check_child_name(self):
        for record in self:
            if not record.employee_id:
                raise ValidationError("Add Employee Name cannot be empty.")

    def approve(self):
        data = self.env['account.fiscalyear'].sudo().search(
            [('date_start', '<=', self.tour_others_id.date_travel), ('date_stop', '>=', self.tour_others_id.date_travel)]).mapped('id')
        total_tour_amount = 0
        # if self.cancellation_status is False and self.settlement_applied is False:
        total_tour_amount += self.tour_others_id.total_budget_expense

        spent_amount = sum(self.tour_others_id.blocked_department_id.tour_ids.mapped('total_budget_expense')) + sum(
            self.tour_others_id.blocked_department_id.settlement_ids.mapped('total_budget_expense'))
        remaining_amount = self.tour_others_id.blocked_department_id.budget_amount - spent_amount
        if self.tour_others_id.blocked_department_id:
            if remaining_amount < total_tour_amount:
                raise ValidationError(
                    'Insufficient Balance in Dept Budget. Please Contact Finance For Further Information.')
        else:
            raise ValidationError('No Budget Data Found. Please Contact Your Finance For Further Information.')

        expense_id = []
        for rec in self.tour_others_id.travel_expense_details_ids:
            expense_id.append(rec.id)
        if self.status == 'Pending':
            self.status = 'Approved'
            kw_tour_action = []
            kw_tour_vals = []
            kw_tour_vals.append((0, 0, {
                'from_date': self.tour_others_id.date_travel,
                'to_date': self.tour_others_id.date_travel,
                'from_city_id': self.city_id.id,
                'to_city_id': self.tour_others_id.to_city_id.id,
                'to_city_class': self.to_city_class.id,
                'accomodation_arrangement': 'Company',
            }))
            kw_tour_vals.append((0, 0, {
                'from_date': self.tour_others_id.date_return,
                'to_date': self.tour_others_id.date_return,
                'from_city_id': self.tour_others_id.to_city_id.id,
                'to_city_id': self.city_id.id,
                'to_city_class': self.to_city_class.id,
                'accomodation_arrangement': 'Not Required',
            }))
            kw_tour_action.append((0, 0, {
                'date': date.today(),
                'employee_id': self.env.user.employee_ids.id,
                'state': 'Approved',
                'remark': 'Group Tour Approved',
            }))
            if self.status == 'Approved':
                tour  = self.env['kw_tour']
                tour.with_env(self.env(user=self.create_uid.id)).create(
                    {
                        'employee_id': self.employee_id.id,
                        'tour_type_new':self.tour_others_id.tour_type_new.id,
                        'tour_type_id': self.tour_others_id.tour_type_id.id,
                        'purpose': self.tour_others_id.purpose,
                        'date_travel': self.tour_others_id.date_travel,
                        'city_id': self.city_id.id,
                        'date_return': self.tour_others_id.date_return,
                        'budget_head_id': self.tour_others_id.budget_head_id.id,
                        'travel_arrangement': self.tour_others_id.travel_arrangement,
                        'tour_detail_ids': kw_tour_vals,
                        'action_log_ids': kw_tour_action,
                        'state': 'Approved',
                        'tour_others_applied_by': self.create_uid.employee_ids.id,
                        'treasury_budget_id': self.tour_others_id.blocked_department_id.id,
                    },
                )
                for record in self.env['kw_tour'].sudo().search(
                        [('state', '=', 'Approved'), ('employee_id', '=', self.employee_id.id)]):
                    record.set_expenses()
        list_data = []
        for rec in self.tour_others_id.assign_tour_others_emp_ids:
            if rec.status in ['Pending']:
                list_data.append(rec.status)
        if len(list_data) == 0:
            self.tour_others_id.state = 'Approved'
            template = self.env.ref("kw_tour.kw_tour_others_event_approve_email_template")
            rec=[]
            for recc in self.tour_others_id.assign_tour_others_emp_ids:
                    rec.append({'name':recc.employee_id.name,
                        'designation':recc.deg_id.name,
                        'department':recc.dept_id.name,
                        'work_email':recc.work_email,
                        'status':recc.status})
            if template:
                mail_to = self.create_uid.employee_ids.work_email
                template.with_context(email_to=mail_to, records=rec,name=self.create_uid.employee_ids.name).send_mail(
                    self.tour_others_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Mail Sent Successfully.")


    def reject(self):
        self.status = 'Rejected'
        self.ticket_price = 0
        expense_id = []
        for rec in self.tour_others_id.travel_expense_details_ids:
            expense_id.append(rec.expense_id.id)
        self.tour_others_id.calculate_expenses()
        for rec in self.tour_others_id.travel_expense_details_ids:
            if rec.expense_id.id not in expense_id:
                rec.unlink()
        list_data = []
        for recc in self.tour_others_id.assign_tour_others_emp_ids:
            if recc.status in ['Pending']:
                list_data.append(recc.status)
        if len(list_data) == 0:
            self.tour_others_id.state = 'Approved'
            template = self.env.ref("kw_tour.kw_tour_others_event_approve_email_template")
            rec=[]
            for recc in self.tour_others_id.assign_tour_others_emp_ids:
                rec.append({'name':recc.employee_id.name,
                    'designation':recc.deg_id.name,
                    'department':recc.dept_id.name,
                    'work_email':recc.work_email,
                    'status':recc.status})
            if template:
                mail_to = self.create_uid.employee_ids.work_email
                template.with_context(email_to=mail_to, records=rec, name=self.create_uid.employee_ids.name).send_mail(
                    self.tour_others_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Mail Sent Successfully.")

    def re_apply(self):
        self.status = 'Pending'
        self.tour_others_id.state = 'Applied'
        self.ticket_price = self.env['group_tour_ticket_config'].sudo().search([('ticket_type', '=', 'Flight')]).mapped('ticket_price')[0]
        expense_id = []
        for rec in self.tour_others_id.travel_expense_details_ids:
            expense_id.append(rec.expense_id.id)
        self.tour_others_id.calculate_expenses()
        for rec in self.tour_others_id.travel_expense_details_ids:
            if rec.expense_id.id not in expense_id:
                rec.unlink()
        rec=[]
        for recc in self.tour_others_id.assign_tour_others_emp_ids:
            if recc.status == 'Pending':
                rec.append({'name':recc.employee_id.name,
                     'designation':recc.deg_id.name,
                     'department':recc.dept_id.name,
                     'work_email':recc.work_email,
                     'status':recc.status})
        template = self.env.ref("kw_tour.kw_tour_others_event_email_template")
        if template:
            take_action_emp_id = literal_eval(
                self.env['ir.config_parameter'].sudo().get_param('tour_others_approver') or '[]')
            emp = self.env['hr.employee'].sudo().search([('id', '=', take_action_emp_id)])
            mail_to = emp.filtered(lambda r: r.work_email != False).mapped('work_email')
            email = ",".join(mail_to) or ''
            template.with_context(email_to=email, mail_for="reapply", name=emp.name,records=rec).send_mail(self.tour_others_id.id,
                                                                           notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Mail Sent Successfully.")


#
# class TourOthersDetails(models.Model):
#     _name = "kw_tour_others_details"
#     _description = "Tour Others Details"
#
#     @api.model
#     def _get_time_list(self):
#         dt = datetime.now()
#         start_loop = dt.replace(hour=0, minute=0, second=0, microsecond=0)
#         end_loop = dt.replace(hour=23, minute=45, second=0, microsecond=0)
#
#         time_list = [(start_loop.strftime('%H:%M:%S'), start_loop.strftime('%I:%M %p'))]
#
#         while start_loop < end_loop:
#             start_loop = (start_loop + relativedelta(minutes=+15))
#             time_list.append((start_loop.strftime('%H:%M:%S'),
#                               start_loop.strftime('%I:%M %p')))
#         return time_list
#
#     tour_others_id = fields.Many2one("kw_tour_others", "Tour", required=True, ondelete='cascade')
#     tour_type = fields.Selection(string="Type", required=False,
#                                  selection=[('Domestic', 'Domestic'), ('International', 'International')])
#     from_date = fields.Date(string="From Date", required=True, )
#     from_time = fields.Selection(selection='_get_time_list', string="From Time")
#
#     from_country_id = fields.Many2one('res.country', string="From Country", related="from_city_id.country_id")
#     from_city_id = fields.Many2one('kw_tour_city', string="From City", required=True, )
#     from_city_currency_id = fields.Many2one("res.currency", "Currency of From City")
#
#     to_date = fields.Date(string="To Date", required=True, )
#     to_time = fields.Selection(selection='_get_time_list', string="To Time")
#
#     to_country_id = fields.Many2one('res.country', string="To Country", related="to_city_id.country_id")
#     to_city_id = fields.Many2one('kw_tour_city', string="To City", required=True, )
#     to_city_class = fields.Many2one(string="City Class", related="to_city_id.classification_type_id" )
#
#     to_city_currency_id = fields.Many2one("res.currency", "Currency of To City")
#
#     travel_arrangement = fields.Selection(string="Travel Arrangement",
#                                           selection=[('Self', 'Self'), ('Company', 'Company')], required=True,
#                                           default="Company")
#
#     accomodation_arrangement = fields.Selection(string="Accommodation Arrangement",
#                                                 selection=[('Self', 'Self'),
#                                                            ('Company', 'Company'),
#                                                            ('Client Arrangement', 'Client Arrangement'),
#                                                            ('Not Required', 'Not Required')
#                                                            ], required=True, default="Company")
#     travel_mode_id = fields.Many2one('kw_tour_travel_mode', "Travel Mode")
#     currency_id = fields.Many2one("res.currency", "Currency", domain=[('name', 'in', ['INR', 'USD'])])
#     cost = fields.Integer("Ticket Cost")
#     document = fields.Binary("Upload Document")
#     document_name = fields.Char("File Name")
#
#     state = fields.Selection(string='Status',
#                              selection=[
#                                  ('Draft', 'Draft'),
#                                  ('Applied', 'Applied'),
#                                  ('Approved', 'Approved')
#                              ])
#
#     @api.model
#     def default_get(self, fields):
#         res = super(TourOthersDetails, self).default_get(fields)
#
#         # tour_start_city = self._context.get('default_from_city', False)
#         tour_last_city = self._context.get('default_last_city', False)
#         tour_travel_date = self._context.get('default_from_travel_date', False)
#         # last_travel_date = self._context.get('default_to_date', False)
#         if tour_last_city:
#             city = self.env['kw_tour_city'].browse(tour_last_city)
#             res['from_city_id'] = city.id
#             # res['from_country_id'] = city.country_id.id
#
#         if tour_travel_date:
#             res['from_date'] = tour_travel_date
#         # if last_travel_date:
#         #     res['to_date'] = last_travel_date
#
#         return res
#
#     @api.onchange('travel_arrangement')
#     def set_travel_details(self):
#         if self.state and self.state in ['Draft', 'Applied', 'Forwarded'] \
#                 and self.travel_arrangement and self.travel_arrangement == 'Self':
#             self.travel_mode_id = self.currency_id = self.cost = self.document = False
#
#     @api.onchange('from_city_id', 'to_city_id')
#     def set_from_city_domain(self):
#         if self.from_city_id:
#             currency_ids = self.from_city_id.mapped('expense_ids.currency_type_id')
#             self.from_city_currency_id = currency_ids and currency_ids[0].id
#         else:
#             self.from_city_currency_id = False
#
#         if self.to_city_id:
#             currency_ids = self.to_city_id.mapped('expense_ids.currency_type_id')
#             self.to_city_currency_id = currency_ids and currency_ids[0].id
#         else:
#             self.to_city_currency_id = False
#         all_currencies = self.from_city_currency_id | self.to_city_currency_id
#
#         if self.currency_id and self.currency_id not in all_currencies:
#             self.currency_id = False
#
#     @api.onchange('from_date', 'to_date')
#     def onchange_date(self):
#         for record in self:
#             if record.from_date and record.to_date:
#                 if record.from_date > record.to_date:
#                     raise ValidationError("From Date cannot be greater than To Date.")
#

# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     @api.multi
#     def write(self, vals):
#         ref_id = self.env.ref('kw_tour.group_kw_tour_others_manager_take_action').id
#         data = self.env['res.groups'].sudo().search([('id', '=',ref_id)])
#         data.users = False
#         data.users = [(4, self.tour_others_approver.user_id.id)]
#         return super(ResConfigSettings, self).write(vals)



class GroupTourTicketConfiguration(models.Model):
    _name = "group_tour_ticket_config"
    _description = 'Group Tour Ticket Configuration'

    ticket_type = fields.Selection(string="Travel Arrangement",
                                          selection=[('Flight', 'Flight'), ('Train', 'Train')], required=True,
                                          default="Flight")
    ticket_price = fields.Float('Amount', required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency",
                                  related='company_id.currency_id', readonly=True)


    @api.constrains('company_id')
    def validate_category(self):
        record = self.env['group_tour_ticket_config'].search([]) - self
        for info in record:
            if info.company_id == self.company_id:
                raise ValidationError(self.company_id.name + " already exists.")