# -*- coding: utf-8 -*-
from odoo import models, fields, api


class kw_workorder(models.Model):
    _name = 'kw_workorder'
    _description = 'kw_workorder'

    crm_id = fields.Many2one('crm.lead', "Work Order")
    current_wo = fields.Boolean('Current WorkOrder')
    workorder_id = fields.Many2one('project.project', "Work Order")


class kw_project_inherit(models.Model):
    _inherit = 'project.project'

    @api.model
    def _get_domain(self):
        rcm_module_exist = self.env['ir.module.module'].sudo().search(
            [('name', '=', 'kw_resource_management')])
        if not rcm_module_exist or rcm_module_exist.state == 'installed':
            users = self.env.ref('kw_resource_management.group_sbu_reviewer').users
            return [('id', 'in', users.mapped('employee_ids').ids)]

    kw_id = fields.Integer("KW ID")
    code = fields.Char('Project Code')
    crm_id = fields.Many2one('crm.lead', "WO/Opportunity")
    emp_id = fields.Many2one(string='Project Manager', comodel_name='hr.employee', ondelete='restrict', required=True)
    user_id = fields.Many2one(related='emp_id.user_id', store=True)
    resource_id = fields.One2many(string='Members', comodel_name='kw_project_resource_tagging',
                                  inverse_name='project_id', domain=[("active", "=", True)])
    resource_inactive_id = fields.One2many(string='Old Members', comodel_name='kw_project_resource_tagging',
                                           inverse_name='project_id', domain=[("active", "=", False)])
    stage_id = fields.Char(related='crm_id.stage_id.name', string='Reference Type')
    create_date_crm = fields.Date(related='crm_id.date', string='Work Order Date')
    sales_person = fields.Char(related='crm_id.user_id.name', string='Account Manager')
    sbu_id = fields.Many2one('kw_sbu_master', string="SBU", compute="get_sbu_id", store=True)
    reviewer_id = fields.Many2one("hr.employee", "Reviewer",
                                  domain=_get_domain)  # added on 13 June 2022 (Gouranga Kala)
    reviewers_ids = fields.Many2many('hr.employee',
                                     'project_employee_rel',
                                     'project_id',
                                     'employee_id',
                                     'Reviewers',
                                     domain=_get_domain)

    workorder_ids = fields.One2many(string="Reference Name", comodel_name='kw_workorder',
                                    inverse_name='workorder_id')
    module_ids = fields.One2many("kw_project.module", "project_id", string="Modules")
    module_count = fields.Integer(compute='module_count_data')

    @api.model
    def get_cc_emails(self):
        users = self.env.ref('kw_project.project_group_cc_users').users
        values = ','.join(str(user_email.email) for user_email in users)
        return values

    @api.depends('emp_id')
    def get_sbu_id(self):
        for rec in self:
            data = self.env['hr.employee'].sudo().search([('id', '=', rec.emp_id.id)], limit=1)
            if data:
                rec.sbu_id = data.sbu_master_id

    # def _auto_init(self):
    #     super(kw_project_inherit, self)._auto_init()
    #     self.env.cr.execute(
    #         "update project_project p set sbu_id = emp.sbu_master_id from hr_employee emp where p.emp_id = emp.id")

    # def _auto_init(self):
    #     super(project.project, self)._auto_init()
    #     self.env.cr.execute("update project_project p set sbu_id = emp.sbu_master_id from hr_employee emp where p.emp_id = emp.id")

    # def account_analytic_line_action(self):   
    #     view_id = self.env.ref("analytic.view_account_analytic_line_tree").id
    #     action = {
    #         'name': 'Margin',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.analytic.line',
    #         'view_mode': 'tree',
    #         'view_type': 'form',
    #         'view_id': view_id,
    #         'target': 'self',
    #         'domain': [('account_id', '=', self.analytic_account_id.id)]
    #     }
    #     return action

    # def cost_account_analytic_line_action(self):
    #     view_id = self.env.ref("analytic.view_account_analytic_line_tree").id
    #     action = {
    #         'name': 'Costs',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.analytic.line',
    #         'view_mode': 'tree',
    #         'view_type': 'form',
    #         'view_id': view_id,
    #         'target': 'self',
    #         'domain': [('amount', '<', 0), ('account_id', '=',  self.analytic_account_id.id)] 
    #     }
    #     return action    

    @api.depends('name')
    def module_count_data(self):
        project = self.env['kw_project.module'].sudo()
        for record in self:
            data = project.search([('project_id', '=', record.id)])
            record.module_count = len(data)

    @api.multi
    def module_count_action(self):
        tree_view_id = self.env.ref("kw_project.module_tree").id
        form_view_id = self.env.ref("kw_project.module_view_form").id
        return {
            'name': 'Modules',
            'domain': [('project_id', '=', self.id)],
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_type': 'form',
            'res_model': 'kw_project.module',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
