from calendar import monthrange
from datetime import date, datetime
from odoo import tools
from odoo import models, fields, api


class TimesheetReport(models.Model):
    _name = "kw_timesheet_calendar_report"
    _description = "Timesheet Calendar report Summary"
    _auto = False
    _rec_name = 'employee_id'

    employee_name = fields.Char(string='Employee Name')
    employee_id = fields.Char(string='Employee Id', )
    date = fields.Date("Date")
    timesheet_effort = fields.Char("Timesheet Effort")
    month_name = fields.Char(string="Month name")
    project_id = fields.Many2one('project.project', string="Project")
    task_id = fields.Many2one('project.task', string="Activity")
    effort = fields.Char("Effort")
    opportunity = fields.Char("Opportunity/Work Order")
    display_task_duration = fields.Char('Task Details', compute="compute_display_task_duration")
    category_name = fields.Many2one("kw_project_category_master", string="Category")
    category_mapped_to = fields.Selection(string="Category Mapped To", related="category_name.mapped_to")
    desc = fields.Text("Description")

    @api.multi
    def compute_display_task_duration(self):
        for record in self:
            task_name = record.task_id.name if record.task_id else ''
            record.display_task_duration = task_name + " : " + record.timesheet_effort + " (Hour(s))"

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            SELECT t.id, e.name AS employee_name, employee_id, t.date, 
            TO_CHAR(t.date, 'FMMonth') AS month_name, coalesce(cl.name,'') AS opportunity,
            sum(unit_amount) AS timesheet_effort, t.project_id AS project_id,t.task_id AS task_id, t.name AS desc, t.prject_category_id AS category_name,
            coalesce(Cast(TO_CHAR((sum(unit_amount) || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') AS varchar), '00 Hrs : 00 Mins') AS effort
            FROM account_analytic_line t 
            JOIN hr_employee e on e.id = t.employee_id
            LEFT JOIN crm_lead cl on cl.id = t.crm_lead_id
            GROUP BY t.id,e.name,employee_id, t.date,cl.name
 
            )""" % (self._table))
