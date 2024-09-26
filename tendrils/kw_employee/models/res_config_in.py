# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    emp_creation_inform_ids = fields.Many2many('hr.job', 'employee_creation_inform_mail_rel', string='Designation')
    hrd_mail = fields.Char('HRD Mail')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        emp_creation_inform_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.emp_creation_inform_ids')
        hrd_mail = self.env['ir.config_parameter'].sudo().get_param('hrd_mail')
        lines = False
        if emp_creation_inform_ids:
            lines = [(6, 0, literal_eval(emp_creation_inform_ids))]
        res.update({'emp_creation_inform_ids': lines, 'hrd_mail': hrd_mail})
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('kw_employee.emp_creation_inform_ids', self.emp_creation_inform_ids.ids)
        param.set_param('hrd_mail', self.hrd_mail)