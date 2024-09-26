from datetime import datetime,date
from odoo import models, fields, api, tools, _
from dateutil import relativedelta

def lv_get_current_financial_dates():
    current_date = date.today()
    current_year = date.today().year
    if current_date < date(current_year, 4, 1):
        start_date = date(current_year-1, 4, 1)
        end_date = date(current_year, 3, 31)
    else:
        start_date = date(current_year, 4, 1)
        end_date = date(current_year+1, 3, 31)
    return start_date,end_date

cur_finance_year = lv_get_current_financial_dates()

class HrLeaveEncashmentReport(models.Model):
    _name           = "kw_carryforward_encashment_report"
    _description    = "Leave Carry Forward and Encashment Report"
    _auto           = False
    _order          = 'date_of_joining asc'

    employee_id     = fields.Many2one('hr.employee',string="Employee Name")
    emp_name        = fields.Char(related="employee_id.name",string="Name")
    emp_code        = fields.Char(related="employee_id.emp_code",string="Emp. Code")
    department      = fields.Char(string="Department",related="employee_id.department_id.name")
    division        = fields.Char(string="Division",related="employee_id.division.name")
    section         = fields.Char(string="Section",related="employee_id.section.name")
    designation     = fields.Char(string="Designation",related="employee_id.job_id.name")
    leave_type_id   = fields.Many2one("hr.leave.type", string="Leave Type",)
    date_of_joining = fields.Date(string="Date of Joining",related="employee_id.date_of_joining",store=False)
    #leave_type      = fields.Char(string="Leave Type")
    tot_entitlement = fields.Float(string="Entitlement Days",compute='_compute_days')
    tot_lapse_days  = fields.Float(string="Lapse Days")
    tot_leave_taken = fields.Float(string="Leave Days")

    cycle_period    = fields.Integer(string="Year")

    remaining_days      = fields.Float(string="Remaining Days",compute='_compute_days')
    carry_forward_days  = fields.Float(string="Carry Forward Days",compute='_compute_days')
    encashment_days     = fields.Float(string="Encashment Days",compute='_compute_days')
    retirement = fields.Boolean(string="Retirement")
  

    current_financial_year = fields.Boolean("Current Financial Year",compute='_compute_current_financial_year',search="_lv_search_current_financial_year")
    previous_financial_year = fields.Boolean("Previous Financial Year",compute='_compute_previous_financial_year',search="_lv_search_previous_financial_year")

    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass
    
    @api.multi
    def _compute_previous_financial_year(self):
        for record in self:
            pass

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            SELECT row_number() over(ORDER BY LEAVE_TABLE.employee_id) as id, LEAVE_TABLE.employee_id, LEAVE_TABLE.emp_code, LEAVE_TABLE.leave_type_id,
            LEAVE_TABLE.leave_type, LEAVE_TABLE.date_of_joining, LEAVE_TABLE.tot_entitlement, LEAVE_TABLE.tot_lapse_days, LEAVE_TABLE.tot_leave_taken,LEAVE_TABLE.cycle_period,
			LEAVE_TABLE.retirement as retirement
            FROM
            (
			select EMP.id as employee_id, emp.name , date_of_joining, emp_code, LV_TBL.leave_type_id,LV_TBL.leave_type, COALESCE(sum(LV_TBL.entitlement),0) tot_entitlement, COALESCE(sum(LV_TBL.lapse_days),0) tot_lapse_days, COALESCE(sum(LV_TBL.leave_taken),0) tot_leave_taken ,LV_TBL.cycle_period,
				case when EMP.active = False and eos.state = 'grant' and eos.offboarding_type = {self.env.ref('kw_eos.kw_offboarding_type_master3').id} then True else False End as retirement
			FROM  hr_employee EMP
			left join kw_resignation eos on eos.applicant_id = EMP.id and EMP.active = False and eos.state = 'grant' and eos.offboarding_type = {self.env.ref('kw_eos.kw_offboarding_type_master3').id}

			INNER JOIN
			(
				SELECT LVT.id as leave_type_id,LVT.name as leave_type,LV_CYL.id as cycle_id, LV_CYL.cycle_period, entitle as entitlement,lapse as lapse_days, LEAVE_TBL.employee_id ,taken as leave_taken
				FROM hr_leave_type LVT  
				LEFT JOIN kw_leave_cycle_master LV_CYL ON LV_CYL.cycle_id >0 
				LEFT JOIN
				(
					select employee_id,				                      
					       holiday_status_id,
					       leave_cycle_id,
					       cycle_period,
					       (case when (LVA.number_of_days>0 or lapse_alc_type =2) then coalesce(LVA.number_of_days,0) else 0 end) as entitle,
					       0 as taken,
					       (case when LVA.number_of_days<0 and lapse_alc_type =4 then coalesce((LVA.number_of_days * -1),0) else 0 end) as lapse,
					       'allocation' as type
					    from hr_leave_allocation LVA where LVA.holiday_status_id in (select id from hr_leave_type where carry_forward=True or encashable=True) and LVA.state = 'validate' 
					 UNION ALL
					    select employee_id,				                      
						holiday_status_id,
						leave_cycle_id,
						cycle_period,
						0 as entitle,
						coalesce(LV.number_of_days,0) as taken,
						0 as lapse,
						'request' as type
					    from hr_leave LV where LV.holiday_status_id in (select id from hr_leave_type where carry_forward=True or encashable=True) and LV.state in ('validate','forward','confirm') 
				)LEAVE_TBL ON LEAVE_TBL.holiday_status_id = LVT.id and LEAVE_TBL.leave_cycle_id = LV_CYL.id
				WHERE (LVT.carry_forward=True or LVT.encashable=True) and  LVT.active=True 

                )LV_TBL ON LV_TBL.employee_id = EMP.ID 
                group by LV_TBL.cycle_period,EMP.ID,LV_TBL.leave_type_id,LV_TBL.leave_type, eos.state, eos.offboarding_type
            )LEAVE_TABLE
        )""" % (self._table))   

    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        start_date,end_date = cur_finance_year
        return [('cycle_period', '=', start_date.year)]

    @api.multi
    def _lv_search_previous_financial_year(self, operator, value):
        start_date,end_date = cur_finance_year
        return [('cycle_period', '=', start_date.year - 1)]


    @api.multi
    def _compute_days(self):        
        start_date,end_date = cur_finance_year 
        for record in self:
            try:
                diff    = relativedelta.relativedelta(end_date, record.employee_id.date_of_joining) if record.employee_id.date_of_joining else False
                employee_service_years ,employee_service_months = diff.years,diff.months #if diff else 0,0

                active_cycle = self.env['kw_leave_cycle_master'].search([('branch_id', '=', record.employee_id.job_branch_id.id if record.employee_id.job_branch_id else False),('cycle_id', '!=', False), ('active', '=', True)], limit=1)
                tot_allocated = self.env['hr.leave.allocation'].search([('employee_id','=',record.employee_id.id),('holiday_status_id','=',record.leave_type_id.id),('leave_cycle_id','=',active_cycle.id),('cycle_period','=',active_cycle.cycle_period),('state','=','validate'),('number_of_days','>',0)])
                record.tot_entitlement = sum(tot_allocated.mapped('number_of_days'))
                
                leave_taken = self.env['hr.leave'].search([('employee_id','=',record.employee_id.id),('holiday_status_id','=',record.leave_type_id.id),('state','=','validate'),('cycle_period','=',active_cycle.cycle_period)])
                record.tot_leave_taken = sum(leave_taken.mapped('number_of_days'))
                
                record.remaining_days = record.tot_entitlement - record.tot_leave_taken - record.tot_lapse_days
                cf_percent,en_percent = 0 ,0
                if employee_service_years>=1:
                    en_percent = record.leave_type_id.encashable_percentage or 0
                    record.encashment_days      = record._get_day_values((record.remaining_days * en_percent)/100) 
                    record.carry_forward_days   = ((record.remaining_days - record.encashment_days))
                elif employee_service_years==0 and employee_service_months>=6 and employee_service_months<12:
                    cf_percent = record.leave_type_id.cf_less_than_year_percent or 0
                    record.carry_forward_days   = record._get_day_values((record.remaining_days * cf_percent)/100) 
                    record.encashment_days      = 0 
            except Exception as e:
                # print(e)
                record.remaining_days       = 0
                record.carry_forward_days   = 0
                record.encashment_days      = 0

    def _get_day_values(self,flt_days):
        int_value   = int(flt_days)
        frac        = flt_days - int_value
            
        return int_value+.5 if frac >=.5 else round(int_value)
      