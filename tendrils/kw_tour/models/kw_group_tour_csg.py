from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from ast import literal_eval

class GroupTourCSG(models.Model):
    _name = 'kw_group_tour_csg'
    _description = "CSG Group Tour"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'tour_type_id'

    tour_type_new = fields.Many2one('kw_tour_type_new', string="Tour Type")
    tour_type_id = fields.Many2one('kw_tour_type', required=True, string="Type Of Tour")
    group_tour_csg_code =  fields.Char(string="CSG/Tour No.", default="New", readonly="1")
    purpose = fields.Text("Purpose", required=True)
    date_travel = fields.Date("Date Of Travel", required=True)
    city_id = fields.Many2one('kw_tour_city', "Originating Place")
    to_city_id = fields.Many2one('kw_tour_city', "Destination Place", required=True)
    date_return = fields.Date("Return Date", required=True)
    budget_head_id = fields.Many2one('kw_tour_budget_head', string="Budget Head", track_visibility='onchange', required=True)
    travel_arrangement = fields.Selection(string="Travel Arrangement",
                                          selection=[('Self', 'Self'), ('Company', 'Company')], required=True,
                                          default="Company")
    acc_arrange = fields.Selection(string="Accommodation Arrangement", selection=[('Self', 'Self'),
                                                           ('Company', 'Company'),
                                                           ('Client Arrangement', 'Client Arrangement'),
                                                           ('Not Required', 'Not Required')
                                                           ], required=True, default="Company")
    # tour_detail_ids = fields.One2many('kw_tour_others_details', 'tour_others_id', string="Tour Details")
    assign_tour_others_csg_emp_ids = fields.One2many('kw_group_tour_csg_assign_employee', 'tour_others_id', string="Add Employee", required=True)
    state = fields.Selection(string='Status',
                             selection=[('Draft', 'Draft'),
                                        ('Applied', 'Applied'),
                                        ], default='Draft')
    # approver_btn_boolean = fields.Boolean(compute='get_approver_btn', store=False)
    travel_expense_details_ids = fields.One2many('kw_tour_travel_expense_details', 'tour_csg_id',
                                                 string="Travel Expenses", )
    department_id = fields.Many2one('hr.department')
    total_budget_expense = fields.Float("Total Blocked Budget Expense", compute='_get_total_budget', store=True)
    can_apply_inr = fields.Boolean(string='Can Apply For Advance INR ?', compute="_compute_advance_inr_usd")
    can_apply_usd = fields.Boolean(string='Can Apply For Advance USD ?', compute="_compute_advance_inr_usd")
    api_exchange_rate = fields.Float('API Exchange Rate')
    city_ids = fields.Many2many('kw_tour_city', compute='get_val', store=False)
    emp_ids = fields.Many2many('hr.employee', compute='get_val', store=False)
    @api.depends('group_tour_csg_code')
    def get_val(self):
        self.city_ids = [(6, 0, self.env['kw_tour_city'].search([('company_id', '=', self.env.user.company_id.id)]).ids)]
        self.emp_ids = [(6, 0, self.env['hr.employee'].search([('company_id', '=', self.env.user.company_id.id)]).ids)]


    @api.model
    def create(self, values):
        values['group_tour_csg_code'] = self.env['ir.sequence'].sudo().next_by_code('self.group_tour_csg_seq') or 'New'
        tour = super(GroupTourCSG, self).create(values)
        self.env.user.notify_success("Group Tour created successfully.")
        return tour

    @api.constrains('tour_type_id', 'assign_tour_others_csg_emp_ids','date_travel',
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


    @api.depends("assign_tour_others_csg_emp_ids")
    @api.multi
    def _compute_advance_inr_usd(self):
        for tour in self:
            inr_expense = tour.travel_expense_details_ids.filtered(lambda r: r.amount_domestic > 0)
            usd_expense = tour.travel_expense_details_ids.filtered(lambda r: r.amount_international > 0)
            if inr_expense:
                tour.can_apply_inr = True
            if usd_expense:
                tour.can_apply_usd = True

    @api.depends('assign_tour_others_csg_emp_ids', 'date_travel', 'date_return', 'city_id', 'to_city_id')
    def _get_total_budget(self):
        for record in self:
            p_amount_inr, p_amount_usd = 0, 0
           
            p_amount_inr += sum(record.travel_expense_details_ids.mapped('amount_domestic'))
            p_amount_usd += sum(
                record.travel_expense_details_ids.mapped('amount_international')) * record.api_exchange_rate
            record.total_budget_expense = p_amount_inr + p_amount_usd


    @api.constrains('date_travel', 'date_return')
    def get_date_value(self):
        if self.date_travel > self.date_return:
            raise ValidationError('Date of return always greater than Date of Travel.')

    @api.onchange('assign_tour_others_csg_emp_ids', 'date_travel', 'date_return', 'to_city_id')
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
            for rec in self.assign_tour_others_csg_emp_ids:
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
                                        if domestic_rec and domestic_rec.currency_type_id.name == rec.employee_id.company_id.currency_id.name:
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

                                        if exp_record and exp_record.currency_type_id.name == rec.employee_id.company_id.currency_id.name:
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
                                    if domestic_rec and domestic_rec.currency_type_id.name == rec.employee_id.company_id.currency_id.name:
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
                                        if domestic_rec and domestic_rec.currency_type_id.name == rec.employee_id.company_id.currency_id.name:
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

                                        if exp_record and exp_record.currency_type_id.name == rec.employee_id.company_id.currency_id.name:
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
                                    if domestic_rec and domestic_rec.currency_type_id.name == rec.employee_id.company_id.currency_id.name:
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
                    for recc in dictt:
                        self.travel_expense_details_ids = [[0, 0, {
                            'expense_id': recc,
                            'no_of_employee': len(li),
                            'amount_domestic': dictt[recc]['amount_domestic'],
                            'amount_international': dictt[recc]['amount_international'],
                            'no_of_night_inr': days_expense_dict[recc]['inr'],
                            'no_of_night_usd': days_expense_dict[recc]['usd'],
                            'currency_domestic': rec.employee_id.company_id.currency_id.id,
                            'currency_international': self.env['res.currency'].sudo().search([('name', '=', 'USD')]).id,
                        }]]



   

    @api.constrains('tour_type_id','assign_tour_others_csg_emp_ids')
    def validate_tour_details(self):
        for tour in self:
            if tour.tour_type_id and not tour.assign_tour_others_csg_emp_ids:
                raise ValidationError('Please add Employee details.')

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
        department_sec = self.env['kw_tour_treasury_budget'].sudo().search(
            [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.section.id),
             ('company_id', '=', self.env.user.employee_ids.company_id.id)],
            limit=1)
        department_div = self.env['kw_tour_treasury_budget'].sudo().search(
            [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.division.id),
             ('company_id', '=', self.env.user.employee_ids.company_id.id)],
            limit=1)
        department_dep = self.env['kw_tour_treasury_budget'].sudo().search(
            [('fiscal_year_id', 'in', data), ('department_id', '=', self.create_uid.employee_ids.department_id.id),
             ('company_id', '=', self.env.user.employee_ids.company_id.id)],
            limit=1)
        departmentt = 0
        if department_sec:
            departmentt = department_sec.id
            if department_sec.remaining_amount < total_tour_amount:
                raise ValidationError(
                    'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
        elif department_div:
            departmentt = department_div.id
            if department_div.remaining_amount < total_tour_amount:
                raise ValidationError(
                    'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
        elif department_dep:
            departmentt = department_dep.id
            if department_dep.remaining_amount < total_tour_amount:
                raise ValidationError(
                    'Insufficient Balance in Your Budget. Please Contact Your Project Manager/RA For Further Information.')
        else:
            raise ValidationError('No Budget Data Found. Please Contact Your PM/RA For Further Information.')

        # departmentt = self.env['kw_tour_treasury_budget'].sudo().search(
        #     [('fiscal_year_id', 'in', data), ('department_id', 'in', [self.create_uid.employee_ids.section.id,
        #                                                               self.create_uid.employee_ids.division.id,
        #                                                               self.create_uid.employee_ids.department_id.id])],
        #     limit=1)
        # spent_amount = sum(departmentt.tour_ids.mapped('total_budget_expense')) + sum(departmentt.settlement_ids.mapped('total_budget_expense'))
        # remaining_amount = departmentt.budget_amount - spent_amount
        # # print(spent_amount, 'spent_amount--->>>', remaining_amount, 'remaining amount------->>>>>>', self.create_uid.id, self.env.user.employee_ids.name, departmentt.id, departmentt.department_id.name)
        # if departmentt:
        #     if remaining_amount < total_tour_amount:
        #         raise ValidationError(
        #             'Insufficient Balance in Dept Budget. Please Contact Finance Dept. For Further Information.')
        # else:
        #     raise ValidationError('No Budget Data Found. Please Contact Finance Dept. For Further Information.')
       
      
        status_data = []
        for rec in self.assign_tour_others_csg_emp_ids:
            rec.status = 'Applied'
            kw_tour_action=[]
            kw_tour_vals = []
            kw_tour_vals.append((0, 0, {
                'from_date': rec.tour_others_id.date_travel,
                'to_date': rec.tour_others_id.date_travel,
                'from_city_id':rec.city_id.id,
                'to_city_id': rec.tour_others_id.to_city_id.id,
                'to_city_class': rec.to_city_class.id,
                'accomodation_arrangement': self.acc_arrange,

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
                'state': 'Draft',
                'remark': 'Group Tour Applied',
            }))
            self.env['kw_tour'].create(
                {
                    'employee_id':rec.employee_id.id,
                    'tour_type_new':rec.tour_others_id.tour_type_new.id,
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
                    'treasury_budget_id':departmentt,
                    'csg_group_tour_boolean':True,
                    'csg_group_tour_code':rec.tour_others_id.group_tour_csg_code
                }
            )
            for record in self.env['kw_tour'].sudo().search([('state', '=', 'Draft'), ('employee_id', '=', rec.employee_id.id)]):
                record.set_expenses()
        self.state = 'Applied'
        # email_list = []
        for rec in self.assign_tour_others_csg_emp_ids:
            email_to = rec.employee_id.work_email
            emp_name = rec.employee_id.name
            notify_template = self.env.ref('kw_tour.csg_tour_apply_email_template')

            notify_template.with_context(email_to=email_to,emp_name=emp_name).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_info(message='Mail sent successfully.')

class GroupTourAssignEmployee(models.Model):
    _name = "kw_group_tour_csg_assign_employee"
    _description = 'Assign Employee for tour others'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    deg_id = fields.Many2one('hr.job',string='Designation',related="employee_id.job_id")
    dept_id = fields.Many2one('hr.department',string='Department',related="employee_id.department_id")
    work_email= fields.Char(related="employee_id.work_email",string="Work Email")
    status= fields.Char(string="Status", default="Pending")
    tour_others_id = fields.Many2one('kw_group_tour_csg')
    # tour_type_boolean = fields.Boolean(compute='compute_tour_type_boolean', store=False)
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
                rec.ticket_price = self.env['group_tour_ticket_config'].sudo().search([('company_id', '=',self.env.user.employee_ids.company_id.id), ('ticket_type', '=', 'Flight')]).ticket_price
            else:
                rec.ticket_price = 0

    
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

    # @api.onchange('employee_id')
    # def onchange_employee_id(self):
    #     selected_employees = self.tour_others_id.assign_tour_others_csg_emp_ids.mapped('employee_id')
    #     return {
    #         'domain': {
    #             'employee_id': [('id', 'not in', selected_employees.ids)]
    #         }
    #     }

    @api.constrains('employee_id')
    def _check_child_name(self):
        for record in self:
            if not record.employee_id:
                raise ValidationError("Add Employee Name cannot be empty.")