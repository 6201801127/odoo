import ast
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dms_meeting_doc_folder = fields.Many2one('kw_dms.directory', ondelete='restrict',
                                             string="Meeting Doc Workspace",
                                             help="Centralize files attached to meeting")

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('kw_dms.meeting_doc_folder', self.dms_meeting_doc_folder.id or False)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(dms_meeting_doc_folder=int(params.get_param('kw_dms.meeting_doc_folder')),)
        return res
