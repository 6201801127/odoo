# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from datetime import datetime,date

# from odoo.addons.kw_hr_leaves.models import hr_leave

# start_date, end_date = hr_leave.lv_get_current_financial_dates()

class KwHrLeaveReport(models.Model):
    _name = "kw_hr_leave_report"
    _description = 'Leave Summary / Report'
    _auto = False
    _order = "id asc" #"date_from DESC, employee_id"

    employee_id     = fields.Many2one('hr.employee', string="Employee", readonly=True)
    designation     = fields.Char(string="Designation",related='employee_id.job_id.name')
    department      = fields.Char(string="Department",related='employee_id.department_id.name')
    date_of_joining = fields.Date(string="Date of Joining",related='employee_id.date_of_joining')
    division        = fields.Char(string="Division",related='employee_id.division.name')
    section         = fields.Char(string="Section",related='employee_id.section.name')
    practice        = fields.Char(string='Practice',related='employee_id.practise.name')
    name            = fields.Char('Description', readonly=True)
    number_of_days  = fields.Float('Number of Days', readonly=True)
    
    type = fields.Selection([
        ('allocation', 'Allocation Request'),
        ('allocation_lapse', 'Allocation Lapse'),
        ('request', 'Leave Request')
        ], string='Request Type', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    category_id = fields.Many2one('hr.employee.category', string='Employee Tag', readonly=True)
    holiday_status_id = fields.Many2one("hr.leave.type", string="Leave Type", readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('hold', 'On Hold'),
        ('forward', 'Forwarded')
        ], string='Status', readonly=True)
    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('category', 'By Employee Tag')
    ], string='Allocation Mode', readonly=True)
    date_from = fields.Date('Start Date', readonly=True)
    date_to = fields.Date('End Date', readonly=True)
    payslip_status = fields.Boolean('Reported in last payslips', readonly=True)
    cycle_id       = fields.Many2one('kw_leave_cycle_master',string='Leave Cycle')
    cycle_period   = fields.Integer(string='Year',related='cycle_id.cycle_period')

    current_financial_year = fields.Boolean("Current Financial Year",compute='_compute_current_financial_year',search="_lv_search_current_financial_year")
    previous_financial_year = fields.Boolean("Previous Financial Year",compute='_compute_current_financial_year',search="_lv_search_previous_financial_year")

    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass
    
    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        domain = [('cycle_period', '=', start_date.year)]
        return domain

    @api.multi
    def _lv_search_previous_financial_year(self, operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        domain = [('cycle_period', '=', start_date.year - 1)]
        return domain

    def init(self):
        tools.drop_view_if_exists(self._cr, 'kw_hr_leave_report')

        self._cr.execute("""
            CREATE or REPLACE view kw_hr_leave_report as (
                SELECT row_number() over(ORDER BY leaves.date_from asc,leaves.holiday_status_id,leaves.employee_id) as id,
                    leaves.employee_id as employee_id, 
                    leaves.name as name,
                    leaves.number_of_days as number_of_days, 
                    leaves.type as type,
                    leaves.category_id as category_id, 
                    leaves.department_id as department_id,
                    leaves.holiday_status_id as holiday_status_id, 
                    leaves.state as state,
                    leaves.holiday_type as holiday_type, 
                    date(leaves.date_from) as date_from,
                    date(leaves.date_to) as date_to, 
                    leaves.payslip_status as payslip_status,
					leaves.cycle_id as cycle_id
                    from (select
                        allocation.employee_id as employee_id,
                        allocation.name as name,
                        allocation.number_of_days as number_of_days,
                        allocation.category_id as category_id,
                        allocation.department_id as department_id,
                        allocation.holiday_status_id as holiday_status_id,
                        allocation.state as state,
                        allocation.holiday_type,
                        allocation.validity_start_date as date_from,
                        allocation.validity_end_date as date_to,
                        FALSE as payslip_status,
						allocation.leave_cycle_id as cycle_id, 
                        case when number_of_days >=0 then 'allocation' when number_of_days <0 then 'allocation_lapse' end as type 
                    from hr_leave_allocation as allocation where state in ('validate')
                    union all select
                        request.employee_id as employee_id,
                        request.name as name,
                        (request.number_of_days * -1) as number_of_days,
                        request.category_id as category_id,
                        request.department_id as department_id,
                        request.holiday_status_id as holiday_status_id,
                        request.state as state,
                        request.holiday_type,
                        request.date_from as date_from,
                        request.date_to as date_to,
                        request.payslip_status as payslip_status,
						request.leave_cycle_id as cycle_id,
                        'request' as type
                    from hr_leave as request where state in ('validate')) leaves order by  cycle_id desc, holiday_status_id 
            );
        """)
