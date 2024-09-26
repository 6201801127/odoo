# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools


class SBUMaster(models.Model):
    _name = 'kw_sbu_master'
    _description = 'SBU Master'
    _rec_name = 'display_name'
    _order = 'sequence'

    @api.model
    def _get_domain(self):
        group_users = self.env.ref('kw_resource_management.group_sbu_representative').users
        return [('id', 'in', group_users.mapped('employee_ids').ids)]

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', string='Reviewer')
    representative_id = fields.Many2one('hr.employee', string='Representative')
    type = fields.Selection(string='Type', selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal')])
    description = fields.Char(string="Description")
    display_name = fields.Char(compute='compute_name')
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order of purpose.")
    kw_id = fields.Integer(string="Tendrils ID")

    @api.depends('employee_id', 'description')
    def compute_name(self):
        for rec in self:
            rec_name = rec.name
            if rec.representative_id:
                rec_name = rec_name + ' ( ' + rec.representative_id.display_name + ' )'
            elif rec.description and not rec.representative_id:
                rec_name = rec_name + ' ( ' + rec.description + ' )'
            rec.display_name = rec_name
