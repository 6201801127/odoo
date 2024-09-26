# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class resUsers(models.Model):
    _inherit = 'res.users'


    @api.model
    def default_get(self, field_list):
        result = super(resUsers, self).default_get(field_list)
        result['tz'] = 'Asia/Kolkata'
        return result

    @api.model
    def create(self, vals):
        res = super(resUsers, self).create(vals)
        res.tz = 'Asia/Kolkata'
        return res

    # FIXME: Will uncomment this post approval
    # @api.multi
    # def write(self, vals):
    #     res = super().write(vals)
    #     for rec in self:
    #         if rec.has_group('groups_inherit.group_employee_type_contractual_with_agency')\
    #                         or rec.has_group('groups_inherit.group_employee_type_contractual_with_stpi'):
    #             loan_officer, loan_manager = self.env.ref('ohrms_loan.group_loan_requester'),\
    #                                         self.env.ref('ohrms_loan.group_loan_approver')
    #             loan_officer.write({'users': [(3, rec.id)]})
    #             loan_manager.write({'users': [(3, rec.id)]})
    #     return res