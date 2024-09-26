# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import api, fields, models
from odoo.exceptions import ValidationError, AccessError


class RecruitmentLocation(models.Model):
    _name = "kw_recruitment_location"
    _description = "Recruitment Location."

    name = fields.Char(string="Name", required=True, size=100)
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 required=True, default=lambda self: self.env.user.company_id)
    branch_id = fields.Many2one(string='Branch', comodel_name='res.partner', ondelete='restrict',
                                domain="[('parent_id', '=', company_id)]", required=False)
    kw_branch_id = fields.Many2one(string='Branch', comodel_name='kw_res_branch', ondelete='restrict',
                                   domain="[('company_id', '=', company_id)]", required=True)
    code = fields.Char("Code")
    active = fields.Boolean(string="Active", default=True)

    @api.constrains('name', 'branch_id')
    def validate_location(self):
        record = self.env['kw_recruitment_location'].search([]) - self
        for data in record:
            if data.branch_id and data.branch_id.id == self.branch_id.id and data.name and data.name.lower() == self.name.lower():
                raise ValidationError(f"The name '{self.name}' with branch '{self.branch_id.name}'  already exists.")

    @api.model
    def create(self, values):
        result = super(RecruitmentLocation, self).create(values)
        self.env.user.notify_success("Recruitment location created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(RecruitmentLocation, self).write(values)
        self.env.user.notify_success("Recruitment location(s) updated successfully.")
        return result

    @api.multi
    def unlink(self):
        result = super(RecruitmentLocation, self).unlink()
        self.env.user.notify_success("Recruitment location(s) deleted successfully.")
        return result

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_recruitment_location'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")
