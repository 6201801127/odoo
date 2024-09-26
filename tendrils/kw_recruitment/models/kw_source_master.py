# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from kw_utility_tools import kw_validations


class UtmSource(models.Model):
    _inherit = 'utm.source'
    _description = 'UTM Source'

    code = fields.Char('Code')
    sequence = fields.Integer("Sequence", default=10,
                              help="Gives the sequence order of qualification.")
    active = fields.Boolean(string="Active", default=True)
    source_type = fields.Selection(string="Source Type", selection=[('all', 'All'), ('recruitment', 'Recruitment')])
    kw_id = fields.Integer(string="Tendrils ID")


class JobPortal(models.Model):
    _name = "kw.job.portal"
    _description = "Job Portal"

    name = fields.Char("Title", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer("Sequence", default=10,
                              help="Gives the sequence order of qualification.")

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw.job.portal'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")
                if record.code.lower() == data.code.lower():
                    raise ValidationError(f"The code {record.code} is already exists.")


class SocialMedia(models.Model):
    _name = "kw.social.media"
    _description = "Social Media"

    name = fields.Char("Title", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer("Sequence", default=10,
                              help="Gives the sequence order of qualification.")

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw.social.media'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")
                if record.code.lower() == data.code.lower():
                    raise ValidationError(f"The code {record.code} is already exists.")


class Partner(models.Model):
    _inherit = "res.partner"

    institute = fields.Boolean(string='Is an Institute',
                               help="Check this box if this contact is an institute.")
    consultancy = fields.Boolean(string='Is a Consultancy',
                                 help="Check this box if this contact is a consultancy.")
    service_partner = fields.Boolean(string='Is an Service Partner',
                                     help="Check this box if this contact is an service partner.")
    consultancy_type = fields.Selection(string='Type Of Consultancy',
                                        selection=[('consult', 'Consultancy'), ('rpo', 'RPO')])


class BusinessUnit(models.Model):
    _name = 'kw_business_unit'
    _description = 'Business Unit'

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer("Sequence", default=10,
                              help="Gives the sequence order of qualification.")
    department_id = fields.Many2one('hr.department', string='Department', domain=[('parent_id', '=', False)])

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_business_unit'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")
