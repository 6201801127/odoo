from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime


class BudgetRevertWizard(models.TransientModel):

    _name="budget.revert"
    _description = "Budget Revert"


    def dynamic_selection_values(self):
        select = []
        if self.env.context.get('capital_budget'):
            capital_budget_id = self.env['revised_budget_wizard'].browse(self.env.context.get('active_id'))
            print(capital_budget_id, 'capital_budget_idcapital_budget_id')
            if capital_budget_id:
                print('IIIIIIIII')
                if capital_budget_id.pending_at == 'Approver':
                    select = [('L1', 'L1'), ('L2', 'L2'), ('Finance', 'Finance'), ('cfo', 'Finance(CFO)')]
                if capital_budget_id.pending_at == 'cfo':
                    select = [('L1', 'L1'), ('L2', 'L2'), ('Finance', 'Finance')]
                if capital_budget_id.pending_at == 'Finance':
                    select = [('L1', 'L1'), ('L2', 'L2')]
                if capital_budget_id.pending_at == 'L2':
                    select = [('L1', 'L1')]
        if self.env.context.get('treasury_budget'):
            treasury_budget_id = self.env['revised_revenue_budget_wizard'].browse(self.env.context.get('active_id'))
            print(treasury_budget_id, 'treasury_budget_id')
            if treasury_budget_id:
                print('IIIIIIIII')
                if treasury_budget_id.pending_at == 'Approver':
                    select = [('L1', 'L1'), ('L2', 'L2'), ('Finance', 'Finance'), ('cfo', 'Finance(CFO)')]
                if treasury_budget_id.pending_at == 'cfo':
                    select = [('L1', 'L1'), ('L2', 'L2'), ('Finance', 'Finance')]
                if treasury_budget_id.pending_at == 'Finance':
                    select = [('L1', 'L1'), ('L2', 'L2')]
                if treasury_budget_id.pending_at == 'L2':
                    select = [('L1', 'L1')]
        if self.env.context.get('project_budget'):
            project_budget_id = self.env['revised_sbu_project_budget_wizard'].browse(self.env.context.get('active_id'))
            print(project_budget_id, 'project_budget_id')
            if project_budget_id:
                print('IIIIIIIII')
                if project_budget_id.pending_at == 'Approver':
                    select = [('L1', 'L1'), ('L2', 'L2'), ('Finance', 'Finance'), ('cfo', 'Finance(CFO)')]
                if project_budget_id.pending_at == 'cfo':
                    select = [('L1', 'L1'), ('L2', 'L2'), ('Finance', 'Finance')]
                if project_budget_id.pending_at == 'Finance':
                    select = [('L1', 'L1'), ('L2', 'L2')]
                if project_budget_id.pending_at == 'L2':
                    select = [('L1', 'L1')]
        print(select, 'SSSSSS')
        return select

    revert_to = fields.Selection(selection=lambda self: self.dynamic_selection_values())
    # capital_budget_id = fields.Many2one('revised_budget_wizard', 'Capital Budget', default=lambda self: self.env['revised_budget_wizard'].browse(self.env.context.get('active_ids')))


    def action_confirm(self):
        if self.env.context.get('capital_budget'):
            capital_budget_id = self.env['revised_budget_wizard'].browse(self.env.context.get('active_ids'))
            if self.revert_to:
                capital_budget_id.pending_at = self.revert_to
        if self.env.context.get('treasury_budget'):
            treasury_budget_id = self.env['revised_revenue_budget_wizard'].browse(self.env.context.get('active_id'))
            if self.revert_to:
                treasury_budget_id.pending_at = self.revert_to
        if self.env.context.get('project_budget'):
            project_budget_id = self.env['revised_sbu_project_budget_wizard'].browse(self.env.context.get('active_id'))
            if self.revert_to:
                project_budget_id.pending_at = self.revert_to


