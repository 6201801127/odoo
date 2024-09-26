from odoo import models, fields, api, tools
import datetime
from datetime import date, timedelta
from math import ceil


class BeverageType(models.Model):
    _name = "central_bench_report_history"
    _description = "Central Bench History Report"

    employee_id = fields.Many2one('hr.employee')
    date_from = fields.Date("From Date")
    date_to = fields.Date("To Date")
    closed_bool = fields.Boolean("Status")


class CentralBenchHeadCount(models.Model):
    _name = 'central_bench_ctc'
    _description = 'central_bench_ctc'
    _auto = False

    MONTH_LIST = [('1', 'January'), ('2', 'February'),
                  ('3', 'March'), ('4', 'April'),
                  ('5', 'May'), ('6', 'June'),
                  ('7', 'July'), ('8', 'August'),
                  ('9', 'September'), ('10', 'October'),
                  ('11', 'November'), ('12', 'December')
                  ]

    year_data = fields.Char(string='Year')
    month_data = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    # technology = fields.Many2one('kw_skill_master',string="Technology")
    week1_count = fields.Integer(string='Week 1 Count')
    week1_ctc = fields.Float(string='Week 1 CTC')
    week2_count = fields.Integer(string='Week 2 Count')
    week2_ctc = fields.Float(string='Week 2 CTC')
    week3_count = fields.Integer(string='Week 3 Count')
    week3_ctc = fields.Float(string='Week 3 CTC')
    week4_count = fields.Integer(string='Week 4 Count')
    week4_ctc = fields.Float(string='Week 4 CTC')
    week5_count = fields.Integer(string='Week 5 Count')
    week5_ctc = fields.Float(string='Week 5 CTC')
    c_date = fields.Date('Date')

    @api.model_cr
    def init(self):
        current_date = date.today()
        year_data = self.env.context.get('year_data') if self.env.context.get('year_data') else current_date.year
        month_data = self.env.context.get('month_data') if self.env.context.get('month_data') else current_date.month

        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
       SELECT row_number() over() as id,
                current_date as c_date,
				a.year_data as year_data,
				a.month_data as month_data,
                sum(a.count) FILTER (WHERE a.week = 1 ) as week1_count,
                sum(a.total_ctc) FILTER (WHERE a.week = 1) as week1_ctc,
                
                sum(a.count) FILTER (WHERE a.week = 2) as week2_count,
                sum(a.total_ctc) FILTER (WHERE a.week = 2) as week2_ctc,
                
                sum(a.count) FILTER (WHERE a.week = 3) as week3_count,
                sum(a.total_ctc) FILTER (WHERE a.week = 3) as week3_ctc,
                
                sum(a.count) FILTER (WHERE a.week = 4) as week4_count,
                sum(a.total_ctc) FILTER (WHERE a.week = 4) as week4_ctc,
                
                sum(a.count) FILTER (WHERE a.week = 5) as week5_count,
                sum(a.total_ctc) FILTER (WHERE a.week = 5) as week5_ctc                
                
                from central_bench_weekly_ctc_report a group by year_data,month_data               
                
         )""" % (self._table))
