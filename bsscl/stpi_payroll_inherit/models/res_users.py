# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class resUsers(models.Model):
    _inherit = 'res.users'


    
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.has_group('groups_inherit.group_employee_type_contractual_with_agency')\
                            or rec.has_group('groups_inherit.group_employee_type_contractual_with_stpi')\
                            or rec.has_group('groups_inherit.group_employee_type_regular'):
                payroll_officer, payroll_manager = self.env.ref('hr_payroll.group_hr_payroll_user'),\
                                                    self.env.ref('hr_payroll.group_hr_payroll_manager')
                payroll_officer.write({'users': [(3, rec.id)]})
                payroll_manager.write({'users': [(3, rec.id)]})
        return res