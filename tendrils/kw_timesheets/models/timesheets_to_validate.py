# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ToValidateTimesheets(models.Model):
    _name = 'kw_timesheets_to_validate'
    _description = 'To validate the timesheets of subordinates'
    _auto = False



    t_date = fields.Date(string='Date')
    timesheet_id = fields.Many2one('account.analytic.line', string='Timesheet Id')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    project_category_id = fields.Many2one('kw_project_category_master',string="Project Category")
    project_id = fields.Many2one('project.project',string="Project")
    task_id = fields.Many2one('project.task',string="Task")
    description = fields.Char(string="Description")
    task_status = fields.Selection([('inprogress','In-Progress'),('completed','Completed')],string="Task Status")
    unit_amount = fields.Float(string="Timesheet fill (Hours)")
    hide_tagged_to = fields.Boolean(string='Hide tagged To')
    validated = fields.Boolean(string='Validated')
    work_hours=fields.Float("Attendance Hours", compute='get_employee_work_hour')

    @api.depends('employee_id','t_date')
    def get_employee_work_hour(self):
        for rec in self:
            emp_work_hr = self.env['kw_daily_employee_attendance'].sudo().search(
                [('attendance_recorded_date', '=', rec.t_date),
                ('employee_id', '=', rec.employee_id.id)],limit=1)
            rec.work_hours = emp_work_hr.worked_hours

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
        SELECT  row_number() over(order by al.date desc, al.id desc,al.employee_id) AS id,
        al.id AS timesheet_id,
        al.date AS t_date,
		al.employee_id AS employee_id,
		al.prject_category_id AS project_category_id,
		al.project_id AS project_id,
		al.task_id AS task_id,
		al.name AS description,
		al.task_status AS task_status,
        al.hide_tagged_to AS hide_tagged_to,
        al.validated AS validated,
		al.unit_amount AS unit_amount
	    FROM account_analytic_line al
        where al.active=true and al.validated=false
            )""" )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)
        # user_is_timesheet_manager = self.env.user.has_group('hr_timesheet.group_timesheet_manager')
        # if self._context.get('filter_project_timesheet'):
        #     employee_projects = self.env['project.project'].search([('emp_id','=',current_employee.id)])
        #     args += [('project_id', '!=', False),('project_id','in',employee_projects.ids)]

        if self._context.get('filter_ra_pm_reviewer_timesheet'):
            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id and pj.reviewer_id = {current_employee.id}::integer
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_reviewer_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_task pt on pt.id = ana.task_id
						join project_project pj on pj.id = ana.project_id
                        where pt.tl_employee_id = ana.employee_id and pt.task_status != 'completed'
						and pj.emp_id = {current_employee.id}::integer
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.reviewer_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            project_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id'''

            self._cr.execute(query)
            query_result = self._cr.fetchall()
            no_reviewer_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            # if not user_is_timesheet_manager:
            args += ['&', '&',('employee_id', '!=', current_employee.id), ('validated', '!=', True),
                     '|', '|', '|',
                         '&', '&', '&', '&', ('task_id.tl_employee_id', '=', current_employee.id),
                         ('project_category_id', '=', project_work.id),
                         '|', '|', ('employee_id.emp_category.code', '!=', 'TTL'),
                              ('employee_id.emp_category.code', '=', None), ('employee_id.emp_category', '=', False),
                         ('timesheet_id', 'not in', no_reviewer_ra_timesheet_ids),
                         ('timesheet_id', 'not in', project_ra_timesheet_ids),

                         '&', ('project_id.emp_id', '=', current_employee.id),
                         '|', '|', ('timesheet_id', 'in', pm_timesheet_ids), ('task_id.tl_employee_id', '=', False),
                         ('employee_id.emp_category.code', '=', 'TTL'),

                         '&', ('employee_id.parent_id', '=', current_employee.id),
                         '|', '|', ('project_category_id', '!=', project_work.id),
                              '&', ('project_category_id', '=', project_work.id), ('timesheet_id', 'in', project_ra_timesheet_ids),
                              '&', '&', ('project_category_id', '=', project_work.id), ('project_id.reviewer_id', '=', False),
                                   ('timesheet_id', 'in', no_reviewer_ra_timesheet_ids),


                         ('timesheet_id', 'in', pm_reviewer_timesheet_ids)]

        return super(ToValidateTimesheets, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.multi
    def action_validate_timesheet(self):
        return {'type': 'ir.actions.act_window',
                'name': 'Validate Timesheet',
                'res_model': 'kw_timesheets_validate_wizard',
                'view_mode': 'form',
                'target':'new',
                }

    