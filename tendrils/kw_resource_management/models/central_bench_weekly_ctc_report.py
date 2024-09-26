from odoo import models, fields, api,tools
import datetime
from datetime import date,timedelta
from math import ceil
from dateutil.relativedelta import relativedelta
import calendar


class BeveraCentralBenchWeeklyCTCcountReportgeType(models.Model):
    _name="central_bench_weekly_ctc_report"
    _description = "Central Bench Weekly CTC count Report"

    MONTH_LIST = [

        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    year_data = fields.Char(string='Year')
    month_data = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    month = fields.Integer(string="Month")
    week= fields.Integer(string="Week")
    count = fields.Integer(string="Count")
    ctc_amount = fields.Float(string="Amount")
    month_selection = fields.Char(string='Month', compute='compute_month',store=True)
    week_selection = fields.Char(string='Week', compute='compute_week',store=True)
    emp_list = fields.Char()
    week_start = fields.Date("Week Start Date")
    week_end = fields.Date("Week End Date")
    total_ctc = fields.Float(string="Total CTC",store=True)
    technology_id = fields.Many2one('kw_skill_master',string="Technology")

            
    @api.multi
    @api.depends('month')
    def compute_month(self):
        month_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                      9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        for rec in self:
            month = rec.month
            rec.month_selection = month_dict.get(month)

    @api.multi
    @api.depends('week')
    def compute_week(self):
        week_dict = {1: 'Week 1', 2: 'Week 2', 3: 'Week 3', 4: 'Week 4', 5: 'Week 5', 6: 'Week 6'}
        for rec in self:
            week = rec.week
            rec.week_selection = week_dict.get(week)

    def update_central_ctc_count(self):
        # New code logic for weekly ctc count 
        current_date=date.today()
        last_day_of_month=current_date.replace(day = calendar.monthrange(current_date.year, current_date.month)[1])
        first_day_of_month=current_date.replace(day = 1)
        if current_date.weekday() == 6 or current_date == last_day_of_month:
            week_number =0
            start = current_date - timedelta(days=current_date.weekday())
            end = start + timedelta(days=6)
            
            if first_day_of_month >= start and first_day_of_month <= end:
                week_start,week_end = first_day_of_month,end
            elif last_day_of_month >= start and last_day_of_month <= end:
                week_start,week_end = start,last_day_of_month
            else:
                week_start,week_end = start,end
                
            list_of_days_in_month = (calendar.monthcalendar(int(current_date.year),int(current_date.month)))
            for i, sublist in enumerate(list_of_days_in_month):
                for j, number in enumerate(sublist):
                    if number == current_date.day:
                        positiion = (i,j)
                        week_number = positiion[0] + 1
                        
            central_bench_data = self.env['sbu_bench_resource'].sudo().search([]).mapped('employee_id.id')
            
            technologies = self.env['hr.employee'].sudo().search([('id','in',central_bench_data)]).mapped('primary_skill_id')
        
            for tech in technologies:
                # Add tech
                check_data = self.env['central_bench_weekly_ctc_report'].sudo().search([('week','=',week_number),('year_data','=',current_date.year),('month','=',int(current_date.month)),('technology_id','=',tech.id)])
                filtered_emp = self.env['hr.employee'].sudo().search([('id','in',central_bench_data),('primary_skill_id','=',tech.id)]).mapped('id')
                if check_data:
                    a=  eval(check_data.emp_list)
                    b = filtered_emp
                    unique_items = set(a + b)
                    unique_items_list = list(unique_items)
                    
                    
                    total_ctc = sum(self.env['hr.contract'].sudo().search([('employee_id.id','in',unique_items_list),('state','=','open')]).mapped('wage'))
                    
                
                        
                    diff_days = (week_end - week_start).days+1
                    
                    
                    check_data.write({
                        'technology_id':tech.id,
                        'emp_list':unique_items_list,
                        'count':len(unique_items_list),
                        'week_start':week_start,
                        'week_end':week_end,
                        'total_ctc':(total_ctc/last_day_of_month.day)*diff_days
                    })
                else:
                    filtered_emp = self.env['hr.employee'].sudo().search([('id','in',central_bench_data),('primary_skill_id','=',tech.id)]).mapped('id')
                    total_ctc = sum(self.env['hr.contract'].sudo().search([('employee_id.id','in',filtered_emp),('state','=','open')]).mapped('wage'))
                    
                    diff_days = (week_end - week_start).days+1
                    
                    check_data.create({
                        'technology_id':tech.id,
                        'year_data':current_date.year,
                        'month_data':str(current_date.month),
                        'month':int(current_date.month),
                        'week': week_number,
                        'emp_list':list(set(filtered_emp)),
                        'count':len(filtered_emp),
                        'week_start':week_start,
                        'week_end':week_end,
                        'total_ctc':(total_ctc/last_day_of_month.day)*diff_days

                    })    
                
