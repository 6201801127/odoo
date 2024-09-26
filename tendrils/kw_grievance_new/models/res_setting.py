from odoo import fields, models, api
from ast import literal_eval


class ResSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mail_to_users = fields.Many2many("hr.employee", "mails_emp_rel", "ml_ids", "ems_id",string="Grievance and Whistleblowing Mail cc")


    @api.model
    def get_values(self):
        res = super(ResSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        mail_to_users = params.get_param('kw_grievance_new.mail_to_users') or "[]"
        lines = False
        if mail_to_users:
            lines = [(6, 0, literal_eval(mail_to_users))]
        res.update(mail_to_users=lines)
        return res

    @api.multi
    def set_values(self):
        res = super(ResSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_grievance_new.mail_to_users',self.mail_to_users.ids)
        return res