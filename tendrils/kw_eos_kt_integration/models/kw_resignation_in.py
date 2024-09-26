# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date, time


class KwKt(models.Model):
    _inherit = 'kw_kt_view'

    resignation_id = fields.Many2one('kw_resignation', string="Resignation Id")

    """KT Reminder : After 2 working days of RL approval"""

    def kw_remainder_before_two_rl_pending(self):
        for rec in self:
            template_obj = self.env.ref('kw_eos_kt_integration.kt_remainder_after_two_days_of_rl_approval')
            mail = self.env['mail.template'].browse(template_obj.id).with_context().send_mail(
                rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    """KT Reminder : After 4 working days of RL approval"""

    def kw_remainder_before_four_rl_pending(self):
        for rec in self:
            template_obj = self.env.ref('kw_eos_kt_integration.kt_remainder_after_four_days_of_rl_approval')
            mail = self.env['mail.template'].browse(template_obj.id).with_context().send_mail(
                rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    """KT Reminder : After 6 working days of RL approval"""

    def kw_remainder_before_six_rl_pending(self):
        for rec in self:
            template_obj = self.env.ref('kw_eos_kt_integration.kt_remainder_after_six_days_of_rl_approval')
            mail = self.env['mail.template'].browse(template_obj.id).with_context().send_mail(
                rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    """KT Reminder : After 8 working days of RL approval"""

    def kw_remainder_before_eight_rl_pending(self):
        for rec in self:
            template_obj = self.env.ref('kw_eos_kt_integration.kt_remainder_after_eight_days_of_rl_approval')
            mail = self.env['mail.template'].browse(template_obj.id).with_context().send_mail(
                rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    """remainder mail scheduler before rl"""

    @api.model
    def kw_remainder_before_rl(self):
        kt_view_record = self.env['kw_kt_view'].sudo().search([('state', 'not in', ['Completed', 'Rejected'])])
        if kt_view_record:
            today_date = datetime.now().date().day
            for rec in kt_view_record:
                resignation_rec = self.env['kw_resignation'].sudo().search(
                    [('id', '=', rec.resignation_id.id), ('state', 'in', ['confirm', 'grant'])])
                if resignation_rec:
                    for res in resignation_rec:
                        if today_date - res.write_date.day == 2:
                            rec.kw_remainder_before_two_rl_pending()
                        elif today_date - res.write_date.day == 4:
                            rec.kw_remainder_before_four_rl_pending()
                        elif today_date - res.write_date.day == 6:
                            rec.kw_remainder_before_six_rl_pending()
                        elif today_date - res.write_date.day == 8:
                            rec.kw_remainder_before_eight_rl_pending()


class kw_resignation(models.Model):
    _inherit = "kw_resignation"

    @api.multi
    def write(self, values):
        res = super(kw_resignation, self).write(values)
        for rec in self:
            if not values.get('resignation_reject'):
                if values.get('state') == 'grant' and rec.kt_required == 'yes':
                    kt_type_rec = self.env['kw_kt_type_master'].sudo().search(
                        [('name', '=', self.offboarding_type.name)])
                    kt_res = self.env['kw_kt_view'].create({
                        'resignation_id': rec.id,
                        'applicant_id': rec.applicant_id.id,
                        'effective_form': rec.effective_form,
                        'last_working_date': rec.last_working_date,
                        'kt_type_id': kt_type_rec.id,
                        'manual': False,
                    })
        return res

    @api.multi
    def view_kt(self):
        menu_id = self.env['ir.ui.menu'].sudo().search([('name', '=', 'Knowledge Transfer')]).id
        action_id = self.env.ref("kw_kt.kt_view_action").id
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list&menu_id={menu_id}',
        }


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def write(self, values):
        res = super(HrEmployee, self).write(values)
        if 'flag' in values:
            if self.status == 'KT Inprogress' and self.kt_required == 'yes':
                kt_type_rec = self.env['kw_kt_type_master'].sudo().search([('name', '=', 'Contract Closure')])
                kt_res = self.env['kw_kt_view'].create({
                    'applicant_id': self.id,
                    'kt_type_id': kt_type_rec.id,
                    'manual': False,
                })
        return res
