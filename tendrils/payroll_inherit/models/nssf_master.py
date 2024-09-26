from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time


class nssf_master(models.Model):
    _name = 'nssf_master'
    _description = 'NSSF Master'
    
    year = fields.Char()
    month = fields.Char()
    gross = fields.Float()
    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(related='employee_id.name')
    code = fields.Char(related='employee_id.emp_code')
    tire_1_pensionable_earnings = fields.Float()
    tire_1_employee_contribution = fields.Float()
    tire_1_employer_contribution = fields.Float()
    tire_1_total_contribution = fields.Float()
    tire_2_pensionable_earnings = fields.Float()
    tire_2_employee_contribution = fields.Float()
    tire_2_employer_contribution = fields.Float()
    tire_2_total_contribution = fields.Float()
    total_contribution = fields.Float(string="Total NSSF Contribution")
    total_employee_contribution = fields.Float()
    total_employer_contribution = fields.Float()
    payslip_id = fields.Many2one('hr.payslip',ondelete='cascade')
    
    
class nssf_configuration(models.Model):
    _name = 'nssf_configuration'
    _description = 'NSSF Configuration'

    date_from = fields.Date()
    date_to = fields.Date()
    min_value_nssf = fields.Integer(string='Lower Limit')
    max_value_nssf = fields.Integer(string='Upper Limit')
    