from odoo import models, fields, api, _


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    set_default = fields.Boolean('Default?', tracking=True)


class ProjectDefault(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        rtn = super(ProjectDefault, self).create(vals)
        stage_obj = self.env['project.task.type']
        stage_ids = stage_obj.search([('set_default', '=', True)])

        project_ids = [x.id for x in rtn]
        for stage in stage_ids:
            stage.sudo().write({'project_ids': [(4, tuple(project_ids), 0)]})

        return rtn
