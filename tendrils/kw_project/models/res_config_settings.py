
from odoo import api, fields, models

class ResConfigSettingsProject(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    kw_project_service_url = fields.Char(
        string="Tendrils Project Service URL",
        help="Web service URL to get the Project information from Tendrils.",
        default='http://172.27.34.48/dev.service.portalV6.csmpl.com/OdooSynSVC.svc'
    )

    kw_project_service_days = fields.Char(
        string="Tendrils Project Sync Day Difference",
        help="Web service URL to get configure the day difference.",
        default=1
    )

    @api.model
    def get_values(self):
        res     = super(ResConfigSettingsProject, self).get_values()
        param   = self.env['ir.config_parameter'].sudo()

        res.update(
            kw_project_service_url = str(param.get_param('kw_proj.project_web_service_url')),
            kw_project_service_days= str(param.get_param('kw_proj.project_service_diff_days')),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettingsProject, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        param.set_param('kw_proj.project_web_service_url', self.kw_project_service_url)
        param.set_param('kw_proj.project_service_diff_days', self.kw_project_service_days)