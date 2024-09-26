from odoo import fields,api,models
import math
from datetime import datetime, timedelta, date
from pytz import timezone, UTC
from dateutil.relativedelta import relativedelta


class LateComingReport(models.Model):
    _name="pf.ledger.report"
    _description="PF Ledger Report"
    _order = "create_date asc"


    employee_id = fields.Many2one('hr.employee',string="Employee")
    branch_id = fields.Many2one('res.branch',string="Center", store=True)
    # holiday_id = fields.Many2one('resource.calendar',string="Holiday Calendar")
    # name = fields.Char(string="Holiday")
    # date = fields.Date(string="Date")
    ledger_for_year = fields.Many2one('date.range', string='Ledger for the year')
    month = fields.Char(string='Month (Basic+DA)')
    epmloyee_contribution = fields.Char('EPF')
    voluntary_contribution = fields.Char('MPF + VPF')
    employer_contribution = fields.Char('Employer (C)')
    interest_employee_voluntary = fields.Char('Interest (EPF)')
    interest_employer = fields.Char('Interest (MPF + VPF)')
    total = fields.Char('Total')
    # is_current_month = fields.Boolean(compute="_check_current_month", store=True)
    # is_not_sat_sun = fields.Boolean(compute="_check_sat_sun", store=True)
    #
    #
    # @api.depends('date')
    # def _check_current_month(self):
    #     for rec in self:
    #         first_day = date.today().replace(day=1)
    #         last_day = date.today().replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
    #         if rec.date:
    #             if first_day <= rec.date <= last_day:
    #                 rec.is_current_month = True
    #             else:
    #                 rec.is_current_month = False
    #
    # @api.depends('month')
    # def _check_sat_sun(self):
    #     for rec in self:
    #         if rec.name == 'Sunday' or rec.name == 'Saturday':
    #             rec.is_not_sat_sun = True
    #         else:
    #             rec.is_not_sat_sun = False


class PFActualLedgerReport(models.Model):
    _name="stpi_pf_ledger_report"
    _description="PF Ledger Report"
    _order = "create_date asc"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    branch_id = fields.Many2one('res.branch', 'Center')
    month = fields.Char('Month')
    date_range_id = fields.Many2one('date.range', 'Ledger for the year')
    employee_contribution = fields.Float('Deposit (MPF)')
    employee_volun_contribution = fields.Float('Deposit (VPF)')
    deposit_employer_contribution = fields.Float('Deposit (EPF)')
    deposit_employee_contribution = fields.Float('Deposit (MPF + VPF)')
    withdraw_employer_contribution = fields.Float('Withdraw (EPF)')
    withdraw_employee_contribution = fields.Float('Withdraw (MPF + VPF)')
    total_employer_contribution = fields.Float('Total (EPF)')
    total_employee_contribution = fields.Float('Total (MPF + VPF)')
    total_pf_contribution = fields.Float('Total (PF)')
    main_rel = fields.Many2one('stpi_pf_ledger_report_main', 'Main Rel')
    
    


class PFActualLedgerMain(models.Model):
    _name="stpi_pf_ledger_report_main"
    _description="PF Ledger Report Main"
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    branch_id = fields.Many2one('res.branch', 'Center')
    date_range_id = fields.Many2one('date.range', 'Ledger for the year')
    is_closed = fields.Boolean('Closed', default=False)
    closed_on = fields.Date('Closed On')
    child_rel = fields.One2many("stpi_pf_ledger_report","main_rel", string="Ledger Report")
    