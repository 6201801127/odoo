# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from datetime import datetime,date
from odoo.tools.misc import format_date
from odoo.addons.kw_hr_leaves.models.hr_leave_allocation import LAPSE_TYPE_CF

# from odoo.addons.kw_hr_leaves.models import hr_leave
# start_date, end_date = hr_leave.lv_get_current_financial_dates()

class KwHrLeaveReport(models.Model):
    _name           = "kw_hr_leave_type_report"
    _description    = 'Leave Type Report'
    _auto           = False

    employee_id         = fields.Many2one('hr.employee', string="Employee", readonly=True)
    leave_id            = fields.Many2one("hr.leave", string="Leave", readonly=True)
    applied_date        = fields.Date(string='Applied On',compute='_compute_applied_date')
    no_of_days_applied  = fields.Float(related='leave_id.actual_number_of_days',string='Leave Applied')
    no_of_days_approved = fields.Float(related='leave_id.number_of_days',string='Leave Approved')
    # hr_allocation_id    = fields.Many2one("hr.leave.allocation", string="Allocation", readonly=True)
    department          = fields.Char(string="Department",related="employee_id.department_id.name")
    division            = fields.Char(string="Division",related="employee_id.division.name")
    section             = fields.Char(string="Section",related="employee_id.section.name")
    designation         = fields.Char(string="Designation",related="employee_id.job_id.name")
    holiday_status_id   = fields.Many2one("hr.leave.type", string="Leave Type", readonly=True)
    taken               = fields.Float(string="Taken")
    entitle             = fields.Float(string="Entitled")
    balance             = fields.Float(string='Balance')
    lapse               = fields.Float(string='Lapse')
    fisc_year           = fields.Integer(string='Year')
    leave_cycle_id      = fields.Many2one("kw_leave_cycle_master", string="Leave Cycle", readonly=True)
    #type                = fields.Char(string="Type")
    type = fields.Selection([
        ('allocation', 'Entitlement'),
        ('request', 'Leave')
        ], string='Request Type', readonly=True)

    date_from           = fields.Date(string="Date From")
    date_to             = fields.Date(string="Date To")
    name                = fields.Text(string="Name")
    note_reason         = fields.Text(string="Reason")
    from_day_half       = fields.Char(string="Start Date", compute='_compute_from_to')
    to_day_half         = fields.Char(string="End Date", compute='_compute_from_to')
    action_taken_on     = fields.Date(string='Approved On')

    current_financial_year = fields.Boolean("Current Financial Year",compute='_compute_current_financial_year',search="_lv_search_current_financial_year")
    previous_financial_year = fields.Boolean("Previous Financial Year",compute='_compute_current_financial_year',search="_lv_search_previous_financial_year")

    @api.multi
    def _compute_applied_date(self):
        for leave in self:
            if leave.leave_id:
                leave.applied_date = leave.leave_id.create_date.date()
                
    @api.multi
    def _compute_from_to(self):
        for leave in self:
            if leave.leave_id:
                
                """From Day Half"""
                if leave.leave_id.request_unit_half :
                    if leave.leave_id.request_date_from_period == 'am':
                        leave.from_day_half = str(format_date(self.env , leave.leave_id.request_date_from) if leave.leave_id.request_date_from else '')+ " First Half"
                    if leave.leave_id.request_date_from_period == 'pm':
                        leave.from_day_half = str(format_date(self.env , leave.leave_id.request_date_from) if leave.leave_id.request_date_from else '')+ " Second Half"
                else :
                    leave.from_day_half = format_date(self.env , leave.leave_id.request_date_from) if leave.leave_id.request_date_from else ''

                """To Day Half"""
                if leave.leave_id.request_unit_half_to_period :
                    if leave.leave_id.request_date_to_period == 'am':
                        leave.to_day_half = str(format_date(self.env , leave.leave_id.request_date_to) if leave.leave_id.request_date_to else '')+ " First Half"
                    if leave.leave_id.request_date_to_period == 'pm':
                        leave.to_day_half = str(format_date(self.env , leave.leave_id.request_date_to) if leave.leave_id.request_date_to else '')+ " Second Half"
                else :
                    leave.to_day_half = format_date(self.env , leave.leave_id.request_date_to) if leave.leave_id.request_date_to else ''
            else:
                leave.from_day_half = leave.date_from if leave.date_from else False
                leave.to_day_half = leave.date_to if leave.date_to else False

    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass
    
    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        # print(start_date , end_date)
        domain = [('fisc_year', '=', start_date.year)]
        return domain
    
    @api.multi
    def _lv_search_previous_financial_year(self, operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        # print(start_date , end_date)
        domain = [('fisc_year', '=', start_date.year - 1)]
        return domain
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'kw_hr_leave_type_report')

        self._cr.execute(f"""
            CREATE or REPLACE view kw_hr_leave_type_report as (

            WITH EMP as (select HR.id as emp_id, HR.name as emp_name, LT.id  as leave_id, LT.name as leave_name,G_YR.* 
		            from  hr_leave_type LT,hr_employee HR,generate_series(2020,date_part('year', CURRENT_DATE)::int) G_YR where HR.active = True and LT.active = True) 
			
	        SELECT row_number() over(ORDER BY EMP.emp_id) as id, EMP.emp_id as employee_id, EMP.emp_name as name, EMP.leave_id as holiday_status_id, EMP.leave_name,EMP.G_YR as fisc_year,coalesce(leaves.taken,0) as taken,coalesce(leaves.entitle,0) as entitle,coalesce(leaves.balance,0) as balance,coalesce(leaves.lapse,0) as lapse ,leaves.leave_cycle_id, leaves.type,coalesce(leaves.date_from,null) as date_from,coalesce(leaves.date_to,null) as date_to,leaves.leave_id as leave_id,date(leaves.action_taken_on) as action_taken_on,leaves.name as note_reason
            FROM EMP
	        LEFT JOIN 
                (
               
                select
                    allocation.employee_id as employee_id,
                    allocation.name as name,
                    allocation.number_of_days as number_of_days,                    
                    allocation.holiday_status_id as holiday_status_id,                    
                    allocation.state as state,
                    allocation.holiday_type,
                    null as date_from,
                    null as date_to,
                    allocation.leave_cycle_id as leave_cycle_id,
                    allocation.cycle_period   as cycle_period,
                    null as leave_id,
                    allocation.action_taken_on as action_taken_on,

                    (case when (allocation.number_of_days>0) then coalesce(allocation.number_of_days,0) else 0 end) as entitle,
                    0 as taken,
                    coalesce(allocation.number_of_days,0) as balance,
                    (case when allocation.number_of_days<0 then coalesce((allocation.number_of_days * -1),0) else 0 end) as lapse,
                    'allocation' as type
                from hr_leave_allocation as allocation where state ='validate'
                union all select
                    request.employee_id as employee_id,
                    request.name as name,
                    request.number_of_days as number_of_days,                    
                    request.holiday_status_id as holiday_status_id,
                    request.state as state,
                    request.holiday_type,
                    request.request_date_from as date_from,
                    request.request_date_to as date_to,
                    request.leave_cycle_id as leave_cycle_id,
                    request.cycle_period   as cycle_period,
                    request.id as leave_id,
                    request.action_taken_on as action_taken_on,
                    0 as entitle,
                    coalesce(request.number_of_days,0) as taken,
                    coalesce((request.number_of_days * -1),0) as balance,
                    0 as lapse,
                    'request' as type
                from hr_leave as request 
                where state ='validate' ) leaves                 
                ON EMP.emp_id = leaves.employee_id AND EMP.leave_id = leaves.holiday_status_id AND EMP.G_YR = leaves.cycle_period
            );
        """)