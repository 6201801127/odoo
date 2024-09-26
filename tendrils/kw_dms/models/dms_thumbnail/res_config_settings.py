
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def documents_open_thumbnail_cron(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.cron',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'name': _("Automatic Thumbnail Creation"),
            'res_id': self.env.ref('kw_dms.cron_dms_file_thumbnails').id,
            'views': [(False, "form")],
            'context': self.env.context,
        }  
