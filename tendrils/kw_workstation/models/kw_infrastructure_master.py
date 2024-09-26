from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kw_infrastructure_master(models.Model):
    _name = 'kw_workstation_infrastructure'
    _description = "A master model to create the Infrastructure master"
    _order = "sequence"

    code = fields.Char(string="Code", required=True, size=100)
    name = fields.Char(string="Name", required=True, size=100)
    # address_id = fields.Many2one('res.partner', string='Location')
    address_id = fields.Many2one('kw_res_branch', string="Branch/SBU", required=True)
    sequence = fields.Integer(string="Sequence")
    active = fields.Boolean('Active', default=True)
    branch_unit_id = fields.Many2one('kw_res_branch_unit', string='Unit', required=True)

    @api.model
    def create(self, vals):
        new_record = super(kw_infrastructure_master, self).create(vals)
        self.env.user.notify_success(message='Infrastructure created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_infrastructure_master, self).write(vals)
        self.env.user.notify_success(message='Infrastructure updated successfully.')
        return res

    @api.constrains('address_id','code','name')
    def check_constraints(self):
        for rec in self:
            record = self.env['kw_workstation_infrastructure'].sudo().search([('address_id','=',rec.address_id.id),('name','=',rec.name)])-self
            if record:
                raise ValidationError("Record already exists!")