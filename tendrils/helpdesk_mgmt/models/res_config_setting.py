"""
Module for Res Config Settings.

This module contains the definition of the transient model for configuring settings in Odoo.

"""
from odoo import fields, models, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    """
    Transient Model for Res Config Settings.

    This class extends 'res.config.settings' to provide additional settings for configuring
    various options in Odoo.

    Attributes:
        _inherit (str): The name of the model being inherited ('res.config.settings').
    """
    _inherit = 'res.config.settings'

    mail_to_user = fields.Many2many("hr.employee", "mail_empl_rel", "mail_id", "emp_id",string="Mail To")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        mail_to_user = self.env['ir.config_parameter'].sudo().get_param('helpdesk_mgmt.mail_to_user') or "[]"
        lines = False
        if mail_to_user:
            lines = [(6, 0, literal_eval(mail_to_user))]

        res.update(mail_to_user=lines)
        return res


    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('helpdesk_mgmt.mail_to_user',self.mail_to_user.ids) 
        return res