class BudgetRevertWizardMain(models.TransientModel):

    _name="budget.revert.main"
    _description = "Budget Revert"


    def dynamic_selection_values(self):
        select = []
        if self.env.context.get('capital_budget'):
            capital_budget_id = self.env['kw_capital_budget'].browse(self.env.context.get('active_id'))
            if capital_budget_id:
                if capital_budget_id.state == 'confirm':
                    select = [('draft', 'L1'), ('to_approve', 'L2'), ('approved', 'Finance'), ('cfo', 'Finance(CFO)')]
                if capital_budget_id.state == 'cfo':
                    select = [('draft', 'L1'), ('to_approve', 'L2'), ('approved', 'Finance')]
                if capital_budget_id.state == 'approved':
                    select = [('draft', 'L1'), ('to_approve', 'L2')]
                if capital_budget_id.state == 'to_approve':
                    select = [('draft', 'L1')]
        if self.env.context.get('treasury_budget'):
            treasury_budget_id = self.env['kw_revenue_budget'].browse(self.env.context.get('active_id'))
            print(treasury_budget_id, 'treasury_budget_id')
            if treasury_budget_id:
                if treasury_budget_id.state == 'confirm':
                    select = [('draft', 'L1'), ('to_approve', 'L2'), ('approved', 'Finance'), ('cfo', 'Finance(CFO)')]
                if treasury_budget_id.state == 'cfo':
                    select = [('draft', 'L1'), ('to_approve', 'L2'), ('approved', 'Finance')]
                if treasury_budget_id.state == 'approved':
                    select = [('draft', 'L1'), ('to_approve', 'L2')]
                if treasury_budget_id.state == 'to_approve':
                    select = [('draft', 'L1')]
        if self.env.context.get('project_budget'):
            project_budget_id = self.env['kw_sbu_project_budget'].browse(self.env.context.get('active_id'))
            if project_budget_id:
                if project_budget_id.state == 'confirm':
                    select = [('draft', 'L1'), ('to_approve', 'L2'), ('approved', 'Finance'), ('cfo', 'Finance(CFO)')]
                if project_budget_id.state == 'cfo':
                    select = [('draft', 'L1'), ('to_approve', 'L2'), ('approved', 'Finance')]
                if project_budget_id.state == 'approved':
                    select = [('draft', 'L1'), ('to_approve', 'L2')]
                if project_budget_id.state == 'to_approve':
                    select = [('draft', 'L1')]
        return select

    revert_to = fields.Selection(selection=lambda self: self.dynamic_selection_values())
    # capital_budget_id = fields.Many2one('revised_budget_wizard', 'Capital Budget', default=lambda self: self.env['revised_budget_wizard'].browse(self.env.context.get('active_ids')))


    def action_confirm(self):
        if self.env.context.get('capital_budget'):
            capital_budget_id = self.env['capital_budget_id'].browse(self.env.context.get('active_ids'))
            if self.revert_to:
                if self.revert_to == 'draft':
                    approver_ids = capital_budget_id.budget_department.level_1_approver_capital.ids
                    capital_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
                    # treasury_budget_id.state = self.revert_to
                elif self.revert_to == 'to_approve':
                    approver_ids = capital_budget_id.budget_department.level_2_approver_capital.ids
                    capital_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
                    # treasury_budget_id.state = self.revert_to
                elif self.revert_to == 'approved':
                    finance_group = self.env.ref(
                        'kw_budget.group_finance_kw_budget')
                    finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                    approver_ids = finance_users.mapped('employee_ids.id')
                    capital_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
                elif self.revert_to == 'cfo':
                    finance_group = self.env.ref(
                        'kw_budget.group_cfo_kw_budget')
                    finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                    approver_ids = finance_users.mapped('employee_ids.id')
                    capital_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
        if self.env.context.get('treasury_budget'):
            treasury_budget_id = self.env['kw_revenue_budget'].browse(self.env.context.get('active_id'))
            if self.revert_to:
                if self.revert_to == 'draft':
                    approver_ids = treasury_budget_id.budget_department.level_1_approver.ids
                    treasury_budget_id.write({'state': self.revert_to,
                               'pending_at_ids': [(6, 0, approver_ids)]
                               })
                    # treasury_budget_id.state = self.revert_to
                elif self.revert_to == 'to_approve':
                    approver_ids = treasury_budget_id.budget_department.level_2_approver.ids
                    treasury_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
                    # treasury_budget_id.state = self.revert_to
                elif self.revert_to == 'approved':
                    finance_group = self.env.ref(
                        'kw_budget.group_finance_kw_budget')
                    finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                    approver_ids = finance_users.mapped('employee_ids.id')
                    treasury_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
                elif self.revert_to == 'cfo':
                    finance_group = self.env.ref(
                        'kw_budget.group_cfo_kw_budget')
                    finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                    approver_ids = finance_users.mapped('employee_ids.id')
                    treasury_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
        if self.env.context.get('project_budget'):
            project_budget_id = self.env['kw_sbu_project_budget'].browse(self.env.context.get('active_id'))
            if self.revert_to:
                if self.revert_to == 'draft':
                    approver_ids = project_budget_id.budget_department.level_1_approver.ids
                    project_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
                    # treasury_budget_id.state = self.revert_to
                elif self.revert_to == 'to_approve':
                    approver_ids = project_budget_id.budget_department.level_2_approver.ids
                    project_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
                    # treasury_budget_id.state = self.revert_to
                elif self.revert_to == 'approved':
                    finance_group = self.env.ref(
                        'kw_budget.group_finance_kw_budget')
                    finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                    approver_ids = finance_users.mapped('employee_ids.id')
                    project_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })
                elif self.revert_to == 'cfo':
                    finance_group = self.env.ref(
                        'kw_budget.group_cfo_kw_budget')
                    finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                    approver_ids = finance_users.mapped('employee_ids.id')
                    project_budget_id.write({'state': self.revert_to,
                                              'pending_at_ids': [(6, 0, approver_ids)]
                                              })



