# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError


class ForwardWizardEOS(models.TransientModel):
    _name = "kw_eos_forward_wizard"
    _description = "kw_eos_forward_wizard"
    _order = 'id'

    eos_id = fields.Many2one('kw_end_of_service', string="Ref")
    forward_to = fields.Many2one('hr.employee', string="User")
    remark = fields.Text('Remarks')

    def save(self):
        if self.eos_id:
            self.eos_id.write({
                'forward_by': self.env.user.employee_ids.id,
                'forward_to': self.forward_to.id,
                'state': 'forward',
                'remark': self.remark,
                'action_to_be_taken_by': self.forward_to.id, })
            # # Mail to Forwarded User
            template_obj = self.env.ref('kw_eos.eos_forward_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).send_mail(self.eos_id.id,
                                                                               notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                               force_send=False)
            self.env.user.notify_success("EOS forwarded successfully.")

        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class RemarkWizard(models.TransientModel):
    _name = "kw_eos_remark_wizard"
    _description = "kw_eos_remark_wizard"
    _order = 'id'

    eos_id = fields.Many2one('kw_end_of_service', string="Ref")
    remark = fields.Text('Remarks')

    def save(self):
        if self.env.context.get('reject'):
            self.eos_id.write({
                'prev_state': self.eos_id.state,
                'state': 'reject',
                'remark': self.remark,
                'action_to_be_taken_by': False
            })
        elif self.env.context.get('hold'):
            self.eos_id.write({
                'prev_state': self.eos_id.state,
                'state': 'hold',
                'remark': self.remark,
            })
        elif self.env.context.get('forward_ra') or self.env.context.get('ra_approve'):
            self.eos_id.write({
                'prev_state': self.eos_id.state,
                'state': 'confirm',
                'remark': self.remark,
                'action_to_be_taken_by': False,
            })
        elif self.env.context.get('unhold'):
            self.eos_id.write({
                'state': self.eos_id.prev_state,
                'remark': self.remark,
            })
        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
