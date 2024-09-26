from odoo import tools
from odoo import models, fields, api
from datetime import date,timedelta


class TimesheetProjectReport(models.Model):
    _name = "kw_timesheet_project_report_view"
    _description = "Timesheet Project Report View"
    _auto = False

    project_id = fields.Many2one("project.project",string="Project ID")
    project_name = fields.Char(string="Project Name")
    tagged_resource = fields.Integer(string="Tagged Resources")
    no_of_filled = fields.Integer(string="Filled")
    no_of_not_filled = fields.Integer(string="Not Filled")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    @api.model_cr
    def init(self):
        today = date.today()
        current_start_date = today - timedelta(days=today.weekday())
        current_week_end_date = current_start_date + timedelta(days=6)
        from_date = 'from_date' in self._context and self._context['from_date'] and self._context['from_date'] or current_start_date
        to_date = 'to_date' in self._context and self._context['to_date'] and self._context['to_date'] or current_week_end_date

        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                        select p.id as id,
                        p.id as project_id,
                        p.name as project_name,
                        --count(distinct prt.emp_id) + case when pj_emp.active = True then 1 else 0 end as tagged_resource,
                        count(distinct prt.emp_id) as tagged_resource,
                        --count(distinct ana.employee_id) + case when pj_emp.active = True then count(distinct pm_ana.employee_id) else 0 end as no_of_filled,
                        count(distinct ana.employee_id) as no_of_filled,
                        --(count(distinct prt.emp_id) + case when pj_emp.active = True then 1 else 0 end)
                        count(distinct prt.emp_id) -
                        --(count(distinct ana.employee_id) + case when pj_emp.active = True then count(distinct pm_ana.employee_id) else 0 end )
                        count(distinct ana.employee_id) as no_of_not_filled,
                                        '{from_date.strftime('%Y-%m-%d')}'::date as from_date,
                                        '{to_date.strftime('%Y-%m-%d')}'::date as to_date

                        from project_project p
                        join kw_project_resource_tagging prt on prt.project_id = p.id
                        join hr_employee rt_emp on prt.emp_id = rt_emp.id
                        left join account_analytic_line ana on ana.employee_id = prt.emp_id and ana.project_id = prt.project_id and ana.date >= '{from_date.strftime('%Y-%m-%d')}' and ana.date <= '{to_date.strftime('%Y-%m-%d')}'
                        --left join account_analytic_line pm_ana on pm_ana.employee_id = p.emp_id and pm_ana.project_id = p.id and pm_ana.date >= '{from_date.strftime('%Y-%m-%d')}' and pm_ana.date <= '{to_date.strftime('%Y-%m-%d')}'
                        --left join hr_employee pj_emp on p.emp_id = pj_emp.id
                        where p.active = True and prt.active = True and rt_emp.active = True
                        group by p.id,p.name
                        --,pj_emp.active
                        order by p.name asc
                )"""

        self.env.cr.execute(query)

    @api.multi
    def action_view_timesheet_details(self):
        tree_view_id = self.env.ref('hr_timesheet.hr_timesheet_line_tree').id
        pivot_view_id = self.env.ref('hr_timesheet.view_hr_timesheet_line_pivot').id
        grid_view_id = self.env.ref('timesheet_grid.timesheet_view_grid_by_employee_readonly').id

        project_resources = self.project_id.resource_id.mapped('emp_id').filtered(lambda r:r.active == True)
        # project_resources |= self.project_id.emp_id.filtered(lambda r:r.active == True)

        return {
            'name': 'View Timesheets',
            'view_type': 'form',
            'view_mode': 'grid,pivot,tree',
            # 'view_id': False,
            'res_model': 'account.analytic.line',
            'type': 'ir.actions.act_window',
            'target': 'self',
            'domain':[('project_id', '!=', False),('project_id','=',self.project_id.id),
                        ('date','>=',self.from_date),('date','<=',self.to_date),
                        ('employee_id','in',project_resources.ids)],

            'context': {'grid_anchor': self.from_date.strftime('%Y-%m-%d'),
                        'week_end_date':self.to_date.strftime('%Y-%m-%d'),
                        'grid_range': 'week',
                        'search_default_groupby_employee':1,
                        # 'search_default_filter_this_month':1,
                        'create':False,
                        'edit':False,
                        'delete':False,
                        'view_pm':True
                       },
            'views': [
            (tree_view_id, 'tree'),
            (pivot_view_id, 'pivot'),
            (grid_view_id, 'grid'),
            ],
        }

    @api.multi
    def action_view_not_filled_employees(self):
        project_resources = self.project_id.resource_id.mapped('emp_id').filtered(lambda r:r.active == True)
        # project_resources |= self.project_id.emp_id.filtered(lambda r:r.active == True)
        resources_filled = self.env['account.analytic.line'].search([('employee_id','in',project_resources.ids),
                                                                     ('project_id','=',self.project_id.id),
                                                                     ('date','<=',self.to_date),
                                                                     ('date','>=',self.from_date)
                                                                     ]).mapped('employee_id')
        resource_not_filled = project_resources - resources_filled
        
        return {
            'name': 'Not Filled Resources',
            'view_type': 'form',
            'view_mode': 'tree,form',
            # 'view_id': False,
            'res_model': 'hr.employee',
            'type': 'ir.actions.act_window',
            'target': 'self',
            'domain':[('id', 'in',resource_not_filled.ids)],
            'context': {
                        'create':False,
                        'edit':False,
                        'delete':False,
                       },
            'views': [(self.env.ref('hr.view_employee_tree').id, 'tree'),
                      (self.env.ref('hr.view_employee_form').id,'form')],
        }
