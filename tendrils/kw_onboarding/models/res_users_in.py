# -*- coding: utf-8 -*-

# from odoo import models, fields, api
# 
# 
# class res_users_in(models.Model):
#     _inherit = 'res.users'

# new_joinee_id = fields.Many2one('kwonboard_new_joinee')

# @api.model
# def multi_has_groups(self, groups_ext_ids):
#     # here groups_ext_ids is a list of groups(external_id may be)
#     if not groups_ext_ids:
#         return False
#         # print(self.groups_id)
#     for group in groups_ext_ids:
#         group_id = self.env.ref(group).id
#         for group_rec in self.groups_id:
#             if group_id == group_rec.id:
#                 # print('matched')
#                 return True
#     return False
