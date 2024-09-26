from odoo import api, fields, models, tools
from datetime import date, datetime

class SbuPlanReport(models.Model):
    _name="kw_sbu_plan_report"
    _auto=False  

    salary_date = fields.Char('Month')
    sbu_developer_count = fields.Integer('SBU Dev #')
    sbu_tl_count = fields.Integer('No. Of TL in SBU')
    sbu_ctc = fields.Float('SBU CTC')
    bench_developer_count = fields.Integer('Bench Dev #')
    bench_tl_count = fields.Integer('No. Of TL in Bench')
    bench_ctc = fields.Float('Bench CTC')
    date_to = fields.Date()
    year = fields.Char(compute='_compute_year_month')

    @api.depends('salary_date','date_to')
    def _compute_year_month(self):
        for rec in self:
            if rec.salary_date and rec.date_to:
                year = rec.date_to.year % 100
                rec.year = f'{rec.salary_date} - {year}'

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select row_number() over (order by p.date_to desc) as id, 
            p.date_to as date_to,count(hr.id) filter (where  hr.sbu_master_id is not null and  kw.code = 'DEV') as sbu_developer_count,
            count(hr.id) filter (where  hr.sbu_master_id is not null and  kw.code = 'TTL') as sbu_tl_count,
            sum(line.total) filter (where line.code = 'CTC' and  hr.sbu_master_id is not null and kw.code in ('DEV','TTL')) as sbu_ctc,
            count(hr.id) filter (where  hr.sbu_master_id is null and  kw.code = 'DEV') as bench_developer_count,
            count(hr.id) filter (where  hr.sbu_master_id is null and  kw.code = 'TTL') as bench_tl_count,
            sum(line.total) filter (where line.code = 'CTC' and  hr.sbu_master_id is  null and kw.code in ('DEV','TTL')) as bench_ctc,
            Case when line.month = 1 then 'JAN'
            when line.month = 2 then 'FEB'
            when line.month = 3 then 'MAR'
            when line.month = 4 then 'APR'
            when line.month = 5 then 'MAY'
            when line.month = 6 then 'JUN'
            when line.month = 7 then 'JUL'
            when line.month = 8 then 'AUG'
            when line.month = 9 then 'SEP'
            when line.month = 10 then 'OCT'
            when line.month = 11 then 'NOV'
            when line.month = 12 then 'DEC'
            end as salary_date
            from hr_employee as hr left join kwmaster_category_name as kw on hr.emp_category = kw.id  join
                        hr_payslip_line as line
                        on  hr.id = line.employee_id and line.code='CTC' join hr_payslip as p
                        on p.id = line.slip_id and p.state='done' where  hr.emp_role = (select id from kwmaster_role_name where code='DL')
            group by line.year,line.month,p.date_to
                    )"""% (self._table))
        