class DepartmnetMappingStart(models.TransientModel):

    _name="budget.department.mapping"
    _description = "Budget Department Mapping Start"

    @api.model
    def default_get(self, fields):
        res = super(DepartmnetMappingStart, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        dep_ids = self.env['kw_budget_dept_mapping'].sudo().search([('id', 'in', active_ids), ('state', '=', 'draft'), ('fiscal_year', '=', current_fiscal.id)]).ids
        res.update({
            'department_ids': dep_ids,
        })
        return res

    department_ids = fields.Many2many('kw_budget_dept_mapping', 'kw_budget_dept_mapping_rel', string='Departments')


    def group_update(self):
        rev_lis = []
        cap_lis = []
        dataa = []
        l2_rev = []
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        data = self.env['kw_budget_dept_mapping'].search([('state', '=', 'approve'), ('fiscal_year', '=', current_fiscal.id)])
        for rec in data:
            if rec.revenue_boolean:
                for employee_id in rec.level_1_approver:
                    rev_lis.append(employee_id.user_id.id)
                for emp in rec.level_2_approver:
                    dataa.append(emp.user_id.id)
                    rev_lis.append(emp.user_id.id)
                    l2_rev.append(emp.user_id.id)
                # group_l2_kw_budget
            if rec.capital_boolean:
                for employee_id in rec.level_1_approver_capital:
                    cap_lis.append(employee_id.user_id.id)
                for emp in rec.level_2_approver_capital:
                    dataa.append(emp.user_id.id)
                    cap_lis.append(emp.user_id.id)
        final_data = dataa + cap_lis + rev_lis
        group_department_head_kw_budget = self.env.ref('kw_budget.group_department_head_kw_budget').sudo()
        group_department_head_kw_budget.write({'users': [(6, 0, final_data)]})
        group_group_l2_kw_budget = self.env.ref('kw_budget.group_l2_kw_budget').sudo()
        group_group_l2_kw_budget.write({'users': [(6, 0, l2_rev)]})

        group_capital = self.env.ref('kw_budget.group_capital_budget_user_kw_budget').sudo()
        group_capital.write({'users': [(6, 0, cap_lis)]})

        group_capital = self.env.ref('kw_budget.group_revenue_budget_user_kw_budget').sudo()
        group_capital.write({'users': [(6, 0, rev_lis)]})


    def update_group_users(self, bud_obj):
        rev_lis = []
        cap_lis = []
        dataa = []
        l2_rev = []
        for rec in bud_obj:
            if rec.revenue_boolean:
                for employee_id in rec.level_1_approver:
                    rev_lis.append(employee_id.user_id.id)
                for emp in rec.level_2_approver:
                    dataa.append(emp.user_id.id)
                    rev_lis.append(emp.user_id.id)
                    l2_rev.append(emp.user_id.id)
                # group_l2_kw_budget
            if rec.capital_boolean:
                for employee_id in rec.level_1_approver_capital:
                    cap_lis.append(employee_id.user_id.id)
                for emp in rec.level_2_approver_capital:
                    dataa.append(emp.user_id.id)
                    cap_lis.append(emp.user_id.id)
        final_data = dataa + cap_lis + rev_lis
        group_department_head_kw_budget = self.env.ref('kw_budget.group_department_head_kw_budget').sudo()
        group_department_head_kw_budget.write({'users': [(6, 0, final_data)]})
        group_group_l2_kw_budget = self.env.ref('kw_budget.group_l2_kw_budget').sudo()
        group_group_l2_kw_budget.write({'users': [(6, 0, l2_rev)]})

        group_capital = self.env.ref('kw_budget.group_capital_budget_user_kw_budget').sudo()
        group_capital.write({'users': [(6, 0, cap_lis)]})

        group_capital = self.env.ref('kw_budget.group_revenue_budget_user_kw_budget').sudo()
        group_capital.write({'users': [(6, 0, rev_lis)]})

    def create_update_sbu_budget_maping(self, sbu_obj):
        if sbu_obj:
            sbu_obj_find = self.env['kw_sbu_project_mapping'].sudo()
            sbu_obj_find_result = sbu_obj_find.search([('sbu_id', '=', sbu_obj.sbu_id.id), ('fiscal_year_id', '=', sbu_obj.fiscal_year.id)])
            if not sbu_obj_find_result:
                data_dict = {
                    'sbu_id': sbu_obj.sbu_id.id,
                    'fiscal_year_id': sbu_obj.fiscal_year.id,
                    'level_1_approver': [(4, approver_id) for approver_id in sbu_obj.level_1_approver_sbu.ids],
                    'level_2_approver': [(4, approver_id) for approver_id in sbu_obj.level_2_approver_sbu.ids]
                }
                pro_obj = sbu_obj_find.create(data_dict)
                pro_obj._update_project_group_users()


    def action_confirm(self):
        self.group_update()
        if self.department_ids:
            for rec in self.department_ids:
                if rec.budget_type == 'Treasury/Capital':
                    self.update_group_users(rec)
                    rec.state = 'approve'
                if rec.budget_type == 'SBU-Project':
                    pro_map = self.create_update_sbu_budget_maping(rec)

                    rec.state = 'approve'




