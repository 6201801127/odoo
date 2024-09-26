from odoo import models, fields, api
from odoo.exceptions import ValidationError
import bs4 as bs


class hr_job_role(models.Model):
    _name = "hr.job.role"
    _description = "Job Role"
    _order = 'name asc'

    name = fields.Char(string='Name', size=100, required=True)
    designations = fields.Many2many('hr.job', 'hr_job_role_rel', 'role_id', 'job_id', string='Associated Designations',
                                    required=True)
    description = fields.Html(string="Description")

    @api.constrains('description', 'designations')
    def check_description(self):
        for record in self:
            if len((bs.BeautifulSoup(record.description, features="lxml")).text.strip()) == 0:
                raise ValidationError('Description cannot be empty')
        if self.env['hr.job.role'].search(
                [('designations', 'in', self.designations.ids)]) - self:
            raise ValidationError("The Designation Already Exist.")





class hr_job_autonomy(models.Model):
    _name = "hr_job_autonomy"
    _description = "Job Role"
    _order = 'name asc'

    name = fields.Char(string='Name', size=100, required=True)
    designations = fields.Many2many('hr.job', 'hr_job_roles_rel', 'role_id', 'job_id', string='Associated Designations',
                                    required=True)
    description = fields.Html(string="Description")

    @api.constrains('description', 'designations')
    def check_description(self):
        for record in self:
            if len((bs.BeautifulSoup(record.description, features="lxml")).text.strip()) == 0:
                raise ValidationError('Description cannot be empty')
        if self.env['hr_job_autonomy'].search(
                [('designations', 'in', self.designations.ids)]) - self:
            raise ValidationError("The Designation Already Exist.")
