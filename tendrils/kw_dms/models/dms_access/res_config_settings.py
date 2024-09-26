
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    documents_access_groups_user_view = fields.Boolean(
        string="Show Access Groups on User Form",
        help="Allows users to edit the access groups of a directory.")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env.ref('kw_dms.view_dms_access_directory_form').write({
            'active': self.documents_access_groups_user_view,
        })
        self.env.ref('kw_dms.view_dms_access_directory_manager_form').write({
            'active': not self.documents_access_groups_user_view,
        })
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        view = self.env.ref('kw_dms.view_dms_access_directory_form')
        res.update(documents_access_groups_user_view=bool(view.active))
        return res
