# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from ast import literal_eval



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    esi_start_date = fields.Date(string='ESI First Period')
    esi_end_date = fields.Date(string='ESI Second Period')

    insurance_start_date = fields.Date(string='Insurance Renewal Date')
    check_health_insurance = fields.Boolean(string='Check Health Insurance Dependant')
    check_health_insurance_self = fields.Boolean(string='Check Health Insurance Self')
    check_el_deduction = fields.Boolean(string='Check EL Deduction')
    payroll_data = fields.Boolean(string=' Check Payroll Data')
    enable_canteen_deduction = fields.Boolean(string='Enable Canteen')
    enable_canteen_excel = fields.Boolean(string='Enable Excel')
    enable_health_insurance_form = fields.Boolean(string='Enable Health Insurance Form')
    enable_health_insurance_home_page = fields.Boolean(string='Enable Health Insurance Home Page')
    last_date_of_submitting_health_insurance_details = fields.Date(string="LastDate Of Submitting Health Insurance Details")
    check_bank_update = fields.Boolean(string='Enable Excel')
    enable_month = fields.Boolean("Enable Monthdays")
    enable_zero_payslip = fields.Boolean("Enable Zero Payslip")
    min_value_nssf = fields.Integer("Minimum Value")
    max_value_nssf = fields.Integer("Maximum Value")


    @api.multi
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.esi_start_date or False
        field2 = self.esi_end_date or False
        field3 = self.insurance_start_date or False
        field4 = self.check_health_insurance or False
        field5 = self.check_health_insurance_self or False
        field6 = self.check_el_deduction or False
        field7 = self.payroll_data or False
        field8 = self.enable_canteen_deduction or False
        field9 = self.enable_canteen_excel or False
        field10 = self.enable_health_insurance_form or False
        field11 = self.last_date_of_submitting_health_insurance_details or False
        field12 = self.check_bank_update or False
        field13 = self.enable_month or False
        field14 = self.enable_zero_payslip or False
        field15 = self.max_value_nssf or 0
        field16 = self.min_value_nssf or 0
        param.set_param('payroll_inherit.min_value_nssf', field14)
        param.set_param('payroll_inherit.max_value_nssf', field15)
        param.set_param('payroll_inherit.run_esi_schedule_start_date', field1)
        param.set_param('payroll_inherit.run_esi_schedule_end_date', field2)
        param.set_param('payroll_inherit.insurance_start_date', field3)
        param.set_param('payroll_inherit.check_health_insurance', field4)
        param.set_param('payroll_inherit.check_health_insurance_self', field5)
        param.set_param('payroll_inherit.check_el_deduction', field6)
        param.set_param('payroll_inherit.payroll_data', field7)
        param.set_param('payroll_inherit.enable_canteen_deduction', field8)
        param.set_param('payroll_inherit.enable_canteen_excel', field9)
        param.set_param('payroll_inherit.enable_health_insurance_form', field10)
        param.set_param('payroll_inherit.enable_health_insurance_home_page', field10)
        param.set_param('payroll_inherit.last_date_of_submitting_health_insurance_details', field11)
        param.set_param('payroll_inherit.check_bank_update', field12)
        param.set_param('payroll_inherit.enable_month', field13)
        param.set_param('payroll_inherit.enable_zero_payslip', field14)
        param.set_param('payroll_inherit.max_value_nssf', field15)
        param.set_param('payroll_inherit.min_value_nssf', field16)
        
        

        

    @api.model
    def get_values(self):
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo()
        res.update(
            esi_start_date=param.get_param('payroll_inherit.run_esi_schedule_start_date'),
            esi_end_date=param.get_param('payroll_inherit.run_esi_schedule_end_date'),
            insurance_start_date=param.get_param('payroll_inherit.insurance_start_date'),
            check_health_insurance=param.get_param('payroll_inherit.check_health_insurance'),
            check_health_insurance_self=param.get_param('payroll_inherit.check_health_insurance_self'),
            check_el_deduction=param.get_param('payroll_inherit.check_el_deduction'),
            payroll_data=param.get_param('payroll_inherit.payroll_data'),
            enable_canteen_deduction=param.get_param('payroll_inherit.enable_canteen_deduction'),
            enable_canteen_excel=param.get_param('payroll_inherit.enable_canteen_excel'),
            enable_health_insurance_form=param.get_param('payroll_inherit.enable_health_insurance_form'),
            last_date_of_submitting_health_insurance_details =param.get_param('payroll_inherit.last_date_of_submitting_health_insurance_details'),
            enable_health_insurance_home_page=param.get_param('payroll_inherit.enable_health_insurance_home_page'),
            check_bank_update =param.get_param('payroll_inherit.check_bank_update'),
            enable_month=param.get_param('payroll_inherit.enable_month'),
            enable_zero_payslip=param.get_param('payroll_inherit.enable_zero_payslip'),
            min_value_nssf=int(param.get_param('payroll_inherit.min_value_nssf')),
            max_value_nssf=int(param.get_param('payroll_inherit.max_value_nssf')),
            
        )

        return res
