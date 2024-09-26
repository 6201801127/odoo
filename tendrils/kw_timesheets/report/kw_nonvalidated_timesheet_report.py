from odoo import models, fields, api, tools
from datetime import date, datetime, time

class Nonvalidated_Timesheet_Report(models.Model):
    _name = 'kw_nonvalidated_timesheet_report'
    _description = 'kw_nonvalidated_timesheet_report'
    _auto = False

    date = fields.Date(string='Date', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    project_category_id = fields.Many2one('kw_project_category_master', string='Category Name')
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    task_id = fields.Many2one('project.task', string='Task', readonly=True)
    name = fields.Char(string='Description', readonly=True)
    pending_at = fields.Char(compute='_compute_pending_at', string='Pending At')
    unit_amount = fields.Float(string='Duration (Hours)', readonly=True)

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
    #     args += [('employee_id','=',current_employee.id)]
    #     return super(Nonvalidated_Timesheet_Report, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.multi
    def _compute_pending_at(self):
        project_work = self.env['kw_project_category_master'].search([('mapped_to', '=', 'Project')], limit=1)
        for record in self:
            names = []
            if record.employee_id.parent_id and record.employee_id.parent_id.name:
                names.append(record.employee_id.parent_id.name)
            if record.employee_id.coach_id and record.employee_id.coach_id.name:
                names.append(record.employee_id.coach_id.name)

            record.pending_at = ', '.join(names)

            if record.project_category_id == project_work:
                # employee is tech lead
                if record.employee_id.emp_category.code == 'TTL':
                    # employee not pm not pr
                    if record.project_id.emp_id != record.employee_id and \
                            record.project_id.reviewer_id != record.employee_id:
                        record.pending_at = record.project_id.emp_id and record.project_id.emp_id.name or ''
                    # employee pm not pr
                    if record.project_id.emp_id == record.employee_id and \
                            record.project_id.reviewer_id != record.employee_id:
                        record.pending_at = record.project_id.reviewer_id and record.project_id.reviewer_id.name or ''
                # employee not tech lead
                elif record.employee_id.emp_category.code != 'TTL':
                    # task has team lead
                    if record.task_id.tl_employee_id:
                        if record.project_id.emp_id != record.employee_id and \
                                record.task_id.tl_employee_id != record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.task_id.tl_employee_id and record.task_id.tl_employee_id.name or ''
                        elif record.project_id.emp_id != record.employee_id and \
                                record.task_id.tl_employee_id == record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.project_id.emp_id and record.project_id.emp_id.name or ''
                        elif record.project_id.emp_id == record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.project_id.reviewer_id and record.project_id.reviewer_id.name or ''
                    # task has no team lead
                    if not record.task_id.tl_employee_id:
                        if record.project_id.emp_id != record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.project_id.emp_id and record.project_id.emp_id.name or ''
                        if record.project_id.emp_id == record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.project_id.reviewer_id and record.project_id.reviewer_id.name or ''
                if record.project_id.emp_id == record.employee_id and not record.project_id.reviewer_id:
                    record.pending_at = record.employee_id.parent_id and record.employee_id.parent_id.name or ''


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
            aal.unit_amount AS unit_amount
            FROM
                account_analytic_line aal
            where active = true and validated = false          
         )""" % (self._table))