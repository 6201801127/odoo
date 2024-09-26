from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class Reimbursement(models.Model):

    _name = "reimbursement.attendence"
    _description = "Reimbursement Attendence"


    employee_id = fields.Many2one('hr.employee', string='Employee')
    year = fields.Char(string='Year', size=4)
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
                              ('10', 'October'), ('11', 'November'), ('12', 'December')], string='Month')
    date_related_month = fields.Date(string='Date related month')
    present_days = fields.Float('Present Days')
    no_of_days = fields.Float('Number of Days')
    no_of_days_related = fields.Float('Number of Days', related='no_of_days')


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