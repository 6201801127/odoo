from odoo import fields, models,api


class PasswordSecurityResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pass_expiry_time = fields.Char(string='Password Expiry Time')
    password_minimum = fields.Integer(
        related="company_id.password_minimum", readonly=False
    )
    password_history = fields.Integer(
        related="company_id.password_history", readonly=False
    )
    password_length = fields.Integer(
        related="company_id.password_length", readonly=False
    )
    password_lower = fields.Integer(
        related="company_id.password_lower", readonly=False
    )
    password_upper = fields.Integer(
        related="company_id.password_upper", readonly=False
    )
    password_numeric = fields.Integer(
        related="company_id.password_numeric", readonly=False
    )
    password_special = fields.Integer(
        related="company_id.password_special", readonly=False
    )
    password_estimate = fields.Integer(
        related="company_id.password_estimate", readonly=False
    )
    login_attempt = fields.Char(readonly=False)
    login_time = fields.Char(readonly=False)
    

    @api.multi
    def set_values(self):
        res = super(PasswordSecurityResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter']

        field1 = self.pass_expiry_time or False
        field2 =self.login_attempt or False
        field3=self.login_time or False
        param.set_param('password_security.pass_expiry_time', field1)
        param.set_param('base.login_cooldown_after', field2)
        param.set_param('base.login_cooldown_duration', field3)
        return res
        
        

    @api.model
    def get_values(self):
        res = super(PasswordSecurityResConfigSettings, self).get_values()
    
        res.update(
            pass_expiry_time = self.env['ir.config_parameter'].sudo().get_param('password_security.pass_expiry_time'),
            login_attempt = self.env['ir.config_parameter'].sudo().get_param('base.login_cooldown_after'),
            login_time = self.env['ir.config_parameter'].sudo().get_param('base.login_cooldown_duration'),
            
        )
        return res
     
