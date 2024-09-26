# -*- coding: utf-8 -*-

from odoo import api,fields, models
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_onboarding_mail_status = fields.Boolean(string="Send E-mail")
    module_onboarding_sms_status = fields.Boolean(string="Send SMS")
    module_onboarding_mode_status = fields.Boolean(string="Demo Mode")
    employee_creation_inform_ids = fields.Many2many('hr.job', 'employee_creation_mail_rel', string='Designation')
    checklist_inform_ids = fields.Many2many('hr.job', 'checklist_inform_mail_rel', string='Checklist Designation')
    responsible_person_id = fields.Many2one('hr.employee', string='Responsible Person')
    onboarding_cc_ids = fields.Many2many('hr.employee','employee_cc_mail_rel', string='Onboarding CC')
    onboarding_induction_check = fields.Boolean(string="Onboarding Induction Feedback Check")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        employee_creation_inform_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.employee_creation_inform_ids')
        onboarding_cc_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.onboarding_cc_ids')
        checklist_inform_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.checklist_inform_ids')
        responsible_person_id = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.responsible_person')
        lines = False
        lines1 = False
        lines0 = False
        if employee_creation_inform_ids:
            lines = [(6, 0, literal_eval(employee_creation_inform_ids))]
        if onboarding_cc_ids:
            lines0 = [(6, 0, literal_eval(onboarding_cc_ids))]
        if checklist_inform_ids:
            lines1 = [(6, 0, literal_eval(checklist_inform_ids))]
        res.update(
            module_onboarding_mail_status = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_mail_status'),
            onboarding_induction_check = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.onboarding_induction_check'),
            module_onboarding_sms_status = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_sms_status'),
            module_onboarding_mode_status = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_mode_status'),
            employee_creation_inform_ids = lines,
            onboarding_cc_ids = lines0,
            checklist_inform_ids = lines1,
            responsible_person_id = int(responsible_person_id) if responsible_person_id != 'False' else False,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.module_onboarding_mail_status or False
        field2 = self.module_onboarding_sms_status or False
        field3 = self.module_onboarding_mode_status or False
        field4 = self.onboarding_induction_check or False

        param.set_param('kw_onboarding.module_onboarding_mail_status', field1)
        param.set_param('kw_onboarding.module_onboarding_sms_status', field2)
        param.set_param('kw_onboarding.module_onboarding_mode_status', field3)
        param.set_param('kw_onboarding.onboarding_induction_check', field4)
        param.set_param('kw_employee.employee_creation_inform_ids', self.employee_creation_inform_ids.ids)
        param.set_param('kw_employee.checklist_inform_ids', self.checklist_inform_ids.ids)
        param.set_param('kw_onboarding.responsible_person', str(self.responsible_person_id.id))
        param.set_param('kw_employee.onboarding_cc_ids', self.onboarding_cc_ids.ids)
