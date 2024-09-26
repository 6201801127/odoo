from odoo import models, fields, api


class ProjectMaster(models.Model):
    _inherit = "project.project"

    # code = fields.Char(string='Project Code', )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = record.code + ' - ' + record.name
            result.append((record.id, record_name))
        return result
