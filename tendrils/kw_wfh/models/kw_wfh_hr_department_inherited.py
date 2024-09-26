# -*- coding: utf-8 -*-
from odoo import models, api


class kw_wfh_hr_department_inherited(models.Model):
    _inherit = 'hr.department'

    @api.multi
    def write(self, vals):
        """ for reporting authority/manager add to hr HOD group"""
        group_hod = self.env.ref('kw_wfh.group_hr_hod', False)
        old_manager_ids = []
        if 'manager_id' in vals:
            old_manager_ids = self.mapped('manager_id')

        res = super(kw_wfh_hr_department_inherited, self).write(vals)

        """# for reporting authority/manager add to hr HOD group"""
        for old_manager in old_manager_ids:
            if old_manager.user_id:
                group_hod.write({'users': [(3, old_manager.user_id.id)]})

        for emp_rec in self:
            if emp_rec.manager_id and emp_rec.manager_id.user_id:
                group_hod.write({'users': [(4, emp_rec.manager_id.user_id.id)]})
        return res
