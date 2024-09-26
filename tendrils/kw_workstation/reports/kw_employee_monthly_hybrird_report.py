from calendar import calendar
import datetime
from odoo import tools
from odoo import models, fields, api


class EmployeeWorkstationhybridReport(models.Model):
    _name = "kw_emp_monthly_hybrid_report"
    _description = "Employee Monthly Hybrid Report"
    _auto = False
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    emp_name = fields.Char(related="employee_id.name", string="Employee Name")
    emp_code = fields.Char(related="employee_id.emp_code", string="Employee Code")
    workstation_id = fields.Many2one('kw_workstation_master', string="Workstation", domain=[('is_hybrid', '=', True)])
    branch_id = fields.Many2one('kw_res_branch', string='Location')
    assign_date = fields.Date(string="Assign Date")
    # week1 = fields.Char(string="Week1")
    # week2 = fields.Char(string="Week2")
    # week3 = fields.Char(string="Week3")
    # week4 = fields.Char(string="Week4")
    # week5 = fields.Char(string="Week5")

    def get_weekly_date(self):
        workstations = self.env['kw_workstation_master'].search([('is_hybrid', '=', True)])
        if workstations:
            year = datetime.datetime.today().year
            month = datetime.datetime.today().month
            first_date_of_month = datetime.date.today().replace(day=1)
            last_day = calendar.monthrange(year, month)[1]
            last_day_of_month = datetime.date.today().replace(day=last_day)
            firstweekday = 0
            calender_data = calendar.Calendar(firstweekday)
            for weekstart in filter(lambda d: d.weekday() == firstweekday, calender_data.itermonthdates(year, month)):
                for workstation in workstations:
                    workstation_id = workstation.id
                    weekend = weekstart + datetime.timedelta(4)
                    last_friday_date = weekstart - datetime.timedelta(4)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT
            emp.id,
            emp.employee_id AS employee_id,
            emp.workstation_id AS workstation_id,
            wm.branch_id AS branch_id,
            emp.assign_date AS assign_date
            FROM kw_workstation_assign emp
            LEFT JOIN kw_workstation_master wm ON wm.id = emp.workstation_id
            GROUP BY emp.id, emp.employee_id, emp.workstation_id, wm.branch_id
            
            )"""
        self.env.cr.execute(query)

        # SELECT
        #     id,
        #     employee_id,
        #     workstation_id,
        #     branch_id,
        #     MAX(CASE WHEN week_num = 1 THEN week_ranges END) AS week1,
        #     MAX(CASE WHEN week_num = 2 THEN week_ranges END) AS week2,
        #     MAX(CASE WHEN week_num = 3 THEN week_ranges END) AS week3,
        #     MAX(CASE WHEN week_num = 4 THEN week_ranges END) AS week4,
        #     MAX(CASE WHEN week_num = 5 THEN week_ranges END) AS week5
        # FROM (
        #     WITH week_assignments AS (
        #         SELECT
        #             emp.id,
        #             emp.employee_id,
        #             emp.workstation_id,
        #             wm.branch_id,
        #             DATE_TRUNC('week', emp.assign_date) AS week_start,
        #             TO_CHAR(MIN(emp.assign_date), 'DD-Mon') AS week_start_formatted,
        #             TO_CHAR(MIN(emp.assign_date + INTERVAL '4 days'), 'DD-Mon') AS week_end_formatted,
        #             ROW_NUMBER() OVER (PARTITION BY EXTRACT(YEAR FROM emp.assign_date), EXTRACT(MONTH FROM emp.assign_date) ORDER BY emp.assign_date) AS week_num
        #         FROM kw_workstation_assign emp
        #         LEFT JOIN kw_workstation_master wm ON wm.id = emp.workstation_id
        #         WHERE
        #             EXTRACT(DOW FROM emp.assign_date) = 1 
        #         GROUP BY
        #             emp.id, emp.employee_id, emp.workstation_id, wm.branch_id, DATE_TRUNC('week', emp.assign_date)
        #     )
        #     SELECT
        #         id,
        #         employee_id,
        #         workstation_id,
        #         branch_id,
        #         string_agg(
        #             week_start_formatted || ' to ' || week_end_formatted,
        #             E'\n'
        #         ) AS week_ranges,
        #         week_num
        #     FROM week_assignments
        #     GROUP BY
        #         id, employee_id, workstation_id, branch_id, week_num
        #     ORDER BY
        #         id, employee_id, workstation_id, branch_id, week_num
        # ) AS week_data
        # GROUP BY
        #     id, employee_id, workstation_id, branch_id
        # ORDER BY
        #     id, employee_id, workstation_id, branch_id
