from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------
    # , config_parameter='kw_sync.emp_web_service_url'
    kw_sync_service_url = fields.Char(
        string="Tendrils Web Service URL",
        help="Web service URL to get the employee information from Kwantify.",
        default='http://172.27.34.48/dev.service.portalV6.csmpl.com/OdooSynSVC.svc/GetModifiedEmpData'
    )

    kw_sync_service_days = fields.Char(
        string="Tendrils Web Service Sync Day Difference",
        help="Web service URL to get configure the day difference.",
        default=1
    )

    kw_sync_error_log_mail = fields.Char(
        string="Tendrils Web Service Sync Error Log",
        help="E-mail to get send the sync error log.",
        default=1
    )
    home_action_id = fields.Many2one('ir.actions.actions', string='New Home Action',
                                     help='Select home action for new user through service')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()

        res.update(
            kw_sync_service_url=str(param.get_param('kw_sync.emp_web_service_url')),
            kw_sync_service_days=str(param.get_param('kw_sync.kw_sync_service_diff_days')),
            kw_sync_error_log_mail=str(param.get_param('kw_sync.kw_sync_error_log_mail_id')),
            home_action_id=int(param.get_param('kw_sync.home_action')),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        param.set_param('kw_sync.emp_web_service_url', self.kw_sync_service_url)
        param.set_param('kw_sync.kw_sync_service_diff_days', self.kw_sync_service_days)
        param.set_param('kw_sync.kw_sync_error_log_mail_id', self.kw_sync_error_log_mail)
        param.set_param('kw_sync.home_action', self.home_action_id.id or False)
