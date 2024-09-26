from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BudgetDepartmentMapping(models.Model):
    _name = 'kw_budget_group_mapping'
    _rec_name = 'group_name'

    group_name = fields.Selection([
        ('capital', 'Capital'),
        ('revenue', 'Revenue'),
        ('sbu', 'SBU')
    ], 'Group Name', track_visibility='always')
    user_ids = fields.Many2many('hr.employee','employee_group_rel','employee_id','group_id',string="Users", track_visibility='always')


    def update_group(self):
        user_ids = self.user_ids.mapped('user_id').ids
        group_map = {
            'capital': 'kw_budget.group_capital_budget_user_kw_budget',
            'revenue': 'kw_budget.group_revenue_budget_user_kw_budget',
            'sbu': 'kw_budget.group_sbu_budget_user_kw_budget'
        }
        
        if self.group_name in group_map:
            self.env.ref(group_map[self.group_name]).sudo().write({
                'users': [(6, 0, user_ids)]
            })
            
        existing_users = self.env.ref('kw_budget.group_department_head_kw_budget').sudo().users
        all_user_ids = list(set(existing_users.ids + user_ids))
        self.env.ref('kw_budget.group_department_head_kw_budget').sudo().write({
            'users': [(6, 0, all_user_ids)]
        })
    
    # def update_group(self):
    #     user_ids = self.user_ids.mapped('user_id').ids
    #     if self.group_name == 'capital':
    #         self.env.ref('kw_budget.group_capital_budget_user_kw_budget').sudo().write({
    #             'users': [(6, 0, user_ids)]
    #         })
    #         existing_users = self.env.ref('kw_budget.group_department_head_kw_budget').sudo().users
    #         all_user_ids = list(set(existing_users.ids + user_ids))
    #         self.env.ref('kw_budget.group_department_head_kw_budget').sudo().write({
    #             'users': [(6, 0, all_user_ids)]
    #         })
    #     elif self.group_name == 'revenue':
    #         self.env.ref('kw_budget.group_revenue_budget_user_kw_budget').sudo().write({
    #             'users': [(6, 0, user_ids)]
    #         })
    #         existing_users = self.env.ref('kw_budget.group_department_head_kw_budget').sudo().users
    #         all_user_ids = list(set(existing_users.ids + user_ids))
    #         self.env.ref('kw_budget.group_department_head_kw_budget').sudo().write({
    #             'users': [(6, 0, all_user_ids)]
    #         })
    #     elif self.group_name == 'sbu':
    #         self.env.ref('kw_budget.group_sbu_budget_user_kw_budget').sudo().write({
    #             'users': [(6, 0, user_ids)]
    #         }) 
    #         existing_users = self.env.ref('kw_budget.group_department_head_kw_budget').sudo().users
    #         all_user_ids = list(set(existing_users.ids + user_ids))
    #         self.env.ref('kw_budget.group_department_head_kw_budget').sudo().write({
    #             'users': [(6, 0, all_user_ids)]
    #         })



        #    existing_users = self.env.ref('kw_budget.group_department_head_kw_budget').sudo().users.ids
        # all_user_ids = list(set(existing_users + user_ids))
        # self.env.ref('kw_budget.group_department_head_kw_budget').sudo().write({
        #                 'users': [(4 if user_id in existing_users else 6, user_id, 0) for user_id in all_user_ids]