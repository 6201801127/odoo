# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools


class SBUMasterIn(models.Model):
    _inherit = 'kw_sbu_master'

    @api.model
    def create(self, vals):
        if 'representative_id' in vals and vals['representative_id']:
            sbu_representative_group = self.env.ref('kw_resource_management.group_sbu_representative', False)
            representative = self.env['hr.employee'].sudo().browse(vals['representative_id'])
            if representative:
                sbu_representative_group.sudo().write({'users': [(4, representative.user_id.id)]})
                self.env.user.notify_success("Users added to the Representative Group")

        res = super(SBUMasterIn, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee']
        if 'representative_id' in vals and vals['representative_id']:
            sbu_representative_group = self.env.ref('kw_resource_management.group_sbu_representative', False)
            representative = employee.sudo().browse(vals['representative_id'])
            remove_users_access = self.representative_id if representative != self.representative_id else False
            all_representatives = self.env['kw_sbu_master'].sudo().search([]).mapped(
                'representative_id') - remove_users_access if remove_users_access else ''
            if representative:
                sbu_representative_group.sudo().write({'users': [(4, representative.user_id.id)]})
                self.env.user.notify_success("Users added to the Representative Group")
            if remove_users_access and remove_users_access.id not in all_representatives.ids:
                sbu_representative_group.sudo().write({'users': [(3, remove_users_access.user_id.id)]})

        res = super(SBUMasterIn, self).write(vals)
        return res
