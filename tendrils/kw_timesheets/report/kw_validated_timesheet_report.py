from odoo import models, fields, api, tools
from datetime import date, datetime, time


class Validated_Timesheet_Report(models.Model):
    _name = 'kw_validated_timesheet_report'
    _description = 'kw_validated_timesheet_report'
    _auto = False

    date = fields.Date(string='Date', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    project_category_id = fields.Many2one('kw_project_category_master', string='Category Name')
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    task_id = fields.Many2one('project.task', string='Task', readonly=True)
    name = fields.Char(string='Description', readonly=True)
    approved_by = fields.Char('Timesheet Approved By')
    unit_amount = fields.Float(string='Duration (Hours)', readonly=True)

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
    #     args += [('employee_id','=',current_employee.id)]

    #     return super(Validated_Timesheet_Report, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
        SELECT 
            ROW_NUMBER() OVER (order by aal.date desc, aal.id desc,aal.employee_id) AS id,
            aal.date AS date,
            aal.employee_id AS employee_id,
            aal.prject_category_id AS project_category_id,
            aal.project_id AS project_id,
            aal.task_id AS task_id,
            aal.name AS name,
            aal.approved_by AS approved_by,
            aal.unit_amount AS unit_amount
            FROM
                account_analytic_line aal
            where active = true and validated=true
         )""" % (self._table))
