# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError



class ButtonConfigMaster(models.Model):
    _name = 'kw_appraisal_btn_config_master'
    _description = 'IAA - Dept. Configuration'

    department_ids = fields.Many2many('hr.department', 'appraisal_btn_department_rel', 'config_id', 'dept_id', 'Department')
    user_ids = fields.Many2many('res.users', 'appraisal_btn_user_rel', 'config_id', 'user_id', 'Users Name')
    # active = fields.Boolean(string="Active")
    type = fields.Selection([('manager','Manager'),('hod','IAA'),('chro','CHRO'),('ceo','CEO')])



class mail_cc_config(models.Model):
    _name = 'mail_cc_config'
    _description = 'Mail Configuration Master'

    period_id = fields.Many2one(comodel_name='kw_assessment_period_master', string="Period")
    mail_to_appr_manager = fields.Many2many("hr.employee", "cc_mail_appraisal_manager_rel", "mail_id", "emp_id",string="Notify CC for Increment ")

    
    @api.constrains('period_id')
    def _check_period(self):
        for rec in self:
            record = self.env['mail_cc_config'].sudo().search([('period_id', '=', rec.period_id.id)]) - self
            if record:
                raise ValidationError(f"This Period is already exist!")

