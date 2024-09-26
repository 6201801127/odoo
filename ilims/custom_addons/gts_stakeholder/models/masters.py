from odoo import api, fields, models, _


class ProjectRole(models.Model):
    _name = 'project.role'

    name = fields.Char('Name', track_visibility='always')


class ProjectStakeholder(models.Model):
    _name = 'project.stakeholder'

    name = fields.Char('Name', track_visibility='always')


class ProjectCommunication(models.Model):
    _name = 'project.communication'

    name = fields.Char('Name', track_visibility='always')
