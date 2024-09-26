# *******************************************************************************************************************
#  File Name             :   kw_emp_month_wise_report.py
#  Description           :   This model is used to filter employee status details month wise
#  Created by            :   Monalisha rout
#  Created On            :   02-11-2023
#  Modified by           :   Monalisha Rout
#  Modified On           :   
#  Modification History  :  
# *******************************************************************************************************************

from odoo import fields, models, api, tools
from datetime import date, datetime, time
import calendar

def get_years():
    year_list = []
    for i in range((date.today().year), 1998, -1):
        year_list.append((i, str(i)))
    return year_list

class MonthlyReportFilter(models.TransientModel):
    _name = 'kw_monthly_emp_report_filter'
    _description = 'Filter'
    

    from_date = fields.Date()
    to_date = fields.Date()
    company_id = fields.Many2one('res.company')
    
    # year = fields.Selection(get_years(), string='Year')
    # month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'),
    #                                           (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'),
    #                                           (10, 'October'), (11, 'November'), (12, 'December')],
    #                                         ) 
    # 
     
    def btn_fetch_employee(self):
        # self.env['kw_emp_month_wise_report'].with_context(date_from=date(int(self.year),int(self.month),1),date_to= date(int(self.year),int(self.month), calendar.monthrange(int(self.year), int(self.month))[1])).init()
        self.env['kw_emp_month_wise_report'].with_context(date_from=self.from_date,date_to= self.to_date,company_id=self.company_id.id).init()
        view_id = self.env.ref('kw_management_report.kw_emp_month_wise_report_tree_view').id
        return {
            'name':'Employee Details',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'kw_emp_month_wise_report',
            'view_id': view_id,
            'target': 'current',
        }
   
