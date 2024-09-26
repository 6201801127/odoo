from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# from stpi_employee.wizards.employee_action_select import EmployeeActionSelection

class Reimbursement(models.Model):

    _name = "reimbursement.attendence"
    _description = "Reimbursement Attendence"


    employee_id = fields.Many2one('hr.employee', string='Employee')
    year = fields.Char(string='Year', size=4)
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
                              ('10', 'October'), ('11', 'November'), ('12', 'December')], string='Month')
    date_related_month = fields.Date(string='Date related month')
    present_days = fields.Integer('Present Days')
    no_of_days = fields.Integer('Number of Days')
    no_of_days_related = fields.Integer('Number of Days', related='no_of_days')


    @api.onchange('month','year')
    @api.constrains('month','year')
    def get_max_no_of_days(self):
        for rec in self:
            if rec.month == '01' or rec.month == '03' or rec.month == '05' or rec.month == '07' or rec.month == '08' or rec.month == '' or rec.month == '10' or rec.month == '12':
                rec.no_of_days = 31
            elif rec.month == '04' or rec.month == '06' or rec.month == '09' or rec.month == '11':
                rec.no_of_days = 30
            else:
                rec.no_of_days = 28



    @api.onchange('present_days')
    @api.constrains('present_days')
    def validate_present_days(self):
        for rec in self:
            if rec.present_days > rec.no_of_days:
                raise ValidationError(
                        _(
                            'Present days must be less than maximum number of days'))

    @api.onchange('year')
    @api.constrains('year')
    def validate_year_isdigit(self):
        for rec in self:
            today = datetime.now().date()
            if rec.year:
                for e in rec.year:
                    if not e.isdigit():
                        raise ValidationError(
                            _(
                                'Please enter correct year, it must be of 4 digits'))
                if int(rec.year) > today.year:
                    raise ValidationError(
                        _(
                            'You are not allowed to enter the future year'))


    @api.onchange('month','year')
    @api.constrains('month','year')
    def calculate_year_month_date(self):
        for rec in self:
            if rec.month and rec.year:
                rec.date_related_month = date(int(rec.year), int(rec.month), 15)

    @api.constrains('employee_id', 'month','year')
    def check_unique_attendence(self):
        for rec in self:
            count = 0
            emp_id = self.env['reimbursement.attendence'].search(
                [('month', '=', rec.month),('year', '=', rec.year), ('employee_id', '=', rec.employee_id.id)])
            for e in emp_id:
                count += 1
            if count > 1:
                raise ValidationError("It must be unique")


class ReimbursementConfiguration(models.Model):
    _name = "reimbursement.configuration"
    _description = "Reimbursement Configuration"
    _rec_name = "reimbursement_type_id"

    # name = fields.Selection([
    #     ('lunch', 'Lunch Subsidy'),
    #     ('telephone', 'Telephone Reimbursement'),
    #     ('broadband', 'Broadband Reimbursement'),
    #     ('mobile', 'Mobile Reimbursement'),
    #     ('medical', 'Medical Reimbursement'),
    #     ('tuition_fee', 'Tuition Fee claim'),
    #     ('hostel', 'Hostel claim'),
    #     ('briefcase', 'Briefcase Reimbursement'),
    #     ('quarterly', 'Newspaper Reimbursements'),
    #     ('el_encashment', 'EL Encashment'),
    # ], string='Reimbursement Type')

    reimbursement_type_id = fields.Many2one('reimbursement.type','Reimbursement Type')

    pay_level_ids = fields.Many2many('hr.payslip.paylevel', string='Pay Level')
    grade_pay = fields.Text(string='Grade Pay')
    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_stpi', 'Contractual with STPI')], string='Employment Type',
                                     store=True)

    job_ids = fields.Many2many('hr.job', string='Post')
    group_ids = fields.Many2many('res.groups', string='Groups')
    # branch_id = fields.Many2one('res.branch', string='Branch', store=True)
    full = fields.Boolean('Full')
    allowed = fields.Char('Upper Limit')
    date_range_type = fields.Many2one('date.range.type', string='Applicable Period')
    max_submit = fields.Integer(string='Max. Application Date')

    open = fields.Boolean('Open')

    attendance_required = fields.Boolean(string='Attendance Required?',default=True)
    reimbursement_type_code = fields.Char(string='Reimbursement Type Code', related='reimbursement_type_id.code')
    per_day_amount = fields.Float(string='Per Day Amount')
    taxable_per_day_amount = fields.Float(string='Taxable Per Day Amount')




    @api.constrains('pay_level_ids')
    def get_grade_pay(self):
        for res in self:
            lst = []
            serch_id = self.env['hr.payslip.paylevel'].search([('id', 'in', res.pay_level_ids.ids)])
            for line in serch_id:
                if line.grade_pay:
                    print('===============================', line.grade_pay)
                    lst.append(line.grade_pay)
            lst = list(set(lst))
            listToStr = ' '.join([str(elem) for elem in lst])
            res.grade_pay = str(listToStr)




    # @api.constrains('full')
    @api.onchange('full')
    def _onchange_full(self):
        for rec in self:
            if rec.full == True:
                rec.allowed = '0'

    # @api.onchange('employee_type')
    # def _onchange_employee_type(self):
    #     self.job_ids = False
    #     if self.employee_type == 'regular':
    #         return {'domain': {'job_ids': ([('employee_type', 'in', [self.env.ref('bsscl_recruitment.regular_id').id])])}}
    #     elif self.employee_type == 'contractual_with_agency':
    #         return {'domain': {'job_ids': ([('employee_type', 'in', [self.env.ref('bsscl_recruitment.cont_ag').id])])}}
    #     elif self.employee_type == 'contractual_with_stpi':
    #         return {'domain': {'job_ids': ([('employee_type', 'in', [self.env.ref('bsscl_recruitment.cont_stpi').id])])}}


