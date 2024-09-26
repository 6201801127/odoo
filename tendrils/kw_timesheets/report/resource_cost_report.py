from odoo import tools
from odoo import models, fields, api
from datetime import datetime , date
from odoo.exceptions import ValidationError


class ResourceCostReport(models.Model):
    _name           = "kw_resource_costs_report"
    _description    = "Timesheet Resource cost Report"
    _auto = False
   
    project_id     = fields.Many2one('project.project', string="Project")
    timesheet_sbu_hour = fields.Float(string="Resource Hours",compute="compute_get_timesheet_sbu_cost_hours")
    timesheet_sbu_cost = fields.Float(string="Resource Cost",compute="compute_get_timesheet_sbu_cost_hours")
    timesheet_horizontal_hour = fields.Float(string="Horizontal Hours",compute="compute_get_timesheet_horizontal_cost_hours")
    timesheet_horizontal_cost = fields.Float(string="Horizontal Cost",compute="compute_get_timesheet_horizontal_cost_hours")
    sbu_id = fields.Many2one('kw_sbu_master', string='SBU Name')
    project_code = fields.Char(related='project_id.crm_id.code', string='Project Code')
    pm_id = fields.Many2one('hr.employee', string="Project Manager")
    reviewer_id = fields.Many2one('hr.employee', string="Reviewer")
    project_sbu_id = fields.Many2one('hr.employee', string='Project SBU')

    @api.multi
    @api.depends('project_id')
    def compute_get_timesheet_sbu_cost_hours(self):
        for project in self:
            domain = []
            active_members = self.env['kw_project_resource_tagging'].sudo().search([('project_id','=',project.project_id.id),('emp_id.sbu_type','=','sbu')])
            if 'from_date' in self._context or 'to_date' in self._context:
                from_date = datetime.strptime(self._context.get('from_date'),'%Y-%m-%d').date()
                to_date = datetime.strptime(self._context.get('to_date'),'%Y-%m-%d').date()
                domain = [('project_id','=',project.project_id.id),('employee_id','in',active_members.mapped('emp_id').ids),('date', '>=', from_date),('date', '<=', to_date)]
            else:
                domain = [('project_id','=',project.project_id.id),('employee_id','in',active_members.mapped('emp_id').ids)]
            timesheet_hours = self.env['account.analytic.line'].sudo().search(domain)
            # print(timesheet_hours)
            total_hours = sum(timesheet_hours.mapped('unit_amount'))
            project.timesheet_sbu_hour = total_hours
            cost_variable = 0.00
            for emp in active_members:
                if 'from_date' in self._context or 'to_date' in self._context:
                    from_date = datetime.strptime(self._context.get('from_date'), '%Y-%m-%d').date()
                    to_date = datetime.strptime(self._context.get('to_date'), '%Y-%m-%d').date()
                    domain = [('project_id','=',project.project_id.id),('employee_id','=',emp.emp_id.id), ('date', '>=', from_date),('date', '<=', to_date)]
                else:
                    domain = [('project_id','=',project.project_id.id),('employee_id','=',emp.emp_id.id)]
                timesheet_rec = self.env['account.analytic.line'].sudo().search(domain).mapped('unit_amount')
                if timesheet_rec:
                    cost_variable += sum(timesheet_rec) * emp.emp_id.timesheet_cost
                else:
                    cost_variable += 0
            project.timesheet_sbu_cost = cost_variable



    @api.multi
    @api.depends('project_id')
    def compute_get_timesheet_horizontal_cost_hours(self):
        for project in self:
            domain = []
            active_members = self.env['kw_project_resource_tagging'].sudo().search(
                [('project_id', '=', project.project_id.id),('emp_id.sbu_type', '=', 'horizontal')])
            if 'from_date' in self._context or 'to_date' in self._context:
                from_date = datetime.strptime(self._context.get('from_date'), '%Y-%m-%d').date()
                to_date = datetime.strptime(self._context.get('to_date'), '%Y-%m-%d').date()
                domain = [('project_id', '=', project.project_id.id),
                          ('employee_id', 'in', active_members.mapped('emp_id').ids), ('date', '>=', from_date),
                          ('date', '<=', to_date)]
            else:
                domain = [('project_id', '=', project.project_id.id),
                          ('employee_id', 'in', active_members.mapped('emp_id').ids)]
            timesheet_hours = self.env['account.analytic.line'].sudo().search(domain)
            # print(timesheet_hours)
            total_hours = sum(timesheet_hours.mapped('unit_amount'))
            project.timesheet_horizontal_hour = total_hours
            cost_variable = 0.00
            for emp in active_members:
                if 'from_date' in self._context or 'to_date' in self._context:
                    from_date = datetime.strptime(self._context.get('from_date'), '%Y-%m-%d').date()
                    to_date = datetime.strptime(self._context.get('to_date'), '%Y-%m-%d').date()
                    domain = [('project_id', '=', project.project_id.id), ('employee_id', '=', emp.emp_id.id),
                              ('date', '>=', from_date), ('date', '<=', to_date)]
                else:
                    domain = [('project_id', '=', project.project_id.id), ('employee_id', '=', emp.emp_id.id)]
                timesheet_rec = self.env['account.analytic.line'].sudo().search(domain).mapped('unit_amount')
                if timesheet_rec:
                    cost_variable += sum(timesheet_rec) * emp.emp_id.timesheet_cost
                else:
                    cost_variable += 0
            project.timesheet_horizontal_cost = cost_variable

    @api.model_cr
    def init(self):
        # print('===================================>>>>>>>>>>>>>>>>>>>>>>', dict(self._context))
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as 
        (
             select row_number() over(ORDER BY p.id) as id, p.id as project_id,(select representative_id from kw_sbu_master where id = p.sbu_id) as project_sbu_id,p.sbu_id as sbu_id, 
             p.crm_id as crm_id,p.emp_id as pm_id, p.reviewer_id as reviewer_id from project_project p where p.active=True
        )""" % (self._table))


class ResourceCostReportWizard(models.TransientModel):
    _name = 'resource_cose_report_wizard'
    _description = "resource Cose Filter Report Wizard"

    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)

    @api.constrains('from_date', 'to_date')
    def validate_date(self):
        for record in self:
            if record.from_date and record.to_date:
                if record.from_date > record.to_date:
                    raise ValidationError(
                        f'Start date should not greater than End date : {record.from_date} > {record.to_date}.')
                if record.to_date > date.today():
                    raise ValidationError("You are not allowed to add for future date.")

    def get_resource_cost_filter(self):
        # data_ids = self.env['kw_resource_costs_report'].sudo().search(['|',('project_sbu_id.user_id', '=', self.env.user.id),('reviewer_id.user_id', '=', self.env.user.id)])
        # data_ids = self.env['kw_resource_costs_report'].sudo().search([('project_sbu_id.user_id', '=', self.env.user.id),('sbu_id','=',self.env.user.employee_ids.sbu_master_id.id)])
        # data_ids = self.env['kw_resource_costs_report'].sudo().search([('reviewer_id.user_id', '=', self.env.user.id)])

        # print("data_ids-----,",data_ids)
        # domain = []
        # if self.env.user.employee_ids.sbu_master_id.representative_id.user_id.id == self.env.user.id:
        #     domain = [('project_sbu_id.user_id', '=', self.env.user.id)]
        # if self.env.user.employee_ids.sbu_master_id.employee_id.user_id.id == self.env.user.id:
        #     domain = [('reviewer_id.user_id', '=', self.env.user.id)]
        action = {
            'name': 'Resourse Cost Report',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'kw_resource_costs_report',
            'context': {'from_date': self.from_date, 'to_date': self.to_date},
            'target': 'self',
            'domain':[]
            # 'domain':[('id','in',data_ids.ids)],
            # 'domain':domain,
        }
        # print("action==========",action)
        return action
