from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'


    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.has_group('groups_inherit.group_employee_type_contractual_with_agency'):
                tds_officer, tds_manager = self.env.ref('tds.group_officer_hr_declaration'),\
                                            self.env.ref('tds.group_manager_hr_declaration')
                tds_officer.write({'users': [(3, rec.id)]})
                tds_manager.write({'users': [(3, rec.id)]})
        return res