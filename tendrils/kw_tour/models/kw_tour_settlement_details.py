from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import  date



class TourSettlementDetails(models.Model):
    _name = 'kw_tour_settlement_details'
    _description = "Tour Settlement Details"

    @api.model
    def _get_city_domain(self):
        domain = []
        if 'default_tour_id' in self._context and self._context['default_tour_id']:
            tour = self.env['kw_tour'].browse(self._context['default_tour_id'])
            from_cities = tour.tour_detail_ids.mapped(lambda r: r.from_city_id)
            to_cities = tour.tour_detail_ids.mapped(lambda r: r.to_city_id)
            all_cities = from_cities | to_cities | tour.city_id

            domain += [('id', 'in', all_cities.ids)]
        else:
            domain += [('id', 'in', [])]
        return domain

    def get_from_date(self):
        date_ = False
        if 'default_tour_id' in self._context and self._context['default_tour_id']:
            tour = self.env['kw_tour'].browse(self._context['default_tour_id'])
            date_ = tour.date_travel
        return date_

    settlement_id = fields.Many2one("kw_tour_settlement", required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee Name", related="settlement_id.employee_id")
    from_date = fields.Date(string='From Date', required=True, oldname="date", default=get_from_date)
    to_date = fields.Date(string='To Date', required=True, default=get_from_date)
    city_id = fields.Many2one("kw_tour_city", "Place Of Expense", required=True, domain=_get_city_domain)
    city_currency_ids = fields.Many2many('res.currency', string="City Currencies")
    category = fields.Selection(string='Category', required=True, default="Tour",
                                selection=[('Tour', 'Tour'), ('Local Visit', 'Local Visit'), ('Visit', 'Visit')])
    expense_id = fields.Many2one("kw_tour_expense_type", "Type Of Expense", required=True,
                                 domain=lambda self: [('id', 'not in',
                                                       [self.env.ref('kw_tour.kw_tour_expense_type_ha').id,
                                                        self.env.ref('kw_tour.kw_tour_expense_type_ticket_cost').id,
                                                        self.env.ref('kw_tour.kw_tour_expense_type_additional_expenses').id])])
    expense_name = fields.Char("Type of Expense", compute='_get_expense_name')
    expense_code = fields.Char(related="expense_id.code", string="Expense Code")
    # expense_name            = fields.Char("Type of Expense",compute="_compute_expense_name")
    misc_expense = fields.Char("Misc Type")
    da_category_id = fields.Many2one("kw_tour_da_category", "DA Category")
    da_percentage = fields.Integer(related='da_category_id.percentage', string="DA %")
    ancillary_expense_id = fields.Many2one("kw_tour_ancillary_expenses", "Expense Category")
    description = fields.Text("Description", required=True)
    currency_id = fields.Many2one('res.currency', "Currency", required=True)
    amount_actual = fields.Float('Eligible Amount', compute="compute_amount")
    amount_claiming = fields.Float("Claimed Amount", required=True)
    status = fields.Selection(string='Bill Status', required=True, default="Paid",
                              selection=[('Paid', 'Paid'), ('Due', 'Due')])
    document = fields.Binary("Upload Document")
    doc_description = fields.Text("Document Description")
    no_of_nights = fields.Integer("No.of Days", compute="compute_no_of_days")
    no_of_days_leave = fields.Float("No. of Days On Leave", compute="compute_leave_days", digits=(4, 1))

    @api.depends('expense_id', 'da_category_id')
    @api.multi
    def _get_expense_name(self):
        for res in self:
            res.expense_name = ''
            if res.expense_id and not res.da_category_id:
                res.expense_name = res.expense_id.name
            if res.expense_id and res.da_category_id:
                exp_list = ', '.join([str(res.expense_id.name) + ' (' + str(res.da_category_id.percentage) + '%)'])
                res.expense_name = exp_list

    # @api.depends('expense_id')
    # @api.multi
    # def _compute_expense_name(self):
    #     for settlement in self:
    #         if settlement.expense_id:
    #             if settlement.expense_id.code == 'misc':
    #                 settlement.expense_name = settlement.misc_expense and  f"{settlement.expense_id.name}({settlement.misc_expense})" or settlement.expense_id.name
    #             else:
    #                 settlement.expense_name = settlement.expense_id.name

    @api.depends('from_date', 'to_date')
    @api.multi
    def compute_leave_days(self):
        for detail in self:
            if detail.from_date and detail.to_date and detail.settlement_id.tour_id:
                employee = detail.settlement_id.tour_id.employee_id
                leave_values = self.env['kw_daily_employee_attendance'].search([('employee_id', '=', employee.id),
                                                                                ('attendance_recorded_date', '>=', detail.from_date),
                                                                                ('attendance_recorded_date', '<=', detail.to_date)]).mapped('leave_day_value')
                detail.no_of_days_leave = leave_values and sum(leave_values) or 0

    @api.depends('from_date', 'to_date', 'city_id', 'expense_id', 'da_category_id', 'currency_id')
    @api.multi
    def compute_amount(self):
        for detail in self:
            total_amount = 0
            if detail.settlement_id.tour_id and detail.expense_id and detail.city_id \
                    and detail.currency_id and detail.no_of_nights > 0:
                city = detail.city_id
                # print(city.classification_type_id.name, 'city------------------------------------------>>>>>>>>>>>>>>>>')
                expense = detail.expense_id
                # print(expense, 'expense------------------------------------------>>>>>>>>>>>>>>>>')
                hardship_expense = self.env.ref('kw_tour.kw_tour_expense_type_ha')
                hardship_bool = False
                percentage = 0

                if expense == hardship_expense:
                    hardship_bool = True
                    expense = detail.city_id.expense_type_id
                    percentage = detail.city_id.eligibility_percent

                currency = detail.currency_id
                effective_from = date(2022, 12, 26)
                i_class_effective_from = date(2023, 7, 1)
                if city.classification_type_id.name.upper().startswith('I'):
                    if detail.from_date and detail.from_date < i_class_effective_from:
                        expense_not_rec = False
                        expense_not_rec = city.expense_ids.filtered(
                            lambda r: not r.employee_grade_id.ids and r.currency_type_id == currency)
                        expense_not_rec = expense_not_rec.filtered(lambda r: r.expense_type_id == expense)
                        amount = expense_not_rec and expense_not_rec.amount or 0
                        if expense and expense.code == 'da' and detail.da_category_id:
                            amount = amount * (detail.da_category_id.percentage / 100)
                        if hardship_bool and percentage > 0:
                            amount = amount * (percentage / 100)
                        total_amount = amount * detail.no_of_nights
                    else:
                        # print('run----------------------------2')
                        emp_level = self.env['kwemp_grade_master'].search(
                            [('name', '=', detail.settlement_id.tour_id.employee_id.grade.name)], limit=1)

                        expense_rec = False
                        expense_rec = city.expense_ids.filtered(
                            lambda r: emp_level.id in r.employee_grade_id.ids and r.currency_type_id == currency)
                        expense_rec = expense_rec.filtered(lambda r: r.expense_type_id == expense)
                        amount = expense_rec and expense_rec.amount or 0

                        if expense and expense.code == 'da' and detail.da_category_id:
                            amount = amount * (detail.da_category_id.percentage / 100)

                        if hardship_bool and percentage > 0:
                            amount = amount * (percentage / 100)
                        total_amount = amount * detail.no_of_nights

                elif detail.from_date and effective_from >= detail.from_date:
                    # print('run----------------------------3')
                    expense_not_rec = False
                    expense_not_rec = city.expense_ids.filtered(lambda r: not r.employee_grade_id.ids and r.currency_type_id == currency)
                    expense_not_rec = expense_not_rec.filtered(lambda r: r.expense_type_id == expense)
                    amount = expense_not_rec and expense_not_rec.amount or 0             
                    if expense and expense.code == 'da' and detail.da_category_id:
                        amount = amount * (detail.da_category_id.percentage / 100)
                    if hardship_bool and percentage > 0:
                        amount = amount * (percentage / 100)
                    total_amount = amount * detail.no_of_nights
                else:
                    # print('run----------------------------4')
                    emp_level = self.env['kwemp_grade_master'].search(
                        [('name', '=', detail.settlement_id.tour_id.employee_id.grade.name)], limit=1)

                    expense_rec = False
                    expense_rec = city.expense_ids.filtered(lambda r:  emp_level.id in  r.employee_grade_id.ids and r.currency_type_id == currency)
                    expense_rec = expense_rec.filtered(lambda r: r.expense_type_id == expense )
                    amount = expense_rec and expense_rec.amount or 0

                    if expense and expense.code == 'da' and detail.da_category_id:
                        amount = amount * (detail.da_category_id.percentage / 100)

                    if hardship_bool and percentage > 0:
                        amount = amount * (percentage / 100)
                    total_amount = amount * detail.no_of_nights
            detail.amount_actual = total_amount

    @api.onchange('amount_claiming')
    def validate_claim_amount(self):
        if self.amount_claiming and self.amount_claiming > self.amount_actual:
            return {
                'warning': {
                    'title': 'Alert...!',
                    'message': "You are applying more than eligible amount."
                }
            }

    @api.constrains('amount_claiming')
    def validate_amount_claiming(self):
        for data in self:
            if data.amount_claiming < 1:
                raise ValidationError("Claimed amount should be greater than 0.")

    @api.depends('from_date', 'to_date')
    @api.multi
    def compute_no_of_days(self):
        for detail in self:
            if detail.from_date and detail.to_date:
                delta = detail.to_date - detail.from_date
                detail.no_of_nights = delta.days + 1

    @api.onchange('expense_id', 'currency_id')
    def change_da_ancillary(self):
        if self.expense_id:
            if self.expense_id.code == 'da':
                self.ancillary_expense_id = False
            elif self.expense_id.code == 'misc':
                self.da_category_id = False
            else:
                self.da_category_id = self.ancillary_expense_id = False
        else:
            self.da_category_id = self.ancillary_expense_id = False

    @api.onchange('city_id')
    def set_expense_domain(self):
        currencies = self.city_id and self.city_id.mapped('expense_ids.currency_type_id').ids or []
        self.city_currency_ids = [[6, 0, currencies]]
        self.currency_id = currencies and currencies[0] or False
        self.expense_id = False
        domain = [('id', 'not in', [self.env.ref('kw_tour.kw_tour_expense_type_ha').id,
                                    self.env.ref('kw_tour.kw_tour_expense_type_ticket_cost').id,
                                    self.env.ref('kw_tour.kw_tour_expense_type_additional_expenses').id])]
        if self.city_id and self.city_id.ha_eligible:
            domain = [('id', 'not in', [self.env.ref('kw_tour.kw_tour_expense_type_ticket_cost').id])]
        return {'domain': {'expense_id': domain}}
