# -*- coding: utf-8 -*-
from odoo import models, fields, api


class kw_kt_plan_config(models.Model):
    _name = "kw_kt_plan_config"
    _description = "KT Plan Configuration model"
    _rec_name = 'applicant_id'

    applicant_id = fields.Many2one('hr.employee', string="Applicant's Name", default=lambda self: self.env.context.get('default_applicant_id', False), store=True, readonly=True,required=True, ondelete='cascade')
    applicant_dept_id = fields.Many2one('hr.department', related="applicant_id.department_id", string="Department")
    applicant_division = fields.Many2one('hr.department', related="applicant_id.division", string="Division")
    applicant_section = fields.Many2one('hr.department', related="applicant_id.section", string="Practice")
    applicant_practise = fields.Many2one('hr.department', related="applicant_id.practise", string="Section")
    tag_kt_ids = fields.One2many('kw_kt_tag', 'kt_plan_config_id', string="Tag Project", ondelete='cascade', required=True)
    # kt_view_id = fields.Many2one(string="KT View Id", default=lambda self: self.env.context.get('default_kt_view_id', False), store=True, readonly=True,required=True, ondelete='restrict')

    company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
                                 default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        new_record = super(kw_kt_plan_config, self).create(vals)
        self.env.user.notify_success('KT plan configured successfully.')
        template_id = self.env.ref('kw_kt.kw_kt_plan_config_template')
        template_id.send_mail(new_record.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Mail sent successfully.")

        # action_id = self.env.ref('kw_kt.kt_plan_action')
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list',
        #     'target': 'self',
        # }
        return new_record
