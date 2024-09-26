import ast
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dms_training_material_folder = fields.Many2one('kw_dms.directory', ondelete='restrict',
                                                   string="Training Material Workspace",
                                                   help="Centralize files attached to policy documents")

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('kw_dms.training_material_folder',
                        self.dms_training_material_folder.id or False)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            dms_training_material_folder=int(
                params.get_param('kw_dms.training_material_folder')),

        )
        return res
