from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'


    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.has_group('groups_inherit.group_employee_type_contractual_with_agency')\
                            or rec.has_group('groups_inherit.group_employee_type_contractual_with_stpi'):
                pf_officer, pf_manager = self.env.ref('pf_withdrawl.group_pf_withdraw_user'),\
                                            self.env.ref('pf_withdrawl.group_pf_withdraw_approver')
                pf_officer.write({'users': [(3, rec.id)]})
                pf_manager.write({'users': [(3, rec.id)]})
        return res