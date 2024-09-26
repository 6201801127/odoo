from odoo import api,models,fields
from odoo import tools
from datetime import date, datetime, time

class TimesheetCtcReport(models.Model):
    _name           = "timesheet_per_hour_ctc_cost_report"
    _description    = "SBU Timesheet Ctc Report Summary"
    _auto = False


   
    year = fields.Char(string='Year')
    month_name = fields.Integer(string='Month')
    sbu_name = fields.Many2one('kw_sbu_master', string='SBU Name')
    average_ctc = fields.Float('CTC')
    employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    month = fields.Char( string='Month', compute='_compute_month_name')

    @api.depends('month_name')
    def _compute_month_name(self):
        month_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                      9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        for rec in self:
            month = rec.month_name
            rec.month = month_dict.get(month)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            with a as (
                select sum(a.unit_amount) as timesheet_effort,a.employee_id as employee_id,h.employement_type,b.sbu_id as sbu_name,h.date_to,count(l.amount),
                (l.amount/(select num_shift_working_days 
                                        from kw_employee_monthly_payroll_info where attendance_year = date_part('year',h.date_to)and
                                        attendance_month = date_part('month',h.date_to) and employee_id = a.employee_id))*sum(a.unit_amount)/8.5 as average_ctc
                        from account_analytic_line a join project_project b on a.project_id = b.id  
                        join hr_payslip h on a.employee_id = h.employee_id join hr_payslip_line l on h.id = l.slip_id
                        join hr_employee e on e.id = h.employee_id
                        where h.state = 'done' and l.code = 'CTC' and a.date between h.date_from and h.date_to and a.prject_category_id = (select id from kw_project_category_master where mapped_to = 'Project')
                        and e.sbu_type = 'horizontal'
                        group by a.employee_id,b.sbu_id,h.employement_type,h.date_to, l.amount order by h.date_to)
            select  row_number() OVER () AS id,
            date_part('year',date_to)::VARCHAR as year,date_part('month',date_to)::VARCHAR as month_name,sbu_name,employement_type,sum(average_ctc) as average_ctc 
            from a group by sbu_name,employement_type,date_to



        )""" % (self._table))


