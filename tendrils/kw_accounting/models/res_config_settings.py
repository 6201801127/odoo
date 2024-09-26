from odoo import models, fields, api, _
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_csm_account_conf = fields.Boolean(string="Enable CSM Accounting Configuration")
    fd_mail_emp_ids = fields.Many2many('hr.employee', 'res_config_fd_employee_rel', 'employee_id', 'res_id', string='FD Notify')
    
    @api.multi
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.enable_csm_account_conf or False
        param.set_param('kw_accounting.fd_mail_emp_ids', self.fd_mail_emp_ids.ids)
        param.set_param('kw_accounting.enable_csm_account_conf_status', field1)

    @api.model
    def get_values(self):
        res = super().get_values()
        fd_mail_emp_ids = self.env['ir.config_parameter'].sudo().get_param('kw_accounting.fd_mail_emp_ids')
        lines = False
        
        if fd_mail_emp_ids:
            lines = [(6, 0, literal_eval(fd_mail_emp_ids))]
        res.update(
            enable_csm_account_conf=self.env['ir.config_parameter'].sudo().get_param('kw_accounting.enable_csm_account_conf_status'),
            fd_mail_emp_ids = lines,
            
        )
        return res