class MonthlyMISReport(models.Model):
    _name = 'kw_emp_month_wise_report'
    _description = 'MIS Report'
    _order = 'name'
    _auto = False

    emp_code = fields.Char()
    name = fields.Char()
    date_of_joining = fields.Date('DOJ')
    age = fields.Float()
    department_id = fields.Many2one('hr.department', string='Department')
    last_working_day = fields.Date('Exit Date')
    emp_grade = fields.Many2one(string=u'Grade', comodel_name='kwemp_grade_master')
    job_id = fields.Many2one('hr.job','Designation')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'),('other', 'Other')])
    birthday = fields.Date('DOB')
    employement_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment")#16
    age_group = fields.Char(compute='compute_age_group',string='Age Group')
    # num_absent_days = fields.Char(compute='compute_absent_days',)
    num_absent_days = fields.Char()
    emp_id = fields.Integer()
    attendance_month= fields.Integer()
    attendance_year= fields.Integer()
    job_branch_id = fields.Many2one('kw_res_branch', string="Work Location")
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practice")
    practise = fields.Many2one('hr.department', string="Section")
    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU")
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],
                                   string="Budget Type")
    emp_band = fields.Many2one('kwemp_band_master', string="Band", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    present_add_state =  fields.Many2one('res.country.state')
    permanent_add_state = fields.Many2one('res.country.state')
    emp_religion = fields.Many2one('kwemp_religion_master', string="Religion")
    blood_group = fields.Many2one('kwemp_blood_group_master', string="Blood Group")
    previous_company_experience_display_abbr = fields.Float(compute="_compute_exp",string='Previous Exp.')
    total_experience_years = fields.Float()
    total_experience_months= fields.Float()
    emp_sts = fields.Char()

    
    @api.depends('age')
    def compute_age_group(self):
        age_ranges = [(18, 31), (31, 41), (41, 51), (51, 61)]
        for rec in self:
            if rec.age:
                for age_range in age_ranges:
                    min_age, max_age = age_range
                    if min_age <= rec.age < max_age:
                        rec.age_group = f'{min_age} - {max_age-1}'
                        
    @api.depends('total_experience_years','total_experience_months')
    def _compute_exp(self):
        for rec in self:
            if rec.total_experience_years or rec.total_experience_months:
                rec.previous_company_experience_display_abbr = rec.total_experience_years + rec.total_experience_months/100

    # @api.depends('emp_id')
    # def compute_absent_days(self):
    #     for rec in self:
    #         if rec.emp_id and rec.attendance_year and rec.attendance_month:
    #             att = self.env['kw_employee_monthly_payroll_info'].sudo().search([('attendance_year','=',int(rec.attendance_year)),('attendance_month','=',int(rec.attendance_month)),('employee_id','=',rec.emp_id)])
    #             if att:
    #                 rec.num_absent_days = att.num_absent_days
    #             else:
    #                 rec.num_absent_days = '--'

    @api.model_cr
    def init(self):
        date_from = self.env.context.get('date_from') if self.env.context.get('date_from') else date.today()
        date_to = self.env.context.get('date_to') if self.env.context.get('date_to') else date.today()
        company_id = self.env.context.get('company_id') if self.env.context.get('company_id') else 1
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""
            CREATE or REPLACE VIEW {self._table} as (
            select row_number() over() as id,
            hr.id as emp_id,
            hr.emp_code,
            hr.name,
            hr.date_of_joining,
            hr.department_id,
            hr.last_working_day,
            hr.grade as emp_grade,
            hr.job_id,
            hr.gender,
            hr.birthday,
            hr.employement_type,
            hr.job_branch_id,
            hr.division,
            hr.section,
            hr.practise,
            hr.sbu_master_id,
            hr.budget_type,
            hr.emp_band,
            hr.present_addr_state_id as present_add_state,
            hr.permanent_addr_state_id as permanent_add_state,
            hr.emp_religion,
            hr.blood_group as blood_group,
            COALESCE(
                FLOOR(SUM(date_part('year', AGE(kw.effective_to, kw.effective_from)))::Integer) +
                FLOOR(SUM(date_part('month', AGE(kw.effective_to, kw.effective_from)))::Integer / 12),
                0
            ) AS total_experience_years,
            case when hr.date_of_joining between '{date_from}' and  '{date_to}' then 'New'
                when hr.date_of_joining <  '{date_from}' then 'Continuing'
                when hr.last_working_day between '{date_from}' and  '{date_to}' then 'Left'
            end as emp_sts,
                
            SUM(date_part('month', AGE(kw.effective_to, kw.effective_from)))::Integer % 12 AS total_experience_months,
            {date_from.month} as attendance_month,
            {date_from.year} as attendance_year,
            date_part('year', age('{date_from}', hr.birthday)) AS age,
            
            (select sum(case 
				when leave_status = '1' then 0
		  		when leave_status = '2' then .5
		  		when leave_status = '3' then .5
		  		else 1
		  		end) from kw_daily_employee_attendance where employee_id = hr.id 
and attendance_recorded_date >= '{date_from}' and attendance_recorded_date <='{date_to}' and state='2' 
and day_status in ('0','3'))as num_absent_days
            FROM
            hr_employee AS hr 
            left JOIN kwemp_work_experience AS kw ON hr.id = kw.emp_id
            WHERE hr.company_id = {company_id} AND
            (date_of_joining <= '{date_from}' AND last_working_day IS NULL and hr.employement_type is not null and hr.job_id is not null and active=true)
            OR (last_working_day > '{date_from}' AND date_of_joining <= '{date_from}' and hr.employement_type is not null and hr.job_id is not null and active=false)
            OR (last_working_day between '{date_from}' and '{date_to}' and date_of_joining between '{date_from}' and '{date_to}' and hr.employement_type is not null and hr.job_id is not null and active=false)
            OR (date_of_joining between '{date_from}' and '{date_to}' and hr.employement_type is not null and hr.job_id is not null)
            group by hr.id
            )"""
        
        self.env.cr.execute(query)
