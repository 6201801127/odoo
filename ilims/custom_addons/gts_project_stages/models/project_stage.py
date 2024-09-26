from odoo import api, fields, models, _


class ProjectStage(models.Model):
    _name = 'project.stage'

    name = fields.Char('Stage Name', track_visibility='always')
    fold = fields.Boolean('Folded in Kanban', track_visibility='always')
    user_id = fields.Many2one('res.users', string='Sales Team', track_visibility='always', ondelete='set null',
                              help='Specific user that uses this stage. Other users will not be able to see or use this stage.')
