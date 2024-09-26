from odoo import api,models,fields
from odoo import tools
from datetime import date, datetime, time

class SbuTourExpenseReport(models.Model):
    _name           = "kw_sbu_tour_expense_report"
    _description    = "SBU Tour Expense Report Summary"
    _auto = False


    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month_name = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    sbu_name = fields.Char('SBU Name')
    no_of_employee = fields.Char('No of Employee')
    total_expense = fields.Float( 'Tour Expense')
    sbu_id = fields.Many2one('kw_sbu_master')

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() OVER () AS id,
        (SELECT name FROM kw_sbu_master WHERE id = hr.sbu_master_id AND type = 'sbu') AS sbu_name,
        COUNT(hr.name) AS no_of_employee,
        hr.sbu_master_id as sbu_id,
        SUM(ts.total_budget_expense) AS total_expense,
        date_part('year',ts.applied_date)::VARCHAR as year,
        date_part('month',ts.applied_date)::VARCHAR as month_name
        FROM
            hr_employee AS hr
        JOIN
            kw_tour_settlement AS ts ON hr.id = ts.employee_id
        WHERE
            ts.state in ('Granted','Payment Done') AND hr.sbu_type = 'sbu' and hr.active=True
        GROUP BY
            sbu_name, year, month_name,sbu_id order by month_name
        )""" % (self._table